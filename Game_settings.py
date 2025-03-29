import pygame

# Constants
pygame.init()

PLAYER_COLOR="white"
SIZE_CHESSBOARD = (600, 600)
SIZE_PIECES = (SIZE_CHESSBOARD[0] / 8, SIZE_CHESSBOARD[0] / 8)
THEME = pygame.transform.scale(pygame.image.load("Images/blue_board.png"), SIZE_CHESSBOARD)
Menu_Image = pygame.transform.scale(pygame.image.load("Images/menu_image.png"), size=SIZE_CHESSBOARD)

blue_button= pygame.transform.scale(pygame.image.load("Images/blue_button.png"), (90, 50))
red_button= pygame.transform.scale(pygame.image.load("Images/red_button.png"), (90, 50))
green_button= pygame.transform.scale(pygame.image.load("Images/green_button.png"), (90, 50))
play_button= pygame.transform.scale(pygame.image.load("Images/play_button.png"), (90, 50))
white_button= pygame.transform.scale(pygame.image.load("Images/white_button.png"), (90, 50))
black_button= pygame.transform.scale(pygame.image.load("Images/black_button.png"), (90, 50))

text_title=pygame.font.Font("freesansbold.ttf", 60).render("CHESS", True, (255, 255, 255))
text_color=pygame.font.Font("freesansbold.ttf", 30).render("COLOR:", True, 	(127,255,212))
text_difficulty=pygame.font.Font("freesansbold.ttf", 25).render("DIFFICULTY:", True, 	(127,255,212))

text_title_rect=text_title.get_rect(center=(SIZE_CHESSBOARD[0] / 2, 60))
text_color_rect=text_color.get_rect(topleft=(10, 210))
text_difficulty_rect=text_difficulty.get_rect(topleft=(10, 310))
blue_button_rect=blue_button.get_rect(topleft=(190,300))
red_button_rect=red_button.get_rect(topleft=(500,300))
green_button_rect=green_button.get_rect(topleft=(350,300))
play_button_rect=play_button.get_rect(topleft=(260,450))
white_button_rect=white_button.get_rect(topleft=(210,200))
black_button_rect=black_button.get_rect(topleft=(410,200))

Victory_Image = pygame.transform.scale(pygame.image.load("Images/Victory.png"), size=SIZE_CHESSBOARD)
Defeat_Image = pygame.transform.scale(pygame.image.load("Images/Defeat.png"), size=SIZE_CHESSBOARD)
FPS = int(60)
AI_difficulty=10
selected_button_for_difficulty = "green"
selected_button_for_color = "white"



# Coordinates and Locations


variables = ["A", "B", "C", "D", "E", "F", "G", "H"]
numbers = ["1", "2", "3", "4", "5", "6", "7", "8"]
coordinates = []
for number in numbers:
    for variable in variables:
        coordinates.append(f"{variable}{number}")

locations = []

for ordinate in range(
    int(SIZE_CHESSBOARD[0] - SIZE_PIECES[0]), -int(SIZE_PIECES[0]), -int(SIZE_PIECES[0])
):
    for apsis in range(0, int(SIZE_CHESSBOARD[0]), int(SIZE_PIECES[0])):
        locations.append(tuple((apsis, ordinate)))

coordinates_locations = dict(zip(coordinates, locations))

def reverse_locations():
    for ordinate1 in range(
        int(0), int(SIZE_CHESSBOARD[0]), int(SIZE_PIECES[0])
    ):
        for apsis1 in range(0, int(SIZE_CHESSBOARD[0]), int(SIZE_PIECES[0])):
            locations.append(tuple((apsis, ordinate)))
    coordinates_locations1 = dict(zip(coordinates, locations))
    return coordinates_locations1


def show_checkmate_message(screen,winner):
    if PLAYER_COLOR == winner :
        victory_sound.play()
        screen.blit(Victory_Image,(0,0))
    else:
        defeat_sound.play()
        screen.blit(Defeat_Image, (0, 0))

    pygame.display.update()  # Update display
    pygame.time.delay(7000)

def show_menu(screen):
    global AI_difficulty,selected_button_for_difficulty,PLAYER_COLOR,selected_button_for_color

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if blue_button_rect.collidepoint(event.pos):
                AI_difficulty=1
                selected_button_for_difficulty= "blue"
            elif green_button_rect.collidepoint(event.pos):
                AI_difficulty=10
                selected_button_for_difficulty= "green"
            elif red_button_rect.collidepoint(event.pos):
                AI_difficulty=20
                selected_button_for_difficulty= "red"
            elif white_button_rect.collidepoint(event.pos):
                PLAYER_COLOR="white"
                selected_button_for_color= "white"
            elif black_button_rect.collidepoint(event.pos):
                PLAYER_COLOR="black"
                selected_button_for_color= "black"
            elif play_button_rect.collidepoint(event.pos):
                return False





    screen.blit(Menu_Image,(0,0))
    screen.blit(text_color, text_color_rect)
    screen.blit(text_difficulty, text_difficulty_rect)
    screen.blit(text_title, text_title_rect)
    screen.blit(white_button, white_button_rect)
    screen.blit(black_button, black_button_rect)
    screen.blit(green_button, green_button_rect)
    screen.blit(blue_button,blue_button_rect)
    screen.blit(red_button,red_button_rect)
    screen.blit(play_button,play_button_rect)

    if selected_button_for_difficulty == "blue":
        pygame.draw.rect(screen, (255, 0, 0), blue_button_rect, 3)  # 3 pixels thick border
    elif selected_button_for_difficulty == "green":
        pygame.draw.rect(screen, (255, 0, 0), green_button_rect, 3)
    elif selected_button_for_difficulty == "red":
        pygame.draw.rect(screen, (255, 0, 0), red_button_rect, 3)
    if selected_button_for_color == "white":
        pygame.draw.rect(screen, (255, 0, 0), white_button_rect, 3)
    elif selected_button_for_color == "black":
        pygame.draw.rect(screen, (255, 0, 0), black_button_rect, 3)

    pygame.display.update()
    return True




# Initialize sound effects
pygame.mixer.init()

move_sound = pygame.mixer.Sound("Sound Effects/moving_piece.wav")
capture_sound = pygame.mixer.Sound("Sound Effects/capturing_sound.wav")
check_sound = pygame.mixer.Sound("Sound Effects/check_sound.wav")
checkmate_sound = pygame.mixer.Sound("Sound Effects/checkmate_sound.wav")
castling_sound=pygame.mixer.Sound("Sound Effects/castling_sound.wav")
victory_sound=pygame.mixer.Sound("Sound Effects/Victory.wav")
defeat_sound=pygame.mixer.Sound("Sound Effects/Defeat_7sec.wav")




