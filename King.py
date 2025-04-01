import Pawn
from Piece import Piece



class King(Piece):
    white_king_instance = None
    black_king_instance = None

    def __init__(self):
        super().__init__(image_path_white="Images/white_king.png",
                         image_path_black="Images/black_king.png",
                         starting_positions_white=["E1"],
                         starting_positions_black=["E8"])
        self.first_location=None
        self.threatened=False
        self.has_moved = False
        self.original_white = self.image_white.copy()
        self.original_black = self.image_black.copy()
        self.piece_type="king"

    def get_valid_moves(self):

        x, y = self.current_Location
        valid_moves = []

        # Dictionary for quick lookup
        occupied_positions = {piece.current_Location: piece for piece in Piece.current_pieces_list}

        # (one square in all directions)
        directions = [
            (75, 0), (-75, 0), (0, 75), (0, -75),  # Horizontal & Vertical
            (75, 75), (-75, 75), (75, -75), (-75, -75)  # Diagonal
        ]

        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy

            # Check if in board boundaries
            if 0 <= new_x < 600 and 0 <= new_y < 600:
                if (new_x, new_y) not in occupied_positions:
                    valid_moves.append((new_x, new_y))  # Empty square
                else:
                    piece = occupied_positions[(new_x, new_y)]
                    if piece.color == self.color:
                        piece.defended = True
                    if piece.color != self.color:
                        valid_moves.append((new_x, new_y))  # Capture opponent's piece

        valid_moves = [move for move in valid_moves if not self.is_square_attacked(move)]

        if not self.has_moved:
            valid_moves.extend(self.get_castling_moves())


        # Kings can not come closer

        enemy_king = King.white_king_instance if self.color == "black" else King.black_king_instance
        enemy_king_pos = enemy_king.current_Location

        # Get all adjacent squares of the enemy king
        adjacent_squares = [
            (enemy_king_pos[0] + dx, enemy_king_pos[1] + dy)
            for dx in [-75, 0, 75]  # Change for your board square size
            for dy in [-75, 0, 75]
            if (dx, dy) != (0, 0)  # Exclude enemy king's current position
        ]

        # Remove squares that are adjacent to the enemy king
        valid_moves = [move for move in valid_moves if move not in adjacent_squares]

        # Remove defended pieces locations
        for piece in Piece.current_pieces_list:
            for move in valid_moves:
                if piece.current_Location==move and piece.defended:
                    valid_moves.remove(piece.current_Location)



        self.valid_moves=valid_moves
        return valid_moves

    def is_square_attacked(self, position):

        for piece in Piece.current_pieces_list:
            if piece.color != self.color and not isinstance(piece, King):  # Ignore enemy kings

                if isinstance(piece, Pawn.Pawn):
                    attack_positions = piece.get_pawn_attack_positions()  # Get diagonal attack squares
                    if position in attack_positions:
                        return True

                elif position in piece.get_valid_moves():
                    return True

        return False

    def get_castling_moves(self):
        from Rook import Rook
        castling_moves = []
        if self.has_moved or self.threatened:  # King must not have moved or be in check
            return castling_moves

        # Convert king's pixel position to board index
        king_col = self.current_Location[0] // 75
        king_row = self.current_Location[1] // 75

        for piece in Piece.current_pieces_list:
            if isinstance(piece, Rook) and piece.color == self.color and not piece.has_moved:
                rook_col = piece.current_Location[0] // 75
                rook_row = piece.current_Location[1] // 75

                if king_row == rook_row and self.is_path_clear(king_col, rook_col, king_row):
                    if rook_col > king_col:  # Kingside castling
                        castling_moves.append(((king_col + 2) * 75, king_row * 75))
                        piece.castling_short=True
                    else:  # Queenside castling
                        castling_moves.append(((king_col - 2) * 75, king_row * 75))
                        piece.castling_long=True

        return castling_moves

    def is_path_clear(self, king_col, rook_col, row):
        min_x = min(king_col, rook_col)
        max_x = max(king_col, rook_col)

        for x in range(min_x + 1, max_x):
            for piece in Piece.current_pieces_list:
                piece_col = piece.current_Location[0] // 75
                piece_row = piece.current_Location[1] // 75
                if (piece_col, piece_row) == (x, row):
                    return False  # Path is blocked

        # Ensure the king does not pass through an attacked square
        for x in range(king_col, rook_col, 1 if rook_col > king_col else -1):
            if any(piece.color != self.color and  not isinstance(piece, King) and (x * 75, row * 75) in piece.get_valid_moves() for piece in Piece.current_pieces_list):
                return False  # The king would pass through check

        return True

    def is_in_check(self,piece_list=None):
        if piece_list is None:
            piece_list=Piece.current_pieces_list

        for piece in piece_list:

            if piece.color != self.color:  # ✅ Only check enemy pieces
                for piece1 in piece_list:
                    piece1.get_valid_moves()
                #print(f"king flee location {self.valid_moves}")
                if self.current_Location in piece.get_valid_moves():
                   # print(piece.current_Location)
                   # print(piece)
                   # print(piece.defended)
                    print(self.get_valid_moves())
                   # print(self.threatened)
                    return True  # ✅ The king is in check
        return False

    @staticmethod
    def is_checkmate(king):
        piece_removed=False

        if not king.threatened:
            return False

        temp_piece_list=Piece.current_pieces_list.copy()
        for piece in temp_piece_list.copy():
            if piece.color == king.color:
                for piece1 in temp_piece_list:
                    piece1.get_valid_moves()
                if isinstance(piece,King):
                    valid_moves=piece.valid_moves
                else:
                    valid_moves = piece.get_valid_moves()

                for move in valid_moves:
                    #  Simulate the move
                    original_pos = piece.current_Location
                    piece.current_Location = move

                    for piece1 in temp_piece_list.copy():
                        if piece1!=piece:
                            if piece1.current_Location==piece.current_Location:
                                temp_piece_list.remove(piece1)
                                piece_removed=True
                                break


                    #  Check if the king  under attack
                    king_still_in_check = king.is_in_check(piece_list=temp_piece_list)

                    #  Undo the move
                    if piece_removed:
                       temp_piece_list.append(piece1)
                    piece.current_Location = original_pos
                    if not king_still_in_check:
                       # print(f"No check after moving this piece{piece},location{piece.current_Location},valid moves={piece.valid_moves}")
                        return False  # The king can escape, so no checkmate

                    piece_removed=False
        return True  # If no valid moves, it's checkmate