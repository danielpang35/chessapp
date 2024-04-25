"""reads chess database"""

import chess.pgn
import State
str = open('game.pgn')

pgn = chess.pgn.read_game(str)
board = pgn.board()
for move in pgn.mainline_moves():
    board.push(move)
    print("\n",board)