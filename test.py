import chess
import chess.svg
import math
from State import State

board = chess.Board()

from flask import Response, Flask


app = Flask(__name__)
@app.route("/")
def home():
    board = chess.Board()
    ret = "<html><svg width ='700' height = '700'>"
    ret += chess.svg.board(board)
    ret += "</svg>"
    ret += "<a href='/move'><button>Move</button></as>"
    return ret

@app.route("/move")
def move():
    global board

    best = 0
    bestsucc = State()
    state = State(board)

    bestsucc = sorted(state.successors(), key=lambda x:x.evaluate(), reverse = state.board.turn)[0]

    print(bestsucc)
    # for succ in state.successors():
    #     if(succ.evaluate()>=best):
    #         best = succ.evaluate()
    #         bestsucc = succ
    #         print(best,bestsucc.board)
    state = bestsucc
    board = bestsucc.board
    ret = "<html>"
    ret += "<svg width ='700' height = '700'>"
    ret += chess.svg.board(bestsucc.board)
    ret += "</svg>"
    ret += "<h1>" + str(state.evaluate())+"</h1>"
    ret += "<a href='/move'><button>Move</button></as>"

    return ret
    
def choosemove(s):
    for s.board.legal_moves:

def minimax(s, depth, maximizingplayer,alph,beta):
    if depth >=5 or s.is_game_over:
        return s.evaluate()
    if maximizingplayer:
        #must be white
        maxval = math.inf
        for succ in s.successors():
            val = max(minimax(succ, depth+1,not maximizingplayer,alph,beta))
            maxval = max(val,maxval)
            alph = max(alph, val)
            if(beta <= alph):
                break
        return maxval
    else:
        #must be black
        minval = -math.inf
        for succ in s.successors():
            val = min(minimax(succ,depth + 1,not maximizingplayer,alph,beta))
            minval = min(val,minval)
            beta = min(val,minval)
            if(alph >= beta):
                break
        return minval
    

    
if __name__ == "__main__":
    app.run(debug = True)