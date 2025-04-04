import sys,subprocess

from Game_settings import *
from stockfish import Stockfish
from Piece import Piece

class QuietStockfish(Stockfish):
    def __init__(self, path):
        super().__init__(path)
        if sys.platform=="win32":
            self._stockfish = subprocess.Popen(
                [path],
                universal_newlines=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
        )



if sys.platform == "win32":
    stockfish_path = "stockfish_engine/Windows/stockfish-windows-x86-64-avx2.exe"
elif sys.platform == "darwin":
    stockfish_path = "stockfish_engine/MacOs/stockfish-macos-m1-apple-silicon"
else:
    stockfish_path = "stockfish_engine/Linux/stockfish-android-armv8"

stockfish = QuietStockfish(path=stockfish_path)
stockfish.update_engine_parameters({ "UCI_Elo": 500,})
stockfish.set_skill_level(AI_difficulty)
ai_cache = {}
coordinates_locations_reversed=reverse_locations()

def get_the_best_move(fen):
    try:
        if fen in ai_cache:
            return ai_cache[fen]
        else:
            stockfish.set_fen_position(fen)
            ai_cache[fen] = stockfish.get_best_move()
            return ai_cache[fen]
    except:
        print(ai_cache)
        raise Exception("AI Error")

def get_the_piece_and_destination_location_by_move(move):
    current_pos=move[0:2].upper()
    next_pos=move[2:4].upper()
    current_location=coordinates_locations[current_pos] if get_player_color()=="white" else coordinates_locations_reversed[current_pos]
    next_location=coordinates_locations[next_pos] if get_player_color()=="white" else coordinates_locations_reversed[next_pos]
    for piece in Piece.current_pieces_list:
        if piece.current_Location==current_location:
            return [piece,next_location]