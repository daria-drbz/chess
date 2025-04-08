from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict
import math


class Move:
    """Класс для хранения информации о ходе"""

    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], piece_moved: 'Piece',
                 piece_captured: Optional['Piece'] = None):
        self.start = start
        self.end = end
        self.piece_moved = piece_moved
        self.piece_captured = piece_captured

    def __repr__(self):
        return f"{self.piece_moved} {self.start}->{self.end}"


class Piece(ABC):
    """Абстрактный базовый класс для шахматных фигур"""

    def __init__(self, color: str, symbol: str):
        self.color = color
        self.symbol = symbol.upper() if color == 'white' else symbol.lower()
        self.has_moved = False

    def get_moves(self, board: 'Board', pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        pass

    def __str__(self):
        return self.symbol


class ChessPiece(Piece):
    """Базовый класс для шахматных фигур"""
    pass


class HexChessPiece(Piece):
    """Базовый класс для гексагональных шахматных фигур"""
    pass


class HexPawn(HexChessPiece):
    def get_moves(self, board, pos):
        x, y = pos
        moves = []
        direction = -1 if self.color == 'white' else 1

        # В гексагональных шахматах пешки ходят по-другому
        # Основное направление зависит от цвета
        if self.color == 'white':
            # Белые пешки двигаются вверх-влево и вверх-вправо
            moves_to_check = [(x + direction, y), (x + direction, y + 1)]
        else:
            # Черные пешки двигаются вниз-вправо и вниз
            moves_to_check = [(x + direction, y), (x + direction, y - 1)]

        for new_x, new_y in moves_to_check:
            if board.is_valid_hex_position((new_x, new_y)):
                if board.is_empty((new_x, new_y)):
                    moves.append((new_x, new_y))

        # Взятие в гексагональных шахматах
        if self.color == 'white':
            capture_moves = [(x - 1, y - 1), (x - 1, y + 1)]
        else:
            capture_moves = [(x + 1, y - 1), (x + 1, y + 1)]

        for new_x, new_y in capture_moves:
            if board.is_valid_hex_position((new_x, new_y)):
                if not board.is_empty((new_x, new_y)) and board.get_piece((new_x, new_y)).color != self.color:
                    moves.append((new_x, new_y))

        return moves


class HexRook(HexChessPiece):
    def get_moves(self, board, pos):
        x, y = pos
        moves = []
        # В гексагональных шахматах ладья ходит по 3 основным направлениям
        directions = [
            (1, 0),  # вниз-вправо
            (-1, 0),  # вверх-влево
            (0, 1),  # вправо
            (0, -1),  # влево
            (1, -1),  # вниз
            (-1, 1)  # вверх
        ]

        for dx, dy in directions:
            for i in range(1, 11):  # Максимальный размер доски
                new_x, new_y = x + dx * i, y + dy * i
                if not board.is_valid_hex_position((new_x, new_y)):
                    break
                if board.is_empty((new_x, new_y)):
                    moves.append((new_x, new_y))
                else:
                    if board.get_piece((new_x, new_y)).color != self.color:
                        moves.append((new_x, new_y))
                    break
        return moves


class HexBishop(HexChessPiece):
    def get_moves(self, board, pos):
        x, y = pos
        moves = []
        # В гексагональных шахматах слон ходит по 3 диагональным направлениям
        directions = [
            (1, 1),  # вниз-вправо-вверх
            (1, -1),  # вниз-влево-вверх
            (-1, 1),  # вверх-вправо-вниз
            (-1, -1),  # вверх-влево-вниз
            (0, 1),  # вправо-влево
            (0, -1)  # влево-вправо
        ]

        for dx, dy in directions:
            for i in range(1, 11):
                new_x, new_y = x + dx * i, y + dy * i
                if not board.is_valid_hex_position((new_x, new_y)):
                    break
                if board.is_empty((new_x, new_y)):
                    moves.append((new_x, new_y))
                else:
                    if board.get_piece((new_x, new_y)).color != self.color:
                        moves.append((new_x, new_y))
                    break
        return moves


class HexQueen(HexChessPiece):
    def get_moves(self, board, pos):
        # Комбинация ладьи и слона в гексагональных шахматах
        rook_moves = HexRook(self.color, 'Q').get_moves(board, pos)
        bishop_moves = HexBishop(self.color, 'Q').get_moves(board, pos)
        return rook_moves + bishop_moves


class HexKing(HexChessPiece):
    def get_moves(self, board, pos):
        x, y = pos
        moves = []
        # Король ходит на одну клетку в любом из 6 направлений
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]:
            new_x, new_y = x + dx, y + dy
            if board.is_valid_hex_position((new_x, new_y)):
                if board.is_empty((new_x, new_y)) or board.get_piece((new_x, new_y)).color != self.color:
                    moves.append((new_x, new_y))
        return moves


class HexKnight(HexChessPiece):
    def get_moves(self, board, pos):
        x, y = pos
        moves = []
        # Конь в гексагональных шахматах имеет 12 возможных ходов
        knight_moves = [
            (2, -1), (2, 1), (-2, -1), (-2, 1),
            (1, -2), (1, 2), (-1, -2), (-1, 2),
            (0, 3), (0, -3), (3, 0), (-3, 0)
        ]

        for dx, dy in knight_moves:
            new_x, new_y = x + dx, y + dy
            if board.is_valid_hex_position((new_x, new_y)):
                if board.is_empty((new_x, new_y)) or board.get_piece((new_x, new_y)).color != self.color:
                    moves.append((new_x, new_y))
        return moves


class Pawn(ChessPiece):
    def get_moves(self, board, pos):
        x, y = pos
        moves = []
        direction = -1 if self.color == 'white' else 1

        # Обычный ход
        if board.is_empty((x + direction, y)):
            moves.append((x + direction, y))
            # Первый ход на 2 клетки
            if not self.has_moved and board.is_empty((x + 2 * direction, y)):
                moves.append((x + 2 * direction, y))

        # Взятие
        for dy in [-1, 1]:
            if 0 <= y + dy < 8:
                target = (x + direction, y + dy)
                if not board.is_empty(target) and board.get_piece(target).color != self.color:
                    moves.append(target)
        return moves


class Rook(ChessPiece):
    def get_moves(self, board, pos):
        x, y = pos
        moves = []
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            for i in range(1, 8):
                new_x, new_y = x + dx * i, y + dy * i
                if 0 <= new_x < 8 and 0 <= new_y < 8:
                    if board.is_empty((new_x, new_y)):
                        moves.append((new_x, new_y))
                    else:
                        if board.get_piece((new_x, new_y)).color != self.color:
                            moves.append((new_x, new_y))
                        break
        return moves


class Knight(ChessPiece):
    def get_moves(self, board, pos):
        x, y = pos
        moves = []
        for dx, dy in [(2, 1), (2, -1), (-2, 1), (-2, -1),
                       (1, 2), (1, -2), (-1, 2), (-1, -2)]:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < 8 and 0 <= new_y < 8:
                if board.is_empty((new_x, new_y)) or board.get_piece((new_x, new_y)).color != self.color:
                    moves.append((new_x, new_y))
        return moves


class Bishop(ChessPiece):
    def get_moves(self, board, pos):
        x, y = pos
        moves = []
        for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            for i in range(1, 8):
                new_x, new_y = x + dx * i, y + dy * i
                if 0 <= new_x < 8 and 0 <= new_y < 8:
                    if board.is_empty((new_x, new_y)):
                        moves.append((new_x, new_y))
                    else:
                        if board.get_piece((new_x, new_y)).color != self.color:
                            moves.append((new_x, new_y))
                        break
        return moves


class Queen(ChessPiece):
    def get_moves(self, board, pos):
        # Комбинация ладьи и слона
        rook_moves = Rook(self.color, 'Q').get_moves(board, pos)
        bishop_moves = Bishop(self.color, 'Q').get_moves(board, pos)
        return rook_moves + bishop_moves


class King(ChessPiece):
    def get_moves(self, board, pos):
        x, y = pos
        moves = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < 8 and 0 <= new_y < 8:
                    if board.is_empty((new_x, new_y)) or board.get_piece((new_x, new_y)).color != self.color:
                        moves.append((new_x, new_y))
        return moves


class Checker(Piece):
    """Класс для шашек"""

    def __init__(self, color: str):
        super().__init__(color, '●' if color == 'white' else '○')
        self.is_king = False  # Флаг для дамки

    def get_moves(self, board, pos):
        x, y = pos
        moves = []
        capture_moves = []
        direction = 1 if self.color == 'black' else -1

        # Обычные ходы для простой шашки
        if not self.is_king:
            for dy in (-1, 1):
                new_x, new_y = x + direction, y + dy
                if 0 <= new_x < 8 and 0 <= new_y < 8:
                    if board.is_empty((new_x, new_y)):
                        moves.append((new_x, new_y))
                    elif board.get_piece((new_x, new_y)).color != self.color:
                        # Проверка возможности взятия
                        jump_x, jump_y = new_x + direction, new_y + dy
                        if 0 <= jump_x < 8 and 0 <= jump_y < 8 and board.is_empty((jump_x, jump_y)):
                            capture_moves.append((jump_x, jump_y))
        else:
            # Ходы для дамки (по всем диагоналям)
            for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                for i in range(1, 8):
                    new_x, new_y = x + dx * i, y + dy * i
                    if not (0 <= new_x < 8 and 0 <= new_y < 8):
                        break
                    if board.is_empty((new_x, new_y)):
                        moves.append((new_x, new_y))
                    else:
                        if board.get_piece((new_x, new_y)).color != self.color:
                            jump_x, jump_y = new_x + dx, new_y + dy
                            if 0 <= jump_x < 8 and 0 <= jump_y < 8 and board.is_empty((jump_x, jump_y)):
                                capture_moves.append((jump_x, jump_y))
                        break

        # Приоритет у ходов со взятием
        return capture_moves if capture_moves else moves


class Board:
    """Класс игровой доски"""

    def __init__(self, game_type='chess'):
        self.grid = [[None for _ in range(11)] for _ in range(11)]  # Достаточно для гексагональной доски
        self.move_history = []
        self.game_type = game_type
        self.setup_board()

    def setup_board(self):
        """Настройка доски в зависимости от типа игры"""
        if self.game_type == 'chess':
            self._setup_chess()
        elif self.game_type == 'checkers':
            self._setup_checkers()
        elif self.game_type == 'hex_chess':
            self._setup_hex_chess()

    def _setup_chess(self):
        """Стандартная расстановка шахмат"""
        # Черные фигуры
        self.grid[0] = [
                           Rook('black', 'R'), Knight('black', 'N'), Bishop('black', 'B'), Queen('black', 'Q'),
                           King('black', 'K'), Bishop('black', 'B'), Knight('black', 'N'), Rook('black', 'R')
                       ] + [None] * 3
        self.grid[1] = [Pawn('black', 'P') for _ in range(8)] + [None] * 3

        # Белые фигуры
        self.grid[6] = [Pawn('white', 'P') for _ in range(8)] + [None] * 3
        self.grid[7] = [
                           Rook('white', 'R'), Knight('white', 'N'), Bishop('white', 'B'), Queen('white', 'Q'),
                           King('white', 'K'), Bishop('white', 'B'), Knight('white', 'N'), Rook('white', 'R')
                       ] + [None] * 3

        # Остальные строки (для совместимости)
        for i in range(2, 6):
            self.grid[i] = [None] * 11
        for i in range(8, 11):
            self.grid[i] = [None] * 11

    def _setup_checkers(self):
        """Расстановка шашек (только на черных клетках)"""
        for row in range(8):
            for col in range(8):
                if (row + col) % 2 == 1:  # Только черные клетки
                    if row < 3:
                        self.grid[row][col] = Checker('black')
                    elif row > 4:
                        self.grid[row][col] = Checker('white')

        # Остальные строки (для совместимости)
        for i in range(8, 11):
            self.grid[i] = [None] * 11

    def _setup_hex_chess(self):
        """Расстановка для гексагональных шахмат Глинского"""

        def _setup_hex_chess(self):
            """Расстановка для гексагональных шахмат Глинского"""
            # Очищаем доску
            self.grid = [[None for _ in range(11)] for _ in range(11)]

        # Черные фигуры (нижняя часть доски)
        self.grid[10][5] = HexRook('black', 'R')
        self.grid[10][4] = HexKnight('black', 'N')
        self.grid[10][3] = HexBishop('black', 'B')
        self.grid[9][4] = HexQueen('black', 'Q')
        self.grid[9][5] = HexKing('black', 'K')
        self.grid[10][6] = HexBishop('black', 'B')
        self.grid[10][7] = HexKnight('black', 'N')
        self.grid[10][8] = HexRook('black', 'R')

        # Черные пешки
        for col in [3, 4, 5, 6, 7, 8]:
            self.grid[9][col] = HexPawn('black', 'P')

        # Белые фигуры (верхняя часть доски)
        self.grid[0][5] = HexRook('white', 'R')
        self.grid[0][6] = HexKnight('white', 'N')
        self.grid[0][7] = HexBishop('white', 'B')
        self.grid[1][5] = HexQueen('white', 'Q')
        self.grid[1][4] = HexKing('white', 'K')
        self.grid[0][3] = HexBishop('white', 'B')
        self.grid[0][2] = HexKnight('white', 'N')
        self.grid[0][1] = HexRook('white', 'R')

        # Белые пешки
        for col in [1, 2, 3, 4, 5, 6]:
            self.grid[1][col] = HexPawn('white', 'P')

    def is_valid_hex_position(self, pos: Tuple[int, int]) -> bool:
        """Проверка, является ли позиция допустимой на гексагональной доске"""
        x, y = pos
        if x < 0 or x > 10 or y < 0 or y > 10:
            return False

        # Проверка границ шестиугольной доски
        if x <= 5:
            if y < 5 - x or y > 5 + x:
                return False
        else:
            if y < x - 5 or y > 15 - x:
                return False
        return True

    def move_piece(self, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        """Выполнить ход с проверкой правил"""
        piece = self.get_piece(start)
        if not piece:
            return False

        # Проверка допустимости хода для текущего типа игры
        if self.game_type == 'hex_chess':
            if not self.is_valid_hex_position(start) or not self.is_valid_hex_position(end):
                return False
        else:
            if not (0 <= start[0] < 8 and 0 <= start[1] < 8 and 0 <= end[0] < 8 and 0 <= end[1] < 8):
                return False

        if end not in piece.get_moves(self, start):
            return False

        move = Move(start, end, piece, self.get_piece(end))
        self.grid[end[0]][end[1]] = piece
        self.grid[start[0]][start[1]] = None
        piece.has_moved = True

        # Проверка превращения в дамку (для шашек)
        if isinstance(piece, Checker) and not piece.is_king:
            if (piece.color == 'black' and end[0] == 7) or (piece.color == 'white' and end[0] == 0):
                piece.is_king = True
                piece.symbol = piece.symbol.upper()  # Обозначаем дамку

        # Проверка превращения пешки в гексагональных шахматах
        if self.game_type == 'hex_chess' and isinstance(piece, HexPawn):
            if (piece.color == 'white' and end[0] == 10) or (piece.color == 'black' and end[0] == 0):
                # Превращение в ферзя (упрощенный вариант)
                self.grid[end[0]][end[1]] = HexQueen(piece.color, 'Q')

        self.move_history.append(move)
        return True

    def undo_move(self) -> bool:
        """Отменить последний ход"""
        if not self.move_history:
            return False

        move = self.move_history.pop()
        self.grid[move.start[0]][move.start[1]] = move.piece_moved
        self.grid[move.end[0]][move.end[1]] = move.piece_captured
        move.piece_moved.has_moved = len(self.move_history) > 0
        return True

    def get_piece(self, pos: Tuple[int, int]) -> Optional[Piece]:
        """Получить фигуру по позиции"""
        return self.grid[pos[0]][pos[1]]

    def is_empty(self, pos: Tuple[int, int]) -> bool:
        """Проверить, пуста ли клетка"""
        return self.get_piece(pos) is None

    def display(self):
        """Отобразить доску в консоли"""
        if self.game_type == 'hex_chess':
            self._display_hex_board()
        elif self.game_type == 'checkers':
            self._display_checkers_board()
        else:
            self._display_chess_board()

    def _display_chess_board(self):
        """Отображение классической шахматной доски"""
        print("  a b c d e f g h")
        print(" +-----------------+")
        for i, row in enumerate(self.grid[:8]):
            print(f"{8 - i}|{' '.join(p and str(p) or '.' for p in row[:8])}|{8 - i}")
        print(" +-----------------+")
        print("  a b c d e f g h")

    def _display_checkers_board(self):
        """Отображение доски для шашек"""
        print("  a b c d e f g h")
        print(" +-----------------+")
        for i, row in enumerate(self.grid[:8]):
            display_row = []
            for j, cell in enumerate(row[:8]):
                if (i + j) % 2 == 0:  # Белые клетки
                    display_row.append('.')
                else:
                    display_row.append(str(cell) if cell else ' ')
            print(f"{8 - i}|{' '.join(display_row)}|{8 - i}")
        print(" +-----------------+")
        print("  a b c d e f g h")

    def _setup_hex_chess(self):
        """Расстановка фигур для гексагональных шахмат Глинского"""
        self.grid = [[None for _ in range(11)] for _ in range(11)]

        # Черные фигуры (нижняя часть доски)
        # Ладьи (2)
        self.grid[10][1] = HexRook('black', 'R')
        self.grid[10][9] = HexRook('black', 'R')
        # Кони (2)
        self.grid[10][2] = HexKnight('black', 'N')
        self.grid[10][8] = HexKnight('black', 'N')
        # Слоны (3)
        self.grid[10][0] = HexBishop('black', 'B')
        self.grid[10][5] = HexBishop('black', 'B')
        self.grid[10][10] = HexBishop('black', 'B')
        # Ферзь
        self.grid[9][4] = HexQueen('black', 'Q')
        # Король
        self.grid[9][5] = HexKing('black', 'K')

        # Черные пешки (9)
        for col in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
            self.grid[9][col] = HexPawn('black', 'P')

        # Белые фигуры (верхняя часть доски)
        # Ладьи (2)
        self.grid[0][1] = HexRook('white', 'r')
        self.grid[0][9] = HexRook('white', 'r')
        # Кони (2)
        self.grid[0][2] = HexKnight('white', 'n')
        self.grid[0][8] = HexKnight('white', 'n')
        # Слоны (3)
        self.grid[0][0] = HexBishop('white', 'b')
        self.grid[0][5] = HexBishop('white', 'b')
        self.grid[0][10] = HexBishop('white', 'b')
        # Ферзь
        self.grid[1][5] = HexQueen('white', 'q')
        # Король
        self.grid[1][4] = HexKing('white', 'k')

        # Белые пешки (9)
        for col in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
            self.grid[1][col] = HexPawn('white', 'p')

    def _display_hex_board(self):
        """Отображение гексагональной доски"""
        letters = "   a b c d e f g h i j k"
        print(letters)
        print(" +-----------------------")

        for i in range(11):
            row_num = 10 - i
            row_display = []

            # Определяем активные столбцы для каждой строки
            if row_num in [10, 0]:
                active_cols = range(0, 11)  # Все столбцы для крайних рядов
            elif row_num in [9, 1]:
                active_cols = range(1, 10)  # 9 пешек
            else:
                active_cols = range(2, 9)  # Центральные поля

            for j in range(11):
                if j in active_cols:
                    piece = self.grid[i][j]
                    row_display.append(str(piece) if piece else '.')  # Закрывающая скобка добавлена
                else:
                    row_display.append(' ')

            print(f"{row_num:2}| {' '.join(row_display)} |{row_num:2}")

        print(" +-----------------------")
        print(letters)

class ChessGame:
    """Класс управления игрой"""

    def __init__(self, game_type='chess'):
        self.board = Board(game_type)
        self.current_player = 'white'
        self.game_type = game_type
        self.move_count = 0

    def play(self):
        """Основной игровой цикл"""
        game_names = {
            'chess': "Шахматы",
            'checkers': "Шашки",
            'hex_chess': "Гексагональные шахматы (Глинского)"
        }
        print(f"=== {game_names.get(self.game_type, 'Игра')} ===")
        print("Формат хода: 'e2 e4' (откуда куда)")
        print("Команды: 'отмена' - отменить ход, 'выход' - завершить игру")

        while True:
            self.board.display()
            print(f"Ход {'белых' if self.current_player == 'white' else 'черных'}")
            print(f"Ход №: {self.move_count + 1}")

            cmd = input("> ").strip().lower()

            if cmd == 'выход':
                print("Игра завершена.")
                break
            elif cmd == 'отмена':
                if self.board.undo_move():
                    self._switch_player()
                    self.move_count -= 1
                    print("Последний ход отменен")
                else:
                    print("Нельзя отменить ход")
                continue

            try:
                parts = cmd.split()
                if len(parts) != 2:
                    raise ValueError("Нужно ввести две позиции")

                start = self._parse_pos(parts[0])
                end = self._parse_pos(parts[1])

                if self.board.move_piece(start, end):
                    print(f"Ход {parts[0]}→{parts[1]} выполнен")
                    self._switch_player()
                    self.move_count += 1
                else:
                    print("Недопустимый ход! Попробуйте еще.")
            except Exception as e:
                print(f"Ошибка: {e}. Введите ход в формате 'e2 e4'")

    def _parse_pos(self, pos_str: str) -> Tuple[int, int]:
        """Преобразовать строку (например 'e2') в координаты доски"""
        if len(pos_str) != 2:
            raise ValueError("Позиция должна состоять из 2 символов")
        col, row = pos_str[0], pos_str[1]

        if self.game_type == 'hex_chess':
            # Для гексагональных шахмат используем буквы a-k и цифры 0-10
            if col < 'a' or col > 'k':
                raise ValueError("Буква должна быть от a до k")
            if not row.isdigit() or int(row) < 0 or int(row) > 10:
                raise ValueError("Цифра должна быть от 0 до 10")
            return (10 - int(row), ord(col) - ord('a'))
        else:
            # Для классических шахмат и шашек
            if col < 'a' or col > 'h':
                raise ValueError("Буква должна быть от a до h")
            if not row.isdigit() or int(row) < 1 or int(row) > 8:
                raise ValueError("Цифра должна быть от 1 до 8")
            return (8 - int(row), ord(col) - ord('a'))

    def _switch_player(self):
        """Сменить текущего игрока"""
        self.current_player = 'black' if self.current_player == 'white' else 'white'


if __name__ == "__main__":
    print("Выберите игру:")
    print("1 - Классические шахматы")
    print("2 - Шашки")
    print("3 - Гексагональные шахматы Глинского")

    while True:
        choice = input("> ").strip()
        if choice in ('1', '2', '3'):
            break
        print("Пожалуйста, введите 1, 2 или 3")

    game_types = {'1': 'chess', '2': 'checkers', '3': 'hex_chess'}
    game = ChessGame(game_types[choice])
    game.play()