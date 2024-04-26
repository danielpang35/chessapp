import chess
import chess.pgn
import copy
import time
class State:
    """class representing a state
    a state in this context is a chess position, or board state
    a successor to any state is the position after one move has been played
    goal state: maximum score achievable"""
    values = {chess.PAWN: 100,
            chess.KNIGHT: 300,
            chess.BISHOP: 335,
            chess.ROOK: 500,
            chess.QUEEN: 850,
            chess.KING: 120}
        
    def __init__(self,board=None):
        if board is not None:
            self.board = board
        else:
            self.board = chess.Board()
        pass
    def __lt__(self, other):
        return self.evaluate() < other.evaluate()
    def edges(self):
        return list(self.board.legal_moves)
    def successors(self):
        successors = []
        b = self.board
        for e in self.edges():
            b.push(e)
            s = State(b)
            successors.append(s)
            b.pop()
        return successors

    def evaluate(self):
        b = self.board
        if b.is_game_over():
            if(b.result()=="1-0"):
                return 10000
            elif(b.result()=="0-1"):
                return -10000
            else:
                return 0
        val = 0.0
        piecemap = b.piece_map()
        for piece in piecemap.values():
            if(piece.color):
                #must be a white piece
                val += self.values[piece.piece_type]
            else:
                #must be a black piece
                val -= self.values[piece.piece_type]    
            # add a number of legal moves term
        bak = b.turn
        b.turn = chess.WHITE
        val += .5*b.legal_moves.count()
        b.turn = chess.BLACK
        val -= .5*b.legal_moves.count()
        b.turn = bak
        return val/100
        
    def orderMoves(self):
        moveValue = 0
        moves = []
        b = self.board
        st = time.time()
        for move in b.legal_moves:
            moveValue = 0
            """calculate value of captures"""
            if(b.is_capture(move)):
                capturedpiece = b.piece_type_at(move.to_square)
                attacker = b.piece_type_at(move.from_square)
                if((capturedpiece != None) & (attacker != None)):
                    """assign any capture at least a value of 5"""
                    moveValue += State.values[capturedpiece] - State.values[attacker] + 5000
                    #print("move: ", move.uci(),chess.piece_name(capturedpiece), "captures",chess.piece_name(attacker), "attacker")
            moves.append((move,moveValue))

        moves = sorted(moves, key = lambda x: x[1])
        end = time.time()
        #print("took %f to order moves", end-st)
        # for move in moves:
        #     print("found move:",move[0].uci(),move[1])
        return moves
