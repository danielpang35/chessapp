"""reads chess database"""

import chess.pgn
pgn = open('games/caissabase.pgn')


game = ""

while(game != None):
    game = chess.pgn.read_game(pgn)
    while(game.next()!=None):
        game = game.next()
        print(game.move)

