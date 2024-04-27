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

"""chess.Piece to arrayboard dict"""
piecetostring = {"P": "wp", "N": "wn", "B": "wb", "R": "wr", "Q": "wq", "K": "wk", 
                        "p": "bp", "n":"bn", "b":"bb", "r":"br", "q":"bq", "k": "bk"}
ct=0
#read from database
pgn = open('game.pgn')
#pgn = open('games/caissabase.pgn')
mastergame = ""
games = []
gc=0
while((game != None) & (gc < 500)):
    mastergame = chess.pgn.read_game(pgn)
    gc+=1
    games.append(mastergame)

from flask import Response, request, Flask, render_template, make_response, jsonify

def to_svg(s):
  return base64.b64encode(chess.svg.board(board=s.board).encode('utf-8')).decode('utf-8')

app = Flask(__name__)
@app.route("/interact")
def serve():
    global board
    
    initdata = {'init':boardtoarray(board)}
    return render_template('home.html',data = initdata)

@app.route("/human", methods = ['POST'])
def play():
    global board
    global state
    input = request.json
    fromsquare = int(input["fromsquare"])
    tosquare = int(input["tosquare"])
    ucistr = chess.square_name(fromsquare) + chess.square_name(tosquare)
    print(ucistr)
    try:
        print("trying to paly move:",fromsquare, tosquare)

        move = chess.Move.from_uci(ucistr)
        if(move):
            print(move)
            board.push(move)
    except:
        print("failed move")
    finally:
        newb = boardtoarray(board)

    if request.method == 'POST':
        """modify/update the information for <user_id>"""
        # you can use <user_id>, which is a str but could
        # changed to be int or whatever you want, along
        # with your lxml knowledge to make the required
        # changes
        print(request.json) # a multidict containing POST data
    print(newb)
    res = jsonify(board=newb)
    return res
    return render_template("home.html")

def boardtoarray(board):
    arr = ['']*64
    for i in range(7,-1,-1):
        for j in range(8):
            squareindex = i*8+j
            square = board.piece_at(chess.Square(squareindex))
            if(square != None):
                piece = piecetostring[square.symbol()]
                #print(piece)
            else:
                piece = ''
            arr[squareindex] = piece
    return arr

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
    ret += "<a href='/interact'><button>Play</button></as>"
    return ret



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
            print("starting with bestmove:",bestmove, "at depth ", i)
            if(time.time()-start > 5):
                print("TIMES UP")
                #return bestmove
            b.push(bestmove)
            scores.append((-negamax(state,i,not b.turn,-math.inf,math.inf),bestmove))
            b.pop()

        for m in state.orderMoves():
            b.push(m[0])
            scores.append((-negamax(state,i,not b.turn,-math.inf,math.inf),m[0]))
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
        return s.evaluate()
    ordered = s.orderMoves()
    maxval = -math.inf
    for move in ordered:
        """for each move in the ordered list, push to state board, perform negamax"""
        start = time.time()
        s.board.push(move[0])
        hash = zobrist.gen_zobhash(s.board)
        if(hash in transpositions):
            s.board.pop()
            if(depth == 4):
                print("move:", move[0], "givenvalue", transpositions[hash], "capturevalue",move[1],"for player","white" if s.board.turn else "black")
            maxval = transpositions[hash]
        else:
            maxval = max(-negamax(s,depth - 1, not turn, -beta,-alpha),maxval)
            s.board.pop()
            transpositions[hash] = maxval if b.turn else -maxval
        #maxval = max(-negamax(s,depth - 1, -beta,-alpha),maxval)
        #print("current maxval", maxval)
        
        alpha = max(alpha, maxval)
        if(alpha < beta):
                #print("prune tree with move ", move[0],"alpha", alpha, "beta", beta)
                """prune"""
                break    
    return maxval

def playOpening(s):
    """return a move to play from a gamenode"""
    global games
    start = time.time()
    fen = s.board().fen()
    print(s.board())
    foundgame = 0
    for game in games:
        if(game):
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
