from contextlib import nullcontext
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

SEARCHSTART = 0
CURRBEST = ''
"""chess.Piece to arrayboard dict"""
piecetostring = {"P": "wp", "N": "wn", "B": "wb", "R": "wr", "Q": "wq", "K": "wk", 
                        "p": "bp", "n":"bn", "b":"bb", "r":"br", "q":"bq", "k": "bk"}
ct=0
pc = 0
quiescenodes = 0
movegentime = 0 
hashtime = 0
evaluationtime = 0
#read from database
pgn = open('game.pgn')
pgn = open('games/caissabase.pgn')
mastergame = ""
games = []
gc=0
transpositionct = 0
while((game != None) & (gc < 500)):
    mastergame = chess.pgn.read_game(pgn)
    gc+=1
    games.append(mastergame)

from flask import Response, request, Flask, render_template, make_response, jsonify, redirect

def to_svg(s):
  return base64.b64encode(chess.svg.board(board=s.board).encode('utf-8')).decode('utf-8')

app = Flask(__name__)
@app.route("/interact")
def serve():
    global state
    global board
    currentboard = {'init':boardtoarray(state.board),'player':True}
    

    return render_template('interact.html',data = currentboard)

@app.route("/reset", methods = ["POST"])
def reset():
    global state
    global board
    global game
    board = chess.Board()
    state = State(board)
    game = chess.pgn.Game()
    #initboard = {'init':boardtoarray(state.board)}
    return redirect("/interact")
@app.route("/undo",methods=['POST'])
def undo():
    global state
    global board
    global game
    state.board.pop()
    state.board.pop()
    return redirect("/interact")
@app.route("/com", methods = ['POST'])
def commove():
    global board
    global state
    global game
    global ct
    ct = 0
    """make move"""
    start = time.time()
    move,eval = computermove(state)
    end = time.time()

    print(state.board,"after computer move")
    """make new boardarray"""
    newb = boardtoarray(state.board)

    """pass in position metrics"""
    positionhash = zobrist.gen_zobhash(state.board)
    timetosearch = end-start
    print(eval)
    data = {
    'eval':-eval,
    'material':int(state.evaluate()),
    'nodessearched':int(ct),
    'searchtime':str(format(timetosearch,".2f"))+'s',
    'transpositions':len(transpositions),
    'transpositions utilized': transpositionct,
    'positionhash':int(positionhash),
    'nodespruned':pc,
    'quiescencenodes':quiescenodes,
    'movegentime':movegentime,
    'evaluationtime':evaluationtime,
    'hashtime':hashtime}
    '''convert move into tosquare,fromsquare'''
    fromsquare = chess.parse_square(move.uci()[0:2])
    tosquare = chess.parse_square(move.uci()[2:4])

    movedata = {'fromsquare':fromsquare, 'tosquare': tosquare}
    print(data)
    res = jsonify(board=newb,data=data,move=movedata)
    return res

@app.route("/human", methods = ['POST'])
def play():
    global board
    global state
    global game
    
    input = request.json
    fromsquare = int(input["fromsquare"])
    tosquare = int(input["tosquare"])
    try:
        print("trying to paly move:",fromsquare, tosquare)
        
        move = state.board.find_move(fromsquare,tosquare)
        san = state.board.san(move)
        print(move)
        state.board.push_san(san)
        game.add_main_variation(move)
        game = game.end()
        moved = True
        print(state.board,"after human move")
    except Exception as e:
        print(e)
        moved = False
    finally:
        newb = boardtoarray(state.board)

    if request.method == 'POST':
       
        print(request.json) 
    res = jsonify(board=newb,moved=moved)
    return res


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
    global game
    board = chess.Board()
    board.reset_board()
    board.reset()
    state = State(board)
    game = chess.pgn.Game()
    ret = "<html><svg width ='700' height = '700'>"
    ret += chess.svg.board(board)
    ret += "</svg>"
    ret += "<a href='/move'><button>Move</button></as>"
    ret += "<a href='/interact'><button>Play</button></as>"
    return ret


@app.route("/move")
def move():
    global ct
    global board
    global state
    global transpositions
    start = time.time()
    ct = 0
    state = State(board)

    currenteval = computermove(state)
    print(not state.board.turn,"played: \n",state.board, "\nwith eval",state.evaluate())
    ret = "<html>"
    ret += "<a href='/move'><button>Move</button></a>"
    ret += "<a href='/'><button>Go Home></button></a>"
    ret += '<div><img width=600 height=600 src="data:image/svg+xml;base64,%s"></img></div>' % to_svg(state)
    ret += "<h1>" + format(state.evaluate(),".2f") + "</h1>"
    ret += "<h1>Evaluated: " + str(ct)+"</h1>"
    ret += "<h1>Pruned: " + str(pc)+"</h1>"
    ret += "<h1>Transpositions Stored: " + str(len(transpositions))+"</h1>"
    ret += "<h1>Hash: " + str(zobrist.gen_zobhash(state.board))+"</h1>"
    end = time.time()
    ret += "<h1>"+str(end-start)+"</h1>"
    return ret


def computermove(s):
    global game
    global state
    if state.board.fullmove_number < 5:
        """for the opening, copy a master"""
        move = playOpening(game)
        if(move!=-1):
            game.add_main_variation(move)
            game = game.end()
            print(move)
            state.board.push(move)
            return move,state.evaluate()
        else:
            result =playMove(state)
            state.board.push(result[0])
            return result[0],result[1]
    

    #TODO: move ordering, iterative deepening
    else:        
        result = playMove(state)
        state.board.push(result[0])
        print(result[0])
        return result[0],result[1]

def playMove(state):
    global pc
    global transpositionct
    global quiescenodes
    global SEARCHSTART
    global CURRBEST
    global x
    global evaluationtime
    global movegentime
    global hashtime
    pc = 0
    transpositionct = 0
    quiescenodes = 0
    b = state.board
    evaluationtime = 0
    movegentime = 0
    hashtime = 0
    scores = []
    #iterative deepening
    #begin iterative deepening
    
    print("Choosing move for", "white" if b.turn else "black")
    SEARCHSTART = time.time()
    bestmove = None
    x=-math.inf

    for i in range(1,4):
        '''TODO: refactor this
        cannot prune any results from below, nor are moves being stored in a transposition table
        maybe:
        eval = negamax(state,i,not b.turn,-math.inf,math.inf'''
        scores = []
        if(bestmove != None):
            print("starting with bestmove:",bestmove, "at depth ", i)
            print("CURRBEST:",CURRBEST,x)
            b.push(bestmove)
            eval = (-negamax(state,i,b.turn,-math.inf,math.inf),bestmove)
            scores.append(eval)
            print("prev best move eval: ", eval)

            b.pop()
       
        for m in state.orderMoves():
            if(time.time()-SEARCHSTART > 3.0):
                print("bestmove:",CURRBEST,"withval",x)
                return bestmove,eval[0]
            b.push(m[0])
            eval =(-negamax(state,i,b.turn,-math.inf,math.inf),m[0])
            
            scores.append(eval)
            b.pop()

        """negamax returns the maximum value of state from perspective of player who's turn it is"""
        """scores stores negative maximum value of all successors"""
        sort = sorted(scores, key = lambda x:x[0], reverse = True)
        bestmove = sort[0][1]
        topeval = sort[0][0]
        print("chose ",bestmove,"withval",topeval)
        CURRBEST = bestmove
        x = topeval

       
    end = time.time()
    topeval = topeval if b.turn else -topeval
    return bestmove, topeval


def negamax(s, depth, turn,alpha, beta):
    global ct
    global pc
    global transpositionct
    global transpositions
    global movegentime
    global evaluationtime
    global hashtime
    givenalpha = alpha  #this is the best that maximizing player could hope for, or the worst position black has the choice of giving white
    b = s.board
    hashstart = time.time()
    hash = zobrist.gen_zobhash(b)
    hashtime += time.time()-hashstart
    if(hash in transpositions):
        entry = transpositions[hash]
        if(entry[1] >= depth):
            transpositionct +=1
            """get previously found alpha and betas"""
            if(entry[2]==0):
                return entry[0]
            # elif(entry[2] == 1):
            #     """UPPERBOUND"""
            #     #found upper bound, meaning this has been searched, yielding nothing better than alpha
            #     #value stored is the minimum value of the position
            #     alpha = max(alpha, entry[0])
           
            # else:
            #     '''LOWERBOUND'''
            #     #found lowerbound, meaning other player had something better before
            #     #position value is at least something, which is stored in table
            #     beta = min(beta, entry[0])
    ct +=1
    if(depth ==0 or b.is_game_over()):
        #quiesce search instead
        # return quiesce(s,alpha, beta)
        EVALSTART = time.time()
        evaluate = s.evaluate()
        evaluationtime +=time.time()-EVALSTART
        return evaluate if b.turn else -evaluate
    start = time.time()
    ordered = s.orderMoves()
    movegentime += time.time()-start
    maxval = -math.inf
    for move in ordered:
        """for each move in the ordered list, push to state board, perform negamax"""
        s.board.push(move[0])        
        maxval = max(-negamax(s,depth - 1, not turn, -beta,-alpha),maxval)
        s.board.pop()
        alpha = max(alpha, maxval)
        if(alpha >= beta):
            #if(depth >1):
                #print("prune tree with move", move[0], "at depth :", depth)
                #print("best move for ", b.turn, " here is so good, ",not b.turn," will not choose this tree.\nalpha:", alpha, "beta:", beta)
            """prune"""
            pc +=1
            break
    flag = 0
    if(alpha <= givenalpha):
        '''this search returned no better moves than the given alpha
            aka, we have found the upper bound of moves: givenalpha or alpha'''
        flag = 1
    elif(alpha >= beta):
        flag = -1
    else:
        flag = 0
    # if((alpha > givenalpha) & (alpha < beta)):
    #     flag = 0
    transpositions[hash] = (maxval, depth,flag)
    
    return maxval

def quiesce(s,alpha,beta):
    global movegentime
    '''given state, search all captures until only moves left are 'quiet' moves'''

    '''standingpat - a lower bound'''
    global quiescenodes
    quiescenodes+=1
    b = s.board
    standingpat = s.evaluate() if b.turn else -s.evaluate()
    start = time.time()
    caps = s.getCapturesOrdered()
    movegentime += time.time()-start
    if(standingpat >= beta):
        return beta
    elif(standingpat>alpha):
        alpha = standingpat
    for cap in caps:
        s.board.push(cap[0])
        capscore = -quiesce(s,-beta,-alpha)
        s.board.pop()
        if(capscore >=beta):
            return beta
        if(capscore < alpha):
            alpha = capscore    
    return alpha
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
