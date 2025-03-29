import sys,pygame

import Game_settings
import Queen
from Game_settings import show_menu
from King import King
from Pawn import Pawn
from Piece import Piece
from Rook import Rook

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen
screen = pygame.display.set_mode(Game_settings.SIZE_CHESSBOARD)
pygame.display.set_caption("Chess")
icon = pygame.image.load("Images/chess_icon.png")
pygame.display.set_icon(icon)
clock = pygame.time.Clock()

# Flags and control mechanism
booted_up = False
menu_open = True
king_becomes_red_after_discovery_check = False
winner=None
checkmated=False
valid_moves=None
running = True
dragging = False
selected_piece = None
offset_x = offset_y = 0
turn="white"
best_move_for_black=None
AI_selected_piece=None
AI_next_move=None





# Main Loop
while running:
    clock.tick(Game_settings.FPS)
    # Show Menu
    while menu_open:
        menu_open=show_menu(screen)

    # Boot up the pieces
    if not booted_up:
        import AI
        booted_up = True
        Piece.boot_up()




    # AI Move
    if turn == "black":
        pygame.time.delay(500)
        best_move_for_black = AI.get_the_best_move(Piece.get_fen(turn))
        AI_selected_piece_n_next_move = AI.get_the_piece_and_destination_location_by_move(best_move_for_black)
        AI_selected_piece = AI_selected_piece_n_next_move[0]
        AI_next_move = AI_selected_piece_n_next_move[1]
        AI_selected_piece.current_Location = AI_next_move

        # Check if pawn reached the promotion rank
        if isinstance(AI_selected_piece, Pawn):
            if ((AI_selected_piece.color == "white" and Game_settings.PLAYER_COLOR == "white" and
                 AI_selected_piece.current_Location[1] == 0) or (
                        AI_selected_piece.color == "black" and Game_settings.PLAYER_COLOR == "black" and
                        AI_selected_piece.current_Location[1] == 0)) or \
                    (AI_selected_piece.color == "black" and Game_settings.PLAYER_COLOR == "white" and
                     AI_selected_piece.current_Location[1] == 525) or (
                    AI_selected_piece.color == "white" and Game_settings.PLAYER_COLOR == "black" and
                    AI_selected_piece.current_Location[1] == 525):
                # Create a new queen in the pawn's place
                promoted_queen = Queen.Queen()
                promoted_queen.color = AI_selected_piece.color
                promoted_queen.current_Location = AI_selected_piece.current_Location
                Piece.current_pieces_list.append(promoted_queen)
                promoted_to_queen = True
                # Remove the pawn from the list
                Piece.current_pieces_list.remove(AI_selected_piece)
                AI_selected_piece=promoted_queen

        # Check king threat
        AI_selected_piece.check_threatening_king()

        # King becomes red by discovery check
        if not AI_selected_piece.threads_the_king and not do_not_change_2_square_Flag:
            for piece in Piece.current_pieces_list:
                enemy_king = King.white_king_instance if piece.color == "black" else King.black_king_instance
                if enemy_king.current_Location in piece.get_valid_moves():
                    #New added deletable if bug
                    enemy_king.threatened = True
                    if Piece.total_check_count_in_turn == 0:
                        enemy_king.image_white.fill((200, 0, 0, 180), special_flags=pygame.BLEND_RGBA_MULT)
                        enemy_king.image_black.fill((200, 0, 0, 180), special_flags=pygame.BLEND_RGBA_MULT)
                        Game_settings.check_sound.play()
                        king_becomes_red_after_discovery_check = True
                        Piece.total_check_count_in_turn = Piece.total_check_count_in_turn + 1
                        break

        # Capture Piece
        for piece in Piece.current_pieces_list:
            if piece != AI_selected_piece:
                capture_Flag = AI_selected_piece.capture_piece(piece)
                if capture_Flag:
                    Game_settings.capture_sound.play()
                    break
            if isinstance(AI_selected_piece, Pawn) and isinstance(piece,
                                                               Pawn) and piece.just_moved_two_squares and AI_selected_piece.current_Location == AI_selected_piece.en_passant_move_location:
                Piece.current_pieces_list.remove(AI_selected_piece.en_passant_taken_piece)
                break

        # Update Castling Images

        Piece.update_short_castling(screen)
        Piece.update_long_castling(screen)


        # Update if castled
        if King.white_king_instance.current_Location != King.white_king_instance.first_location:
            King.white_king_instance.has_moved = True
        if King.black_king_instance.current_Location != King.black_king_instance.first_location:
            King.black_king_instance.has_moved = True


        # If checkmate
        if King.is_checkmate(King.black_king_instance):
            winner = "white"
            checkmated = True

        elif King.is_checkmate(King.white_king_instance):
            winner = "black"
            checkmated = True

        # Change turn
        Game_settings.move_sound.play()
        turn = "white"

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False


        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            mouse_pos = event.pos
            for piece in Piece.current_pieces_list:
                if piece.color=="white":
                    rect = piece.image_white.get_rect(topleft=piece.current_Location)
                else:
                    rect = piece.image_black.get_rect(topleft=piece.current_Location)
                if rect.collidepoint(mouse_pos):
                    dragging = True
                    selected_piece = piece if piece.color=="white" else None
                    #selected_piece=piece if piece.color==turn else None
                    if selected_piece:
                        valid_moves=selected_piece.get_valid_moves()
                        previous_Location=piece.current_Location
                        offset_x = mouse_pos[0] - piece.current_Location[0]
                        offset_y = mouse_pos[1] - piece.current_Location[1]

            # Mouse movement while dragging
        elif event.type == pygame.MOUSEMOTION and dragging:
            if selected_piece:
                selected_piece.current_Location = (event.pos[0] - offset_x, event.pos[1] - offset_y)

            # Mouse button released
        elif event.type == pygame.MOUSEBUTTONUP:

            # Flags
            king_becomes_red_after_discovery_check = False
            defended=False
            promoted_to_queen=False
            do_not_change_2_square_Flag=False
            capture_Flag=False
            on_same_color_piece = False
            piece_shielding = False
            king_still_in_check = False

            if selected_piece:
                # Place the piece
                snap_to_Grid_Flag = selected_piece.snap_to_grid()



                # Check if pawn reached the promotion rank
                if isinstance(selected_piece, Pawn) and selected_piece.current_Location in valid_moves:
                    if ((selected_piece.color == "white" and Game_settings.PLAYER_COLOR=="white" and selected_piece.current_Location[1] == 0) or (selected_piece.color == "black" and Game_settings.PLAYER_COLOR=="black" and selected_piece.current_Location[1] == 0)) or \
                       (selected_piece.color == "black" and  Game_settings.PLAYER_COLOR=="white" and selected_piece.current_Location[1] == 525) or (selected_piece.color == "white" and  Game_settings.PLAYER_COLOR=="black" and selected_piece.current_Location[1] == 525):
                        # Create a new queen in the pawn's place
                        promoted_queen = Queen.Queen()
                        promoted_queen.color=selected_piece.color
                        promoted_queen.current_Location=selected_piece.current_Location
                        Piece.current_pieces_list.append(promoted_queen)
                        promoted_to_queen=True
                        # Remove the pawn from the list
                        Piece.current_pieces_list.remove(selected_piece)




                if snap_to_Grid_Flag[0] and snap_to_Grid_Flag[1]  in valid_moves:
                    selected_piece.check_threatening_king()

                if promoted_to_queen:
                    promoted_queen.check_threatening_king()

                # Check if piece defended
                if isinstance(selected_piece,King):
                    for piece in piece.current_pieces_list:
                        if piece!=selected_piece:
                            if selected_piece.current_Location==piece.current_Location and piece.defended:
                                defended=True




                #  Check if over same color piece
                if not snap_to_Grid_Flag[0] or snap_to_Grid_Flag[1] not in valid_moves:
                    # noinspection PyUnboundLocalVariable
                    on_same_color_piece=True

                # Check if piece shielding
                if turn=="white":
                    for piece in Piece.current_pieces_list:
                        if King.white_king_instance.current_Location in piece.get_valid_moves() and piece.color=="black":
                            if selected_piece.current_Location != piece.current_Location:
                                piece_shielding=True
                                break
                else:
                    for piece in Piece.current_pieces_list:
                        if King.black_king_instance.current_Location in piece.get_valid_moves() and piece.color=="white":
                            if selected_piece.current_Location!=piece.current_Location:
                                piece_shielding=True
                                break


                # Check if  king threatened
                if King.white_king_instance.threatened and turn == "white":
                    for piece in Piece.current_pieces_list:
                        if King.white_king_instance.current_Location in piece.get_valid_moves() and piece.color=="black":
                            if selected_piece.current_Location != piece.current_Location:
                                king_still_in_check = True
                                break



                if King.black_king_instance.threatened and turn == "black":
                    for piece in Piece.current_pieces_list:
                        if King.black_king_instance.current_Location in piece.get_valid_moves() and piece.color=="white":
                            if selected_piece.current_Location != piece.current_Location:
                                king_still_in_check = True
                                break






                # Return to previous position
                if king_still_in_check or piece_shielding or on_same_color_piece or defended:
                    selected_piece.current_Location = previous_Location
                    do_not_change_2_square_Flag=True

                # King becomes red by discovery check
                if not selected_piece.threads_the_king and not do_not_change_2_square_Flag:
                    for piece in Piece.current_pieces_list:
                        enemy_king = King.white_king_instance if piece.color == "black" else King.black_king_instance
                        if enemy_king.current_Location in piece.get_valid_moves():
                            if Piece.total_check_count_in_turn == 0:
                                enemy_king.image_white.fill((200, 0, 0, 180), special_flags=pygame.BLEND_RGBA_MULT)
                                enemy_king.image_black.fill((200, 0, 0, 180), special_flags=pygame.BLEND_RGBA_MULT)
                                Game_settings.check_sound.play()
                                king_becomes_red_after_discovery_check = True
                                Piece.total_check_count_in_turn = Piece.total_check_count_in_turn + 1
                                break





                # Capture Piece
                for piece in Piece.current_pieces_list:
                    if piece != selected_piece :
                        capture_Flag = selected_piece.capture_piece(piece)
                        if capture_Flag:
                            Game_settings.capture_sound.play()
                            break
                    if isinstance(selected_piece, Pawn) and isinstance(piece, Pawn) and piece.just_moved_two_squares and selected_piece.current_Location==selected_piece.en_passant_move_location:
                        Piece.current_pieces_list.remove(selected_piece.en_passant_taken_piece)
                        break


                # Update Castling Mechanics
                Piece.update_short_castling(screen)
                Piece.update_long_castling(screen)


                # Update if castled
                if King.white_king_instance.current_Location != King.white_king_instance.first_location:
                    King.white_king_instance.has_moved = True
                if King.black_king_instance.current_Location != King.black_king_instance.first_location:
                    King.black_king_instance.has_moved = True

                # Update if rook moves
                if isinstance(selected_piece, Rook):
                    if selected_piece.first_location != selected_piece.current_Location:
                        selected_piece.has_moved = True

                # Check moving 2 squares
                if isinstance(selected_piece, Pawn) and abs(
                        selected_piece.current_Location[1] - selected_piece.first_location[
                            1]) == 150:  # If pawn moved two squares
                    selected_piece.just_moved_two_squares = True  #  Set it to True






                # Changing turns
                if snap_to_Grid_Flag[0] and snap_to_Grid_Flag[1] in valid_moves and not king_still_in_check and not piece_shielding and not defended:
                    # If the move is valid, switch turns
                    Piece.total_check_count_in_turn=0
                    Game_settings.move_sound.play()
                    turn = "black" if turn == "white" else "white"





                # Reset En Passant flag for all pawns, except the one that just moved two squares
                if not  do_not_change_2_square_Flag:
                    for piece in Piece.current_pieces_list:
                        if isinstance(piece, Pawn):
                            if piece != selected_piece:
                                piece.just_moved_two_squares = False


                #Reset defended State
                for piece in piece.current_pieces_list:
                    piece.defended=False

                # If checkmate
                if King.is_checkmate(King.black_king_instance):
                    winner="white"
                    checkmated=True

                elif King.is_checkmate(King.white_king_instance):
                    winner="black"
                    checkmated=True




            dragging = False
            selected_piece = None




    screen.blit(Game_settings.THEME, (0, 0))

    # Update Piece Images
    for piece in Piece.current_pieces_list:
        if (isinstance(piece, King) and piece.threatened) or (not king_becomes_red_after_discovery_check and isinstance(piece, King)) :
            screen.blit(piece.image_white if piece.color == "white" else piece.image_black, piece.current_Location)
            if turn=="white" and piece.color=="black":
                piece.image_white = piece.original_white.copy()
                piece.image_black = piece.original_black.copy()
            if turn == "black" and piece.color == "white":
                piece.image_white = piece.original_white.copy()
                piece.image_black = piece.original_black.copy()
        else:
            screen.blit(piece.image_white if piece.color == "white" else piece.image_black, piece.current_Location)


    pygame.display.flip()
    if checkmated:
        Game_settings.checkmate_sound.play()
        pygame.time.delay(3000)
        Game_settings.show_checkmate_message(screen, winner)
        menu_open=True
        checkmated=False
        booted_up=False
        Piece.current_pieces_list=[]






pygame.quit()
sys.exit()



