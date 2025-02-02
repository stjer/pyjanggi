from __future__ import annotations
import numpy as np
from typing import List, Optional

from ..constants import MIN_ROW, MAX_ROW, MIN_COL, MAX_COL, NUM_ROWS, NUM_COLS
from .piece import Piece, PieceType
from .camp import Camp
from .formation import Formation
from .location import Location

class Board:
    """
    Simple board class used for the game of Janggi. Contains and handles a single 
    10x9 two-dimensional list that contains either a Piece object or None.
    """

    def __init__(self, cho_formation: Formation, han_formation: Formation, bottom_camp: Camp):
        self.cho_formation = cho_formation
        self.han_formation = han_formation
        self.bottom_camp = bottom_camp
        self.__board = np.full((NUM_ROWS, NUM_COLS), None)

    def __str__(self) -> str:
        """Generate colored and structured string representation of the board."""
        print_str = ""
        for row in range(-1, MAX_ROW+1):
            for col in range(-1, MAX_COL+1):
                if row == -1 and col >= 0:
                    print_str += " " + str(col)
                elif row >= 0 and col == -1:
                    print_str += " " + str(row % 10)
                elif row >= 0 and col >= 0:
                    if self.__board[row][col]:
                        print_str += str(self.__board[row][col])
                    else:
                        print_str += "  "
                else:
                    print_str += " "
                print_str += " "
            print_str += "\n"
        return print_str

    @classmethod
    def full_board_from_formations(cls, cho_formation: Formation, han_formation: Formation, player: Camp) -> Board:
        """
        Return Board class instance that represents a full board.

        Args:
            cho_formation (Formation): Formation of Camp Cho.
            han_formation (Formation): Formation of Camp Han.
            player (Camp): Camp that the player is playing. This is used to assign that camp as the bottom camp.

        Returns:
            Board: Full Board class.
        """
        board = cls(cho_formation, han_formation, player)
        cho_half_board = Board._generate_half_board(cho_formation)
        han_half_board = Board._generate_half_board(han_formation)
        cho_half_board.mark_camp(Camp.CHO)
        han_half_board.mark_camp(Camp.HAN)
        if player == Camp.CHO:
            han_half_board.flip()
        else:
            cho_half_board.flip()
        board.merge(cho_half_board)
        board.merge(han_half_board)

        return board

    @classmethod
    def board_from_FEN(cls, cho_formation: Formation, han_formation: Formation, fen: str, player: Camp) -> Board:
        """
        Create a board from a Forsyth-Edwards Notation (FEN) string.
        
        Args:
            cho_formation (Formation): Formation of Camp Cho.
            han_formation (Formation): Formation of Camp Han.
            fen (str): FEN string representing board state.
            player (Camp): Camp that the player is playing.
        
        Returns:
            Board: Board initialized with pieces according to FEN.
        """
        # Create initial board using existing method
        board = cls.full_board_from_formations(cho_formation, han_formation, player)
        for i in range(10):
            for i2 in range(9):
                board.__board[i][i2]=None
        # Parse FEN string
        parts = fen.split()
        rows = parts[0].split('/')
        
        # Mapping for piece type conversion
        piece_map = {
            'k': PieceType.GENERAL,
            'a': PieceType.GUARD,
            'e': PieceType.ELEPHANT,
            'h': PieceType.HORSE,
            'c': PieceType.CANNON,
            'r': PieceType.CHARIOT,
            'p': PieceType.SOLDIER
        }
        
        # Place pieces on board
        for row in range(NUM_ROWS):
            col = 0
            for char in rows[row]:
                if char.isdigit():
                    # Skip empty squares
                    col += int(char)
                else:
                    # Determine piece camp and type
                    camp = Camp.CHO if char.isupper() else Camp.HAN
                    piece_type = piece_map[char.lower()]
                    
                    # Create and place piece
                    piece = Piece(piece_type, camp)
                    board.__board[row][col] = piece
                    col += 1
        
        return board

    
    def copy(self) -> Board:
        """
        Return a copied Board class.

        Returns:
            Board: Copied version of the board.
        """
        copied_board = Board(self.cho_formation,
                             self.han_formation, self.bottom_camp)
        copied_board.__board = self.__board.copy()
        return copied_board

    def put(self, row: int, col: int, piece: Piece):
        """
        Put piece into board at the given (row,col) location.
        Used row and col as inputs instead of Location to make it easier to generate
        initial boards in formation.py.

        Args:
            row (int): Row that the given piece that will placed on.
            col (int): Column that the given piece that will be placed on.
            piece (Piece): Piece that will be placed on the board.
        """
        self.__board[row][col] = piece

    def merge(self, board: Board):
        """
        Merge the given board into self.__board by overwriting.

        Args:
            board (Board): Input board that will be merged into self.__board.
        """
        for row in range(MIN_ROW, MAX_ROW+1):
            for col in range(MIN_COL, MAX_COL+1):
                if board.get(row, col):
                    self.__board[row][col] = board.get(row, col)

    def get(self, row: int, col: int) -> Piece:
        """
        Return the piece that is located at the given location of the board.

        Args:
            row (int): Row of piece.
            col (int): Column of piece.

        Returns:
            Piece: Piece located at (row,col) on the board. Can be None.
        """
        return self.__board[row][col]

    def remove(self, row: int, col: int):
        """
        Remove piece at the given location of the board.

        Args:
            row (int): Row of the piece to be removed.
            col (int): Column of the piece to be removed.
        """
        self.__board[row][col] = None

    def move(self, origin: Location, dest: Location) -> Optional[Piece]:
        """
        Move piece from origin to destination and return the piece that was
        originally placed at the given dest.

        Args:
            origin (Location): Original location of the piece being played.
            dest (Location): Destination of the piece being played.
        """
        assert self.get(origin.row, origin.col) is not None
        piece_to_remove = self.get(dest.row, dest.col)
        piece = self.get(origin.row, origin.col)
        self.put(dest.row, dest.col, piece)
        self.remove(origin.row, origin.col)
        return piece_to_remove

    def flip(self):
        """Rotate the board 180 degrees and update self.__board."""
        self.__board = np.flip(self.__board)

    def mark_camp(self, camp: Camp):
        """
        Mark all pieces on the board with the given camp (CHO or HAN).
        Used to mark half-boards when setting up initial boards.

        Args:
            camp (Camp): Camp enum to mark pieces with.
        """
        for row in range(MIN_ROW, MAX_ROW+1):
            for col in range(MIN_COL, MAX_COL+1):
                if self.__board[row][col]:
                    self.__board[row][col].camp = camp

    def get_score(self, camp: Camp) -> int:
        """
        Return score for the player who's playing the given camp.

        Args:
            camp (Camp): Camp of the player whose score will be calculated.

        Returns:
            int: Score of the player who's playing the given camp.
        """
        score = 0
        for row in range(MIN_ROW, MAX_ROW+1):
            for col in range(MIN_COL, MAX_COL+1):
                if self.__board[row][col] and self.__board[row][col].camp == camp:
                    score += self.__board[row][col].value
        return score

    def get_piece_locations(self) -> List[Location]:
        """
        Get locations of all pieces on the board.

        Returns:
            List[Location]: List of all locations of the pieces on the board.
        """
        piece_locations = []
        for row in range(MIN_ROW, MAX_ROW+1):
            for col in range(MIN_COL, MAX_COL+1):
                if self.__board[row][col]:
                    piece_locations.append(Location(row, col))
        return piece_locations

    def get_king_location(self, camp: Camp) -> List[Location]:
        """
        Get locations of camp's kings on the board.

        Returns:
            List[Location]: List of all locations of the pieces on the board.
        """
        king_location = []
        for row in range(MIN_ROW, MAX_ROW+1):
            for col in range(MIN_COL, MAX_COL+1):
                
                if self.__board[row][col] and self.__board[row][col].camp == camp and (set('楚漢') & set(str(self.get(row,col)))):
                    king_location.append(Location(row, col))
        return king_location

    def get_piece_locations_for_camp(self, camp: Camp) -> List[Location]:
        """
        Get locations of all pieces with the given camp.

        Args:
            camp (Camp): Camp of the pieces to fetch.

        Returns:
            List[Location]: List of all locations of the pieces with the given camp.
        """
        piece_locations = []
        for row in range(MIN_ROW, MAX_ROW+1):
            for col in range(MIN_COL, MAX_COL+1):
                if self.__board[row][col] and self.__board[row][col].camp == camp:
                    piece_locations.append(Location(row, col))
        return piece_locations

    def is_check(self, camp: Camp) -> List[Location]:

        enemy_locations = []
        king_location = []
        for row in range(MIN_ROW, MAX_ROW+1):
            for col in range(MIN_COL, MAX_COL+1):
                if self.__board[row][col] :
                    if self.__board[row][col].camp != camp:
                        enemy_locations.append(Location(row, col))
                    elif set('楚漢') & set(str(self.get(row, col))):
                        king_location = Location(row, col)
        return king_location, enemy_locations            
        
    @classmethod
    def _generate_half_board(cls, formation: Formation) -> Board:
        """
        Generate half-board that only contains pieces for a single side.

        Args:
            formation (Formation): Formation of the half board.

        Returns:
            Board: Half-board that contains pieces for only one camp.
        """
        board = cls(Formation.UNDECIDED, Formation.UNDECIDED, Camp.UNDECIDED)
        board.put(6, 0, Piece(PieceType.SOLDIER))
        board.put(6, 2, Piece(PieceType.SOLDIER))
        board.put(6, 4, Piece(PieceType.SOLDIER))
        board.put(6, 6, Piece(PieceType.SOLDIER))
        board.put(6, 8, Piece(PieceType.SOLDIER))

        board.put(7, 1, Piece(PieceType.CANNON))
        board.put(7, 7, Piece(PieceType.CANNON))

        board.put(8, 4, Piece(PieceType.GENERAL))

        board.put(9, 3, Piece(PieceType.GUARD))
        board.put(9, 5, Piece(PieceType.GUARD))

        board.put(9, 0, Piece(PieceType.CHARIOT))
        board.put(9, 8, Piece(PieceType.CHARIOT))

        if formation == Formation.OUTER_ELEPHANT:
            board.put(9, 1, Piece(PieceType.ELEPHANT))
            board.put(9, 2, Piece(PieceType.HORSE))
            board.put(9, 6, Piece(PieceType.HORSE))
            board.put(9, 7, Piece(PieceType.ELEPHANT))

        elif formation == Formation.LEFT_ELEPHANT:
            board.put(9, 1, Piece(PieceType.ELEPHANT))
            board.put(9, 2, Piece(PieceType.HORSE))
            board.put(9, 6, Piece(PieceType.ELEPHANT))
            board.put(9, 7, Piece(PieceType.HORSE))

        elif formation == Formation.RIGHT_ELEPHANT:
            board.put(9, 1, Piece(PieceType.HORSE))
            board.put(9, 2, Piece(PieceType.ELEPHANT))
            board.put(9, 6, Piece(PieceType.HORSE))
            board.put(9, 7, Piece(PieceType.ELEPHANT))

        elif formation == Formation.INNER_ELEPHANT:
            board.put(9, 1, Piece(PieceType.HORSE))
            board.put(9, 2, Piece(PieceType.ELEPHANT))
            board.put(9, 6, Piece(PieceType.ELEPHANT))
            board.put(9, 7, Piece(PieceType.HORSE))
        return board
