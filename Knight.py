from Piece import Piece

class Knight(Piece):
    def __init__(self):
        super().__init__(image_path_white="Images/white_horse.png",
                         image_path_black="Images/black_horse.png",
                         starting_positions_white=["B1", "G1"],
                         starting_positions_black=["G8", "B8"])
        self.piece_type="knight"

    def get_valid_moves(self):
        from King import King
        x, y = self.current_Location
        valid_moves = []

        # Dictionary for quick lookup
        occupied_positions = {piece.current_Location: piece for piece in Piece.current_pieces_list}

        # (L-shape)
        moves = [
            (x + 150, y + 75), (x + 150, y - 75),
            (x - 150, y + 75), (x - 150, y - 75),
            (x + 75, y + 150), (x + 75, y - 150),
            (x - 75, y + 150), (x - 75, y - 150)
        ]

        for new_x, new_y in moves:
            if 0 <= new_x < 600 and 0 <= new_y < 600:
                if (new_x, new_y) not in occupied_positions:  # Empty square
                    valid_moves.append((new_x, new_y))
                else:
                    piece = occupied_positions[(new_x, new_y)]
                    if piece.color == self.color:
                        piece.defended = True
                        opponent_king = King.white_king_instance if self.color == "black" else King.black_king_instance
                        opponent_king.valid_moves = [move for move in opponent_king.valid_moves if
                                                     move != piece.current_Location]
                    if piece.color != self.color:  # Capture opponent's piece
                        valid_moves.append((new_x, new_y))

        return valid_moves