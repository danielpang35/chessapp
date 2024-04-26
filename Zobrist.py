import numpy
import chess
import random
class zobrist:
    def __init__(self):
        self.setup()
    
    def setup(self):
        random.seed(1)
        self.piece_keys = numpy.zeros((12,64),dtype=numpy.uint64)
        self.enpassant_keys = numpy.zeros(64,dtype=numpy.uint64)
        self.turn_key = 0
        self.castling_keys = numpy.zeros(16,dtype=numpy.uint64)

        for i in range(12):
            for j in range(64):
                self.piece_keys[i][j] = numpy.uint64(random.getrandbits(64))
                self.enpassant_keys[j] = numpy.uint64(random.getrandbits(64))
        for i in range(16):
            self.castling_keys[i] = numpy.uint64(random.getrandbits(64))
        self.turn_key = numpy.uint64(random.getrandbits(64))

    def gen_zobhash(self,b):
        hash = numpy.uint64(0)
        pm = b.piece_map()
        #hash piece keys
        for piecesquare,piece in pm.items():
            piece = {"P": 0, "N": 1, "B": 2, "R": 3, "Q": 4, "K": 5, 
                     "p": 6, "n":7, "b":8, "r":9, "q":10, "k": 11}[piece.symbol()]
            hash^=self.piece_keys[(piece,piecesquare)]
        
        #hash en passant
        if ((b.ep_square!=None) & (b.has_legal_en_passant())):
            hash ^= self.enpassant_keys[b.ep_square]
        
        #hash castling rights
        hash ^= self.castling_keys[b.castling_rights>>62]
        
        #hash turn
        if(b.turn):
            hash^=self.turn_key
        
        return hash
