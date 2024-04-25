import chess
import chess.svg
import math
from State import State

board = chess.Board()

from flask import Response, Flask


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

    best = 0
    bestsucc = State()
    state = State(board)

    bestsucc = sorted(state.successors(), key=lambda x:minimax(x,0,x.board.turn,-math.inf,math.inf), reverse = state.board.turn)[0]

    print(bestsucc.board)
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
    

def minimax(s, depth, maximizingplayer,alph,beta):
    if depth >=4 or s.board.is_game_over():
        return s.evaluate()
    if maximizingplayer:
        #must be white
        maxval = math.inf
        print("HELP")
        for succ in s.successors():
            maxval = max(minimax(succ, depth+1,not maximizingplayer,alph,beta),maxval)
            alph = max(alph, maxval)
            if(maxval >= beta):
                print("pruned")
                break
        print(maxval)
        return maxval
    else:
        #must be black
        minval = math.inf
        for succ in s.successors():
            minval = min(minimax(succ,depth + 1,not maximizingplayer,alph,beta),minval)
            beta = min(beta,minval)
            if(minval <=alpha ):
                print("pruned")
                break
        print(minval)
        return minval
    

    
if __name__ == "__main__":
    app.run(debug = True)