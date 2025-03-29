from Piece import Piece
import Game_settings

class Pawn(Piece):
    def __init__(self):
        super().__init__(image_path_white="Images/white_pawn.png",
                         image_path_black="Images/black_pawn.png",
                         starting_positions_white=["A2","B2","C2","D2","E2","F2","G2","H2"],
                         starting_positions_black=["A7","B7","C7","D7","E7","F7","G7","H7"])

        self.just_moved_two_squares = False
        self.first_location=None
        self.en_passant_done=False
        self.en_passant_taken_piece=None
        self.en_passant_move_location=None
        self.piece_type="pawn"

    def get_valid_moves(self):
        from King import King

        x, y = self.current_Location
        valid_moves = []

        #  Dictionary for quick lookup
        occupied_positions = {piece.current_Location: piece for piece in Piece.current_pieces_list}

        # Determine direction based on color
        direction = -75 if self.color == "white" and Game_settings.PLAYER_COLOR=="white" or self.color == "black" and Game_settings.PLAYER_COLOR=="black"else 75

        # Forward move (one square)
        forward_one = (x, y + direction)
        if forward_one not in occupied_positions and 0 <= forward_one[1] < 600:
            valid_moves.append(forward_one)

            # Forward move (two squares, only if in starting position)
            starting_row = 450 if self.color == "white" and Game_settings.PLAYER_COLOR=="white" or self.color == "black" and Game_settings.PLAYER_COLOR=="black" else 75  # 2nd row for white, 7th row for black
            forward_two = (x, y + 2 * direction)
            if y == starting_row and forward_two not in occupied_positions:
                valid_moves.append(forward_two)

        # Capture moves (diagonal left and right)
        for dx in [-75, 75]:
            capture_pos = (x + dx, y + direction)
            if capture_pos in occupied_positions:
                piece = occupied_positions[capture_pos]
                if piece.color == self.color:
                    piece.defended = True
                    opponent_king = King.white_king_instance if self.color == "black" else King.black_king_instance
                    opponent_king.valid_moves = [move for move in opponent_king.valid_moves if
                                                 move != piece.current_Location]
                if piece.color != self.color:  # Can only capture opposite color
                    valid_moves.append(capture_pos)

            en_passant_pos = (x + dx, y)  # Square where enemy pawn just moved two squares
            if en_passant_pos in {piece.current_Location for piece in Piece.current_pieces_list}:
                piece = next(piece for piece in Piece.current_pieces_list if piece.current_Location == en_passant_pos)
                if isinstance(piece, Pawn) and piece.color != self.color and piece.just_moved_two_squares:
                    self.en_passant_taken_piece=piece
                    self.en_passant_done=True
                    self.en_passant_move_location=(x + dx, y + direction)
                    valid_moves.append((x + dx, y + direction))  # Move to capture en passant
        return valid_moves

    def get_pawn_attack_positions(self):
        # Add diagonal pawn attack positions
        x, y = self.current_Location
        attack_positions = []

        if self.color == "white":
            attack_positions.append((x - 75, y - 75))  # Left diagonal
            attack_positions.append((x + 75, y - 75))  # Right diagonal
        else:
            attack_positions.append((x - 75, y + 75))  # Left diagonal
            attack_positions.append((x + 75, y + 75))  # Right diagonal

        return attack_positions