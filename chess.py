import chessmasks as cm
import datetime as dt


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
BOTH  = 0b11


pieceArray      = [PAWN, QUEEN, KING, ROOK, BISHOP, KNIGHT]
colourArray     = [WHITE, BLACK]

pieceSet        = set(pieceArray)
colourSet       = set(colourArray)

slidingPieces   = set([QUEEN, BISHOP, ROOK])
staticPieces    = set([KNIGHT, KING])

promotePieces   = [QUEEN, ROOK, KNIGHT, BISHOP, KING]

letterMap = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7}
letterMapInv = {val: key for key, val in letterMap.items()}
numSet = set(["1", "2", "3", "4", "5", "6", "7", "8"])

pieceToLetter = {PAWN: "", QUEEN: "Q", ROOK: "R", KING: "K", KNIGHT: "N", BISHOP: "B"}

class Bitboard():
    
    # Starting bitboards for each piece type DEFAULT
    DEFAULT = dict()
    
    DEFAULT[NONE]               = 0b0
    
    DEFAULT[BLACK | NONE]       = 0b0
    DEFAULT[WHITE | NONE]       = 0b0
    DEFAULT[BLACK | ALL]        = 0b11111111_11111111
    DEFAULT[WHITE | ALL]        = 0b11111111_11111111 << 8*6
    
    DEFAULT[BOTH | ALL]         = DEFAULT[WHITE | ALL] + DEFAULT[BLACK | ALL] 
    
    DEFAULT[BLACK | PAWN]       = 0b11111111 << 8
    DEFAULT[BLACK | ROOK]       = 0b10000001
    DEFAULT[BLACK | KNIGHT]     = 0b01000010
    DEFAULT[BLACK | BISHOP]     = 0b00100100
    DEFAULT[BLACK | QUEEN]      = 0b00010000
    DEFAULT[BLACK | KING]       = 0b00001000
    
    DEFAULT[WHITE | PAWN]       = 0b11111111 << 8*6
    DEFAULT[WHITE | ROOK]       = 0b10000001 << 8*7
    DEFAULT[WHITE | KNIGHT]     = 0b01000010 << 8*7
    DEFAULT[WHITE | BISHOP]     = 0b00100100 << 8*7
    DEFAULT[WHITE | QUEEN]      = 0b00010000 << 8*7
    DEFAULT[WHITE | KING]       = 0b00001000 << 8*7


    def __init__(self, piece=NONE, bits=0b0):
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
    
    def __getitem__(self, coords):
        index = coordsToIndex(coords)
        return (self.bits >> index) & 0b1
        
        
    def __setitem__(self, coords, value):
        index = coordsToIndex(coords)
        bit = 0b1 << index
        
        if value == 1:
            self.bits = self.bits | bit
        elif value == 0:
            self.bits = self.bits & ~bit 

        else:
            raise Exception("value must be 1 or 0, value was {}".format(value))

    def __str__(self):
        tempText = ""
        for i in range(0,8):
            tempText = tempText + "{:08b}".format((self.bits >> 8*i) & 0b11111111)
            
            # if i != 7:
            tempText = tempText + "\n"

        return tempText
    
    def slideFromLeft(self, bitboardAll, bitboardOwn, coords, captureMask, reverse=False):
        pass
        
    
class Gamestate():
    
    def __init__(self):
        
        self.pieceBitboards  = dict()
        self.enPassant  = {WHITE: Bitboard(WHITE), BLACK: Bitboard(BLACK)}
        self.turn = WHITE
        
        self.moves = dict()
        self.captures = dict()
        
        self.pieceBitboards[BOTH | ALL] = Bitboard(BOTH | ALL)
        
        for pieceType in pieceArray + [ALL]:
            for colour in colourArray:
                self.pieceBitboards[pieceType | colour] = Bitboard(pieceType | colour)
                
    # Gets bitboard of the specified piece        
    def getBoard(self, piece):
        return self.pieceBitboards[piece]
    
    # Incase of disparity between piece boards and an "ALL" board
    def updateAlls(self):
        for colour in colourArray:
            bits = 0b0
            for pieceType in pieceArray:
                bits |= self.getBoard(colour | pieceType)
                
            self.getBoard(colour + ALL).setBits(bits)
                
    
    # Returns the bitboard containing all pieces of specified colour
    def getAll(self, colour=BOTH):
        return self.pieceBitboards[colour | ALL]
    
    # Sets all values to the appropriate value of a new game
    def default(self):
        
        self.turn = WHITE
        
        self.getBoard(BOTH + ALL).default()
        
        for colour in colourArray:
            self.enPassant[colour].default()
            
            for pieceType in pieceArray + [ALL]:
                self.getBoard(pieceType | colour).default()
                
    # Return all moves where a piece can be captured
    def getCaptures(self, piece, pos):
        oppColour = invColour(getColour(piece))
        
        if getPieceType(piece) == PAWN:
            return cm.getCaptureMask(piece, pos) & self.getAll(oppColour).getBits()
        else:
            return self.getMoves(piece,pos) & self.getAll(oppColour).getBits()
    
    # returns a binary number corresponding to legal moves for piece at position Pos
    # (Returns an integer number, not a Bitboard)
    def getMoves(self, piece, pos):
        
        pieceType   = getPieceType(piece)
        colour      = getColour(piece)

        if pieceType in slidingPieces:
            # print(Bitboard(bits=self.getSlidingMoves(piece,pos)))
            return self.getSlidingMoves(piece, pos) & ~self.getAll(colour).getBits()

        elif pieceType in staticPieces:
            # print(Bitboard(bits=cm.getCaptureMask(piece, pos)))
            return cm.getCaptureMask(piece, pos) & ~self.getAll(colour).getBits()
        
        elif pieceType == PAWN:
            pawnMask = cm.getMoveMask(piece, pos) & ~self.getAll().getBits()
            
            if pawnMask != 0 and cm.canDoubleStepPawn(colour, pos):
                return cm.getDoubleStepPawnMask(colour, pos) & ~self.getAll().getBits()
            
            return pawnMask
        
        else:
            raise Exception("Piece {} is not a valid selection for getMoves".format(piece))

    
    # Gets moves for sliding pieces (Queen, Rook, Bishop)
    def getSlidingMoves(self, piece, coords):
        
        # Gets the digits of a binary number after digit "pieceNum"
        def getLeft(bits, pieceNum):
            return bits >> pieceNum + 1
        
        # Gets the digits of a binary number up to digit "pieceNum"
        def getRight(bits, pieceNum):
            ones = ((0b1 << pieceNum) - 0b1)
            return bits & ones
        
        # Reverses the bits of a 64 digit binary number
        # Example: revBits64(0b1101) = 0b0000...001011
        def revBits64(bits):
            revStr = bin(bits)[:1:-1]
            length = len(revStr)
            
            rev = int(revStr, 2) << (64 - length)
                
            return rev
        
        # 
        def getSlideFromMask(bits, mask):
            return ((bits-1) ^ (bits)) & mask
        
        pieceNum = coordsToIndex(coords)
        colour = piece & 0b11
        bitboardOwn = self.getAll(colour)
        bitboardAll = self.getAll()
        # This algorithm needs cleaning up and explaining.
        # May be more efficient to run along each slide manually
        
        final = 0b0
        #captureMask     = cm.getCaptureMask(piece, coords)
        for captureMask in cm.getCaptureLines(piece,coords):
            maskedPieces    = captureMask & bitboardAll.getBits()
            
            captureMaskRight    = getRight(captureMask, pieceNum)
            captureMaskRightRev = revBits64(captureMaskRight)
            
            right               = getRight(maskedPieces, pieceNum)
            rightRev            = revBits64(right)
            calcRightRev        = getSlideFromMask(rightRev, captureMaskRightRev)
            calcRight           = revBits64(calcRightRev)
            
            captureMaskLeft     = getLeft(captureMask, pieceNum)
            
            left                = getLeft(maskedPieces, pieceNum)
            calcLeft            = getSlideFromMask(left, captureMaskLeft)
            
            combined    = calcRight | (calcLeft << (pieceNum + 1) )
            final       |= combined & ~bitboardOwn.getBits()
        
        return final
    
    # Promotes a pawn in position pos to a piece of type pieceType
    def promotePiece(self, colour, pieceType, pos):
        pawnBoard       = self.getBoard(colour + PAWN)
        promoteBoard    = self.getBoard(colour + pieceType)
        
        pawnBoard[pos]      = 0
        promoteBoard[pos]   = 1
        
    #Moves piece from fromPos to toPos, and updates the ALL boards.
    def movePiece(self, piece, fromPos, toPos, capture=True, returnString=False):
        
        colour = getColour(piece)
        
        pieceBoard = self.getBoard(piece)
        
        if pieceBoard[fromPos] == 0:
            raise Exception("There is no piece of type {} at position {}".format(bin(piece), fromPos))
            
        if self.getAll(colour) == 1:
            raise Exception("There is already a piece of colour {} at position {}".format(bin(colour), toPos))
            
        if capture == True:
            
            oppColour = invColour(colour)
            # This could be handled more efficiently by specifying the capture board. Will rethink later
            for oppPieceType in pieceArray:
                oppBoard = self.getBoard(oppPieceType | oppColour)
                if oppBoard[toPos] == 1:
                    self[oppPieceType + oppColour, toPos[0], toPos[1]] = 0
                    
        self[piece, fromPos[0], fromPos[1]] = 0
        self[piece, toPos[0], toPos[1]]   = 1
                    
        if returnString == True:
            return pieceToLetter[piece] + coordsToAlg(fromPos) + "x" * int(capture) + coordsToAlg(toPos)
        
    #returns the piece in position pos
    def getPiece(self, pos):
        i,j = pos
        for pieceType in pieceArray:
            for colour in colourArray:

                if self.getBoard(pieceType + colour)[i,j] == 1:
                    return pieceType + colour

        return NONE

    # Returns True if a move is legal, False otherwise
    def isLegalMove(self, piece, fromPos, toPos):
        pieceBoard = self.getBoard(piece)
        if pieceBoard[fromPos] == 1:

            
            moveBits = self.getMoves(piece, fromPos)
            index = coordsToIndex(toPos)
            if (moveBits >> index) & 0b1 == 1:
                return True

        return False

    # args: piece, xPos, yPos
    # sets the value at (xPos, yPos) on piece's Bitboard to val
    def __setitem__(self, args, val):
        if len(args) != 3:
            raise Exception("3 arguments should be given; Piece, xPos, and yPos. {} were given".format(len(args)))
        if val != 1 and val != 0:
            raise Exception("Value must be 0 or 1, {} was given".format(val))
            
        piece, *pos = args
        colour = getColour(piece)
        
        board       = self.getBoard(piece)
        boardColAll = self.getAll(colour)
        boardAll    = self.getAll()
        
        board[pos]          = val
        boardColAll[pos]    = val
        boardAll[pos]       = val
    
    # args: piece, xPos, yPos
    def __getitem__(self, args):
        if len(args) != 3:
            raise Exception("3 arguments should be given; Piece, xPos, and yPos. {} were given".format(len(args)))
            
        piece, *pos = args    
        board = self.getBoard(piece)
        
        return board[pos]
    
    def __str__(self):
        pass

def invColour(colour):
    return ~colour & 0b11

def getColour(piece):
    return piece & 0b11

def getPieceType(piece):
    return piece & ~0b11

def onesBetween(ind1, ind2):
    ones = ((0b1 << (ind2 - ind1 + 1)) - 1) << ind1
    return bin(ones)


# Co-ordinate stuff
def coordsToIndex(coords):
    if len(coords) == 2:
        col, row = coords
        return 8*row + (7-col)
    raise Exception("2 co-ordinates required, {} given.".format(len(coords)))
    
def coordsToAlg(coords):
    if len(coords) == 2:
        col, row = coords
        return letterMapInv[row] + str(col+1)

    raise Exception("2 co-ordinates required, {} given".format(len(coords)))

def indexToCoords(index):
    row = index // 8
    col = 7 - (index % 8)

    return (col, row)

# test = Bitboard(WHITE + PAWN)
# test.default()

# test[0,2] = 1
# print(test)


# test = Bitboard()
# test.setBits(cm.antiDiagMask[1])
# print(test)


# bits = cm.getCaptureMask(BISHOP + WHITE, (3, 4))
# test.setBits(bits)
# print(test)
# print(test[1,1])

# game = Gamestate()
# game.default()

# game.getBoard(WHITE | BISHOP)
# print(game.getBoard(WHITE + BISHOP))
# # game.movePiece(WHITE | BISHOP, (2,0), (4,4))
# print(game.getBoard(WHITE + ROOK))
# tet = game.getSlidingMoves(WHITE + ROOK, (2,2))

# test.setBits(tet)
# print((test))


# print(coordsToAlg((3,7)))
# print(test)

