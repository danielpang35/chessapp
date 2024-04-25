import chess
import chess.svg
import chess.pgn
import io
import math
import base64
import time
from State import State

board = chess.Board()
state = State(board)
game = chess.pgn.Game()
ct=0
#read from database
pgn = open('games/caissabase.pgn')
mastergame = ""
games = []
gc=0
while((game != None) & (gc < 500)):
    print("parsing game",gc)
    mastergame = chess.pgn.read_game(pgn)
    gc+=1
    games.append(mastergame)

from flask import Response, Flask

def to_svg(s):
  return base64.b64encode(chess.svg.board(board=s.board).encode('utf-8')).decode('utf-8')

app = Flask(__name__)
@app.route("/")
def home():
    global board
    board = chess.Board()
    
    ret = "<html><svg width ='700' height = '700'>"
    ret += chess.svg.board(board)
    ret += "</svg>"
    ret += "<a href='/move'><button>Move</button></as>"
    return ret

@app.route("/move")
def move():
    global board
    global state
    global game
    global ct
    ct = 0
    best = 0
    state = State(board)
    if board.fullmove_number < 5:
        """for the opening, copy a master"""
        print("current pos:",game.end().board())
        move = playOpening(game)
        if(move!=-1):
            game.add_main_variation(move)
            game = game.end()
            print(move)
            board.push(move)
            bestsucc = State(board)
        else:
            bestsucc =playMove(state)
    #TODO: move ordering, iterative deepening
    else:
        bestsucc = playMove(state)
        print(bestsucc.board)
    state = bestsucc
    board = bestsucc.board
    print(not board.turn,"played: \n",bestsucc.board, "\nwith eval",bestsucc.evaluate())

    ret = "<html>"
    ret += '<img width=600 height=600 src="data:image/svg+xml;base64,%s"></img><br/>' % to_svg(bestsucc)
    ret += "<h1>" + str(state.evaluate())+"</h1>"
    ret += "<h1>Evaluated: " + str(ct)+"</h1>"
    ret += "<a href='/move'><button>Move</button></as>"

    return ret

def playOpening(s):
    """return a move to play from a gamenode"""
    global games
    start = time.time()
    fen = s.board().fen()
    print(s.board())

    for game in games:
        while(game.next()!=None):
            if(game.board().fen() == fen):
                foundgame = game.next().move
            if(time.time()-start >=.5):
                if(foundgame):
                    return foundgame
                else:
                    return -1
            game = game.next()
    return -1

def playMove(state):
    b = state.board
    scores = []
    start = time.time()
    
    for s in state.successors():
        scores.append((minimax(s,0,s.board.turn,-math.inf,math.inf),s))
    end = time.time()
    print("minimaxed successors in %f", end-start)
    sort = sorted(scores, key = lambda x:x[0],reverse = state.board.turn)
    bestsucc = sort[0][1]
    topeval = sort[0][0]
    return bestsucc


def minimax(s, depth, maximizingplayer,alph,beta):
    global ct
    ct+=1
    if depth >=3 or s.board.is_game_over():
        return s.evaluate()
    if maximizingplayer:
        #must be white
        maxval = -math.inf
        
        ordered = s.orderMoves()
        for move in ordered:
            start = time.time()
            s.board.push(move[0])
            maxval = max(minimax(s,depth+1, not maximizingplayer,alph,beta),maxval)
            s.board.pop()
            end = time.time()
            print("searched ordered moves in %f ", end-start)
            alph = max(alph, maxval)
            if(maxval >= beta):
                break
        return maxval
    else:
        #must be black
        minval = math.inf
        ordered = s.orderMoves()
        for move in ordered:
            s.board.push(move[0])
            minval = min(minimax(s, depth + 1,not maximizingplayer,alph,beta),minval)
            s.board.pop()
            beta = min(beta, minval)
            if(minval <= alph):
                break
            
        
        return minval
    

if __name__ == "__main__":
    app.run(debug = True)
