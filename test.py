import chess
import chess.svg
import chess.pgn
import io
import math
import base64
import time
from State import State
from Zobrist import zobrist

board = chess.Board()
state = State(board)
game = chess.pgn.Game()
zobrist = zobrist()
transpositions = {}
ct=0
#read from database
pgn = open('games/caissabase.pgn')
mastergame = ""
games = []
gc=0
while((game != None) & (gc < 500)):
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
    global state
    board = chess.Board()
    board.reset_board()
    board.reset()
    state = State(board)
    
    ret = "<html><svg width ='700' height = '700'>"
    ret += chess.svg.board(board)
    ret += "</svg>"
    ret += "<a href='/move'><button>Move</button></as>"
    return ret


@app.route("/human")
def play():
    pass
def computermove(s):
    global game
    if board.fullmove_number < 5:
        """for the opening, copy a master"""
        move = playOpening(game)
        if(move!=-1):
            game.add_main_variation(move)
            game = game.end()
            print(move)
            print(board)
            state.board.push(move)
        else:
            bestmove =playMove(state)
            state.board.push(bestmove)
            print(state.board)
    

    #TODO: move ordering, iterative deepening
    else:        
        bestmove = playMove(state)
        state.board.push(bestmove)
    
@app.route("/move")
def move():
    global ct
    global board
    global state
    start = time.time()
    ct = 0
    state = State(board)
    
    bestmove = computermove(state)
    print(not state.board.turn,"played: \n",state.board, "\nwith eval",state.evaluate())

    ret = "<html>"
    ret += "<a href='/move'><button>Move</button></a>"
    ret += "<a href='/'><button>Go Home></button></a>"
    ret += '<div><img width=600 height=600 src="data:image/svg+xml;base64,%s"></img></div>' % to_svg(state)
    ret += "<h1>" + format(state.evaluate(),".2f") + "</h1>"
    ret += "<h1>Evaluated: " + str(ct)+"</h1>"
    ret += "<h1>Hash: " + str(zobrist.gen_zobhash(state.board))+"</h1>"
    end = time.time()
    ret += "<h1>"+str(end-start)+"</h1>"
    return ret


def playMove(state):
    b = state.board
    scores = []
    #iterative deepening
    #begin iterative deepening
    bestmove = None
    print("Choosing move for", "white" if b.turn else "black")
    start = time.time()
    for i in range(4):
        scores = []
        if(bestmove != None):
            print("starting with bestmove:",bestmove)
            if(time.time()-start > 5):
                print("TIMES UP")
                #return bestmove
            b.push(bestmove)
            scores.append((-negamax(state,i,b.turn,-math.inf,math.inf),bestmove))
            b.pop()

        for m in state.orderMoves():
            b.push(m[0])
            scores.append((-negamax(state,i,b.turn,-math.inf,math.inf),m[0]))
            b.pop()

        sort = sorted(scores, key = lambda x:x[0], reverse = True)
        bestmove = sort[0][1]
        topeval = sort[0][0]
        print("bestmove:",bestmove,"withval",topeval)

        # for move in sort:
        #     print("move:",move[1],"withval",move[0])
    # for s in state.successors():
    #     scores.append((minimax(s,0,s.board.turn,-math.inf,math.inf),s))
    end = time.time()
    #print("minimaxed successors in %f", end-start)
    #print("Chose move ", bestmove.uci(),topeval, "for white" if b.turn else "for black")
    return bestmove


def negamax(s, depth, turn,alpha, beta):
    global ct
    ct +=1
    b = s.board
    if(depth ==0 or b.is_game_over()):
        return s.evaluate() if turn else -s.evaluate()
    ordered = s.orderMoves()
    maxval = -math.inf
    for move in ordered:
        """for each move in the ordered list, push to state board, perform negamax"""
        start = time.time()
        s.board.push(move[0])
        hash = zobrist.gen_zobhash(s.board)
        if(hash in transpositions):
            s.board.pop()
            print("using transposition",hash)
            if(depth == 4):
                print("move:", move[0], "givenvalue", transpositions[hash], "capturevalue",move[1],"for player","white" if s.board.turn else "black")
            maxval = transpositions[hash]
        else:
            x = -negamax(s,depth - 1, not turn, -beta,-alpha)
            if(x>maxval):
                #print("move:", move[0], "givenvalue", x, "capturevalue",move[1],"for player","white"if s.board.turn else "black")
                maxmove = move[0]
                maxval = x
            s.board.pop()
            transpositions[hash] = maxval
        #maxval = max(-negamax(s,depth - 1, -beta,-alpha),maxval)
        #print("current maxval", maxval)
        
        alpha = max(alpha, maxval)
        if(alpha > beta):
                #print("prune tree with move ", move[0],"alpha", alpha, "beta", beta)
                """prune"""
                break    
    #print("returning from depth", depth, "with bestmove ", maxmove, "for player ","white"if s.board.turn else "black")
    return maxval

def playOpening(s):
    """return a move to play from a gamenode"""
    global games
    start = time.time()
    fen = s.board().fen()
    print(s.board())
    foundgame = 0
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


def minimax(s, depth, maximizingplayer,alph,beta, prevbest = None):
    global ct
    ct+=1
    if depth ==0 or s.board.is_game_over():
        if(s.board.turn):
            return s.evaluate()
        else:
            return -s.evaluate()


    if maximizingplayer:
        #must be white
        maxval = -math.inf
        
        ordered = s.orderMoves()
        for move in ordered:
            start = time.time()
            
            s.board.push(move[0])
            maxval = max(minimax(s,depth-1, not maximizingplayer,alph,beta),maxval)
            s.board.pop()
            end = time.time()
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
            minval = min(minimax(s, depth - 1,not maximizingplayer,alph,beta),minval)
            s.board.pop()
            beta = min(beta, minval)
            if(minval <= alph):
                break
            
        
        return minval
    

if __name__ == "__main__":
    app.run(debug = True)
