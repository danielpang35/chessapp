import chess
import chess.pgn
import copy

class State:
    """class representing a state
    a state in this context is a chess position, or board state
    a successor to any state is the position after one move has been played
    goal state: maximum score achievable"""
    values = {chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0}
        
    def __init__(self,board=None):
        if board is not None:
            self.board = copy.deepcopy(board)
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
                return 1000
            elif(b.result()=="0-1"):
                return -1000
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
        return val
    