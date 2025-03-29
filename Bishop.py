from Piece import Piece

class Bishop(Piece):
    def __init__(self):
        super().__init__(image_path_white="Images/white_bishop.png",
                         image_path_black="Images/black_bishop.png",
                         starting_positions_white=["C1", "F1"],
                         starting_positions_black=["C8", "F8"])
        self.piece_type="bishop"

    def get_valid_moves(self):
        from King import King
        x, y = self.current_Location
        valid_moves = []

        # Dictionary for quick lookup
        occupied_positions = {piece.current_Location: piece for piece in Piece.current_pieces_list}

        # Define diagonal movement directions: Top-Right, Top-Left, Bottom-Right, Bottom-Left
        directions = [(75, 75), (-75, 75), (75, -75), (-75, -75)]

        for dx, dy in directions:
            step = 1
            while True:
                new_x, new_y = x + dx * step, y + dy * step

                # Check if in board boundaries
                if not (0 <= new_x < 600 and 0 <= new_y < 600):
                    break  # Stop if out of bounds

                # Check if position is occupied
                if (new_x, new_y) in occupied_positions:
                    piece = occupied_positions[(new_x, new_y)]
                    if piece.color == self.color:
                        piece.defended=True
                        opponent_king = King.white_king_instance if self.color=="black" else King.black_king_instance
                        opponent_king.valid_moves=[move for move in opponent_king.valid_moves if move != piece.current_Location]


                    if piece.color != self.color:
                        valid_moves.append((new_x, new_y))  # Capture opponent's piece
                    break  # Stop moving in this direction

                valid_moves.append((new_x, new_y))  # Valid empty square
                step += 1  # Continue in the same direction

        return valid_moves