import chessmasks as cm
 
NONE    = 0b0
PAWN    = 0b1   << 2
QUEEN   = 0b10  << 2
KING    = 0b11  << 2
ROOK    = 0b100 << 2
BISHOP  = 0b101 << 2
KNIGHT  = 0b110 << 2
ALL     = 0b111 << 2

WHITE = 0b01
BLACK = 0b10

pieceArray = [PAWN, QUEEN, KING, ROOK, BISHOP, KNIGHT]
colourArray = [WHITE, BLACK]

letterMap = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7}
numSet = set(["1", "2", "3", "4", "5", "6", "7", "8"])

class Bitboard():
    
    # Starting bitboards for each piece type DEFAULT
    DEFAULT = dict()
    
    DEFAULT[WHITE | NONE]       = 0b0
    DEFAULT[BLACK | NONE]       = 0b0
    DEFAULT[BLACK | ALL]        = 0b0
    DEFAULT[WHITE | ALL]        = 0b0
    
    DEFAULT[WHITE | PAWN]       = 0b11111111 << 8
    DEFAULT[WHITE | ROOK]       = 0b10000001
    DEFAULT[WHITE | KNIGHT]     = 0b01000010
    DEFAULT[WHITE | BISHOP]     = 0b00100100
    DEFAULT[WHITE | QUEEN]      = 0b00010000
    DEFAULT[WHITE | KING]       = 0b00001000
    
    DEFAULT[BLACK | PAWN]       = 0b11111111 << 8*6
    DEFAULT[BLACK | ROOK]       = 0b10000001 << 8*7
    DEFAULT[BLACK | KNIGHT]     = 0b01000010 << 8*7
    DEFAULT[BLACK | BISHOP]     = 0b00100100 << 8*7
    DEFAULT[WHITE | QUEEN]      = 0b00010000 << 8*7
    DEFAULT[WHITE | KING]       = 0b00001000 << 8*7


    def __init__(self, piece=NONE, bits=0):
        self.bits = bits
        self.piece = piece
        
    # Gets bitboard   
    def getBits(self):
        return self.bits
    
    def getPiece(self):
        return self.piece
    
    # Manually sets self.bits
    def setBits(self, bits):
        self.bits = bits
        
    def setPiece(self):
        return self.piece
        
    # Sets bits to default starting position
    def default(self):
        self.bits = Bitboard.DEFAULT[self.piece]
        
    # Gets bit for value corresponding to index, where index is in algebraic chess notation
    def getSquare(self, index):
        if len(index) == 2:
            if index[0] in letterMap and index[1] in numSet:
                
                col = index[0]
                row = int(index[1]) - 1
                
                return (self.bits >> (row*8 + col)) & 0b1
            
        raise Exception("Index must be a valid square on a chess board")
        
    def coordsToIndex(self, coords):
        if len(coords) == 2:
            row, column = coords
            return row*8 + column
        raise Exception("2 co-ordinates required, {} given.".format(len(coords)))
        
    def indexToCoords(self, index):
        pass
    
    def __getitem__(self, coords):
        index = coordsToIndex(coords)
        return (self.bits << index) & 0b1
        
        
    def __setitem__(self, coords, value):
        index = self.coordsToIndex(coords)
        bit = 0b1 << index
        
        if value == 1:
            self.bits = self.bits | bit
        elif value == 0:
            self.bits = self.bits & ~bit 

        else:
            raise Exception("value must be 1 or 0, value was {}".format(value))
            
    def getSlidingMoves(self, bitboardAll, bitboardOwn, pieceNum):
        
        mask = getCaptureMask(self.getPiece())
        
        masked = mask & bitboardAll.getBits()

        right = getRight(masked, pieceNum)
        left  = Left(masked, pieceNum)
        rightRev = revBits64(right)
        
        rightRev = calcMoves(right)
        calcLeft = calcMoves(left)
        calcRight = revBits64(right)
        
        combined = (calcRight << pieceNum + 1) | calcLeft
        final = combined & ~bitboardOwn.getBits()
        
        return final

    def __str__(self):
        tempText = ""
        for i in range(0,8):
            tempText = tempText + "{:08b}\n".format((self.bits >> 8*(7-i)) & 0b11111111)

        return tempText
    
class Gamestate():
    
    def __init__(self):
        self.white = dict()
        self.black = dict()
        for piece in pieceArray:
            self.white[piece | WHITE] = Bitboard(piece | WHITE)
            self.black[piece | BLACK] = Bitboard(piece | BLACK)

        
    
    def newGame(self):
        self.white[PAWN] = Bitboard()
        self.black[PAWN] = Bitboard()
        
# Gets the digits of a binary number after digit "pieceNum"
def getLeft(bits, pieceNum):
    return bits >> pieceNum + 1

# Gets the digits of a binary number up to digit "pieceNum"
def getRight(bits, pieceNum):
    ones = ((0b1 << pieceNum) - 0b1)
    return bits & ones

# Reverses the bits of a 64 digit binary number
def revBits64(bits):
    rev = 0b0
    for i in range(0,64):
        rev |= (~(bits >> i) & 0b1 ) << i
        
    return rev
    
def calcMoves(bits, mask):
    return ((bits-1) ^ (bits)) & mask
    
class Gameboard():
    
    def __init__(self):
        for piece in pieceArray:
            for colour in colourArray:
                pass
    

test = Bitboard(WHITE | PAWN)
test.default()

test[0,4] = 1
print(test)


test = Bitboard()
test.setBits(cm.antiDiagMask[1])
print(test)


bits = cm.getCaptureMask(KING | WHITE, 3, 4)
test.setBits(bits)
print(test)
