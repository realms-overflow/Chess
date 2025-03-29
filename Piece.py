from abc import abstractmethod
import pygame
import Game_settings


class Piece:
    castling_rights = "KQkq"
    total_check_count_in_turn = 0
    current_pieces_list = []
    color= None

    def __init__(self, **kwargs):
        # Current Location

        self.current_Location = None
        self.defended=False
        self.threads_the_king=False
        self.piece_type=None
        self.valid_moves=[]

        # White Image
        self.image_white = pygame.transform.scale(
            pygame.image.load(kwargs.get("image_path_white")), Game_settings.SIZE_PIECES
        )

        # Black Image
        self.image_black = pygame.transform.scale(
            pygame.image.load(kwargs.get("image_path_black")), Game_settings.SIZE_PIECES
        )

        # Starting Position White
        self.starting_pos_white = [
            Game_settings.coordinates_locations[pos]
            for pos in kwargs.get("starting_positions_white", [])
        ]

        # Starting Position Black
        self.starting_pos_black = [
            Game_settings.coordinates_locations[pos]
            for pos in kwargs.get("starting_positions_black", [])
        ]

    @abstractmethod
    def get_valid_moves(self):
        pass

    def capture_piece(self, piece):
        if self.color != piece.color and self.current_Location== piece.current_Location:
            if piece in Piece.current_pieces_list:
                Piece.current_pieces_list.remove(piece)
                return True

    def snap_to_grid(self):
        x, y = self.current_Location

        closest_square = None
        min_distance = float("inf")

        for square, position in Game_settings.coordinates_locations.items():
            dist = (x - position[0]) ** 2 + (y - position[1]) ** 2
            if dist < min_distance:
                min_distance = dist
                closest_square = position

        if closest_square:
            for other_piece in Piece.current_pieces_list:
                if other_piece.current_Location == closest_square and other_piece.color == self.color:
                    return [False,closest_square]

            self.current_Location = closest_square
            return [True,closest_square]

    def check_threatening_king(self):
        from King import King
        if self.color == "white":
            enemy_king = King.black_king_instance

        else:
            enemy_king = King.white_king_instance

        if enemy_king and enemy_king.current_Location in self.get_valid_moves():
            # Apply red tint
            enemy_king.threatened=True
            self.threads_the_king=True
            enemy_king.image_white = enemy_king.original_white.copy()
            enemy_king.image_black = enemy_king.original_black.copy()
            enemy_king.image_white.fill((200, 0, 0, 180), special_flags=pygame.BLEND_RGBA_MULT)
            enemy_king.image_black.fill((200, 0, 0, 180), special_flags=pygame.BLEND_RGBA_MULT)
            Game_settings.check_sound.play()
            return True

        else:
            # No threat, So restore
            enemy_king.threatened = False
            self.threads_the_king=False
            enemy_king.image_white = enemy_king.original_white.copy()
            enemy_king.image_black = enemy_king.original_black.copy()
            return False

    @classmethod
    def boot_up(cls):
        """Creates instances of pieces at their starting positions."""
        from Bishop import Bishop
        from Knight import Knight
        from King import King
        from Pawn import Pawn
        from Queen import Queen
        from Rook import Rook

        # Create instances of each piece subclass
        pieces = [Rook(), Pawn(), King(), Queen(), Bishop(), Knight()]

        if Game_settings.PLAYER_COLOR=="white":
            for piece in pieces:
                for pos in piece.starting_pos_white:
                    new_piece = piece.__class__()
                    new_piece.current_Location = pos
                    new_piece.color="white"
                    if isinstance(new_piece,King):
                        King.white_king_instance=new_piece
                        new_piece.first_location=pos
                    if isinstance(new_piece,Pawn):
                        new_piece.first_location=pos
                    cls.current_pieces_list.append(new_piece)

                for pos in piece.starting_pos_black:
                    new_piece = piece.__class__()
                    new_piece.current_Location = pos
                    new_piece.color = "black"
                    if isinstance(new_piece, King):
                        King.black_king_instance = new_piece
                        new_piece.first_location = pos
                    if isinstance(new_piece,Pawn):
                        new_piece.first_location=pos
                    cls.current_pieces_list.append(new_piece)
        else:
            for piece in pieces:
                for pos in piece.starting_pos_black:
                    new_piece = piece.__class__()
                    new_piece.current_Location = pos
                    new_piece.color = "white"
                    if isinstance(new_piece, King):
                        King.white_king_instance = new_piece
                        new_piece.first_location = pos
                    if isinstance(new_piece,Rook):
                        new_piece.first_location=pos
                    if isinstance(new_piece, Pawn):
                        new_piece.first_location = pos
                    cls.current_pieces_list.append(new_piece)

                for pos in piece.starting_pos_white:
                    new_piece = piece.__class__()
                    new_piece.current_Location = pos
                    new_piece.color = "black"
                    if isinstance(new_piece, King):
                        King.black_king_instance = new_piece
                        new_piece.first_location = pos
                    if isinstance(new_piece, Rook):
                        new_piece.first_location = pos
                    if isinstance(new_piece, Pawn):
                        new_piece.first_location = pos
                    cls.current_pieces_list.append(new_piece)

    @staticmethod
    def check_piece_collision_with_mouse():
        click_pos = pygame.mouse.get_pos()
        for piece in Piece.current_pieces_list:
            rect_white = piece.image_white.get_rect(topleft=piece.current_Location)
            rect_black = piece.image_black.get_rect(topleft=piece.current_Location)
            if rect_white.collidepoint(click_pos) or rect_black.collidepoint(click_pos):
                print("Clicked on a piece at:", piece.current_Location)

    @staticmethod
    def print_coordinate_location_on_click():
        click_pos = pygame.mouse.get_pos()
        for coordinates_location, position in Game_settings.coordinates_locations.items():
            if pygame.Rect(position, Game_settings.SIZE_PIECES).collidepoint(click_pos):
                print(coordinates_location)


    @classmethod
    def get_fen(cls,turn):
        from King import King
        from Rook import Rook

        SQUARE_SIZE = 75

        # Create an empty 8x8 board
        board = [["" for _ in range(8)] for _ in range(8)]

        # Place pieces on the board
        for piece in cls.current_pieces_list:
            # Convert pixel location to board coordinates
            x_pixel, y_pixel = piece.current_Location  # Assuming pixel coordinates are stored here
            x = x_pixel // SQUARE_SIZE
            y = y_pixel // SQUARE_SIZE

            # Make sure x, y are within bounds (0 to 7)
            if 0 <= x < 8 and 0 <= y < 8:
                char = piece.get_fen_symbol()  # Let the piece decide its FEN code
                board[y][x] = char
            else:
                print(f"Warning: Piece at {piece.current_Location} is out of bounds!")

        # Create the FEN string
        fen_rows = []
        for row in board:
            fen_row = ""
            empty_count = 0

            for square in row:
                if square == "":
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen_row += str(empty_count)
                        empty_count = 0
                    fen_row += square

            if empty_count > 0:  # Add remaining empty squares if any
                fen_row += str(empty_count)

            fen_rows.append(fen_row)

        # Join rows with "/" to create the FEN board representation
        fen_board = "/".join(fen_rows)

        # Add other FEN parts as placeholders (turn, castling, en passant, etc.)
        # Typically, those depend on the full game context
        turn_char="w" if turn=="white" else "b"

        for piece in cls.current_pieces_list:
            if isinstance(piece,Rook) and piece.color=="white" and piece.has_moved:
                if  piece.current_Location[0]>King.white_king_instance.current_Location[0]:
                    cls.castling_rights = cls.castling_rights.replace("K","")
                    break
            if isinstance(piece,Rook) and piece.color=="white" and piece.has_moved:
                if  piece.current_Location[0]<King.white_king_instance.current_Location[0]:
                    cls.castling_rights = cls.castling_rights.replace("Q","")
                    break
            if isinstance(piece,Rook) and piece.color=="black" and piece.has_moved:
                if  piece.current_Location[0]>King.white_king_instance.current_Location[0]:
                    cls.castling_rights = cls.castling_rights.replace("k","")
                    break
            if isinstance(piece,Rook) and piece.color=="black" and piece.has_moved:
                if  piece.current_Location[0]<King.white_king_instance.current_Location[0]:
                    cls.castling_rights = cls.castling_rights.replace("q","")
                    break



        if King.white_king_instance.has_moved:
            cls.castling_rights = cls.castling_rights.replace("K", "")
            cls.castling_rights = cls.castling_rights.replace("Q", "")
        if King.black_king_instance.has_moved:
            cls.castling_rights = cls.castling_rights.replace("k", "")
            cls.castling_rights = cls.castling_rights.replace("q", "")

        fen = f"{fen_board} {turn_char} {cls.castling_rights} - 0 1"
        return fen

    def get_fen_symbol(self):
        symbol_map = {  # Example symbol mapping
            "pawn": "p",
            "knight": "n",
            "bishop": "b",
            "rook": "r",
            "queen": "q",
            "king": "k",
        }
        piece_type = getattr(self, "piece_type", "pawn").lower()
        symbol = symbol_map.get(piece_type, "p")

        # Uppercase for white, lowercase for black
        return symbol.upper() if self.color == "white" else symbol.lower()









    @staticmethod
    def mirror_fen(fen, axis='vertical'):
        """
        Mirror or reverse a FEN string.

        :param fen: FEN string to mirror.
        :param axis: Axis to flip ('horizontal', 'vertical', 'all').
        :return: New FEN string after mirroring.
        """
        # Split the FEN into its components
        parts = fen.split()
        board_layout = parts[0]
        #turn = parts[1]
        castling_rights = parts[2]
        en_passant = parts[3]
        halfmove_clock = parts[4]
        fullmove_number = parts[5]

        # Split the board layout into rows
        rows = board_layout.split('/')

        if axis == 'horizontal':
            # Reverse each row (left-right flip)
            rows = [''.join(reversed(row)) for row in rows]

        elif axis == 'vertical':
            # Reverse the order of rows (top-bottom flip)
            rows = rows[::-1]

        elif axis == 'all':
            # Combine vertical and horizontal flip
            rows = [''.join(reversed(row)) for row in rows[::-1]]

        else:
            raise ValueError("Invalid axis value. Use 'horizontal', 'vertical', or 'all'.")

        # Process castling rights (reverse KQkq if "all" or "vertical" flips happen)
        if axis in ['vertical', 'all']:
            castling_rights = castling_rights.translate(str.maketrans('KQkq', 'kqKQ'))

        # Process en passant (adjust row numbers if "vertical" or "all")
        if en_passant != '-':
            file = en_passant[0]
            rank = en_passant[1]
            if axis in ['vertical', 'all']:
                new_rank = str(9 - int(rank))  # Rows are flipped vertically
                en_passant = file + new_rank

        # Join the transformed rows back into a string
        new_board_layout = '/'.join(rows)

        # Reconstruct the new FEN
        new_fen = f"{new_board_layout} b {castling_rights} {en_passant} {halfmove_clock} {fullmove_number}"
        return new_fen

    @staticmethod
    def update_long_castling(screen):
        from King import King
        from Rook import Rook

        # Player color: White / Up Left Black
        if King.black_king_instance.current_Location == (150, 0) and Game_settings.PLAYER_COLOR == "white":
            for piece in Piece.current_pieces_list:
                if isinstance(piece,
                              Rook) and piece.color == "black" and piece.castling_long and not King.black_king_instance.has_moved:
                    piece.current_Location = (225, 0)
                    piece.castling_long = False
                    piece.check_threatening_king()
                    screen.blit(piece.image_white if piece.color == "white" else piece.image_black,
                                piece.current_Location)

        # Player color: White / Up Left White
        if King.white_king_instance.current_Location == (
                150, 525) and Game_settings.PLAYER_COLOR == "white":
            for piece in Piece.current_pieces_list:
                if isinstance(piece,
                              Rook) and piece.color == "white" and piece.castling_long and not King.white_king_instance.has_moved:
                    piece.current_Location = (225, 525)
                    piece.castling_long = False
                    piece.check_threatening_king()
                    screen.blit(piece.image_white if piece.color == "white" else piece.image_black,
                                piece.current_Location)

        # Player color: Black / For Up Left White
        if King.white_king_instance.current_Location == (
                150, 0) and Game_settings.PLAYER_COLOR == "black":
            for piece in Piece.current_pieces_list:
                if isinstance(piece,
                              Rook) and piece.color == "white" and piece.castling_long and not King.white_king_instance.has_moved:
                    piece.current_Location = (225, 0)
                    piece.castling_long = False
                    piece.check_threatening_king()
                    screen.blit(
                        piece.image_white if piece.color == "white" else piece.image_black,
                        piece.current_Location)

        # Player color: Black / For Bottom Left Black
        if King.black_king_instance.current_Location == (
                150, 525) and Game_settings.PLAYER_COLOR == "black":
            for piece in Piece.current_pieces_list:
                if isinstance(piece,
                              Rook) and piece.color == "black" and piece.castling_long and not King.black_king_instance.has_moved:
                    piece.current_Location = (225, 525)
                    piece.castling_long = False
                    piece.check_threatening_king()
                    screen.blit(
                        piece.image_white if piece.color == "white" else piece.image_black,
                        piece.current_Location)

    @staticmethod
    def update_short_castling(screen):
        from King import King
        from Rook import Rook

        # Player color: White / For Bottom Right
        if (King.white_king_instance.current_Location == (450, 525) and
                Game_settings.PLAYER_COLOR == "white"):
            for piece in Piece.current_pieces_list:
                if isinstance(piece,
                              Rook) and piece.color == "white" and piece.castling_short and not King.white_king_instance.has_moved:
                    piece.current_Location = (375, 525)
                    piece.castling_short = False
                    piece.check_threatening_king()
                    screen.blit(piece.image_white if piece.color == "white" else piece.image_black,
                                piece.current_Location)

        # Player color: Black / For Bottom Right
        if King.black_king_instance.current_Location == (450, 525) and Game_settings.PLAYER_COLOR == "black":
            for piece in Piece.current_pieces_list:
                if isinstance(piece,
                              Rook) and piece.color == "black" and piece.castling_short and not King.black_king_instance.has_moved:
                    piece.current_Location = (375, 525)
                    piece.castling_short = False
                    piece.check_threatening_king()
                    screen.blit(piece.image_white if piece.color == "white" else piece.image_black,
                                piece.current_Location)

        # Player color: Black / For Up Right
        if (King.black_king_instance.current_Location == (450, 0) and
                Game_settings.PLAYER_COLOR == "white"):
            for piece in Piece.current_pieces_list:
                if isinstance(piece,
                              Rook) and piece.color == "black" and piece.castling_short and not King.black_king_instance.has_moved:
                    piece.current_Location = (375, 0)
                    piece.castling_short = False
                    piece.check_threatening_king()
                    screen.blit(piece.image_white if piece.color == "white" else piece.image_black,
                                piece.current_Location)

        # Player color: White / For Up Right
        if King.white_king_instance.current_Location == (450, 0) and Game_settings.PLAYER_COLOR == "black":
            for piece in Piece.current_pieces_list:
                if isinstance(piece,
                              Rook) and piece.color == "white" and piece.castling_short and not King.white_king_instance.has_moved:
                    piece.current_Location = (375, 0)
                    piece.castling_short = False
                    piece.check_threatening_king()
                    screen.blit(piece.image_white if piece.color == "white" else piece.image_black,
                                piece.current_Location)











