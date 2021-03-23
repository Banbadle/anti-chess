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

pieceArray  = [PAWN, QUEEN, KING, ROOK, BISHOP, KNIGHT]
pieceSet    = set(pieceArray)
colourArray = [WHITE, BLACK]
colourSet   = set(colourArray)

#CREATE MASKS
horizMask       = dict()
vertMask        = dict()
diagMask        = dict()
antiDiagMask    = dict()

pawnMaskWhite   = dict()
pawnMaskBlack   = dict()

queenMask       = dict()
kingMask        = dict()
rookMask        = dict()
bishopMask      = dict()
knightMask      = dict()

rookLines       = dict()
bishopLines     = dict()
queenLines      = dict()

pawnMoveWhite       = dict()
pawnMoveBlack       = dict()

for i in range(0,8):
    
    horizMask[i]    = (0b11111111) << i*8
    vertMask[i]     = (0b10000000_10000000_10000000_10000000_10000000_10000000_10000000_10000000 >> i)

for i in range(0,8):

    diagMask[i]         = (0b00000001_00000010_00000100_00001000_00010000_00100000_01000000_10000000 << i*8) & ((0b1 << 64) - 1)
    diagMask[-i]        = (0b00000001_00000010_00000100_00001000_00010000_00100000_01000000_10000000 >> i*8) & ((0b1 << 64) - 1)
    antiDiagMask[i]     = (0b10000000_01000000_00100000_00010000_00001000_00000100_00000010_00000001 << i*8) & ((0b1 << 64) - 1)
    antiDiagMask[-i]    = (0b10000000_01000000_00100000_00010000_00001000_00000100_00000010_00000001 >> i*8) & ((0b1 << 64) - 1)
    


for x in range(0,8):
    for y in range(0,8):
        #Variables for referencing diagonals
        diag        = y - x
        antiDiag    = x - (7-y)
        
        #ROOK
        rookMask[x,y]   = vertMask[x] | horizMask[y]
        rookLines[x,y]  = [vertMask[x], horizMask[y]]
        #BISHOP
        bishopMask[x,y] = diagMask[diag] | antiDiagMask[antiDiag]
        bishopLines[x,y]= [diagMask[diag], antiDiagMask[antiDiag]]
        #QUEEN
        queenMask[x,y]  = bishopMask[x,y] | rookMask[x,y]
        queenLines[x,y] = [*rookLines[x,y], *bishopLines[x,y]]
        
        #KING
        baseKing        = 0b1_11000000
        kingMaskTemp    = ((baseKing >> x) & 0b11111111)  << y*8
        
        kingMask[x,y]   =  kingMaskTemp | (kingMaskTemp << 8) | (kingMaskTemp >> 8)
        
        #PAWN
        basePawn        = 0b1_01000000
        pawnMaskTemp    = ((basePawn >> x) & 0b11111111)  << y*8
        
        pawnMaskWhite[x,y]  = (pawnMaskTemp >> 8) & ((0b1 << 64) - 1)
        pawnMaskBlack[x,y]  = (pawnMaskTemp << 8) & ((0b1 << 64) - 1)
        
        basePawnMove        = 0b10000000
        pawnMoveMask        = (basePawnMove >> x) << y*8
        pawnMoveWhite[x,y]  = (pawnMoveMask >> 8) & ((0b1 << 64) - 1)
        pawnMoveBlack[x,y]  = (pawnMoveMask << 8) & ((0b1 << 64) - 1)
        
        #KNIGHT
        baseKnight1     = 0b10_00100000
        knightMaskTemp1 = ((baseKnight1 >> x) & 0b11111111) << y*8
        baseKnight2     = 0b01_01000000
        knightMaskTemp2 = ((baseKnight2 >> x) & 0b11111111) << y*8
        
        knightMask[x,y] = (knightMaskTemp1 << 8 | knightMaskTemp1 >> 8) | (knightMaskTemp2 >> 16 | knightMaskTemp2 << 16)
        
        
maskDict = dict()

maskDict[WHITE | PAWN]  = pawnMaskWhite
maskDict[BLACK | PAWN]  = pawnMaskBlack

for colour in colourArray:
    maskDict[colour | ROOK]     = rookMask
    maskDict[colour | BISHOP]   = bishopMask
    maskDict[colour | QUEEN]    = queenMask
    maskDict[colour | KING]     = kingMask
    maskDict[colour | KNIGHT]   = knightMask

lineDict            = dict()   
for colour in colourArray: 
    lineDict[BISHOP + colour]    = bishopLines
    lineDict[ROOK + colour]      = rookLines
    lineDict[QUEEN + colour]     = queenLines

pawnMoveDict = dict()
pawnMoveDict[WHITE] = pawnMoveWhite
pawnMoveDict[BLACK] = pawnMoveBlack

def shiftLineToPos(line, x, y):
    return ((line >> x) & 0b11111111) << y*8       
        
def getCaptureMask(piece, pos):
    pieceDict = maskDict[piece]
    return pieceDict[pos]

def getCaptureLines(piece, pos):
    return lineDict[piece][pos]
  
def getMoveMask(piece,pos):
    pieceType = piece & ~0b11
    colour = piece & 0b11
    if pieceType == PAWN:
        return pawnMoveDict[colour][pos]
    else:
        return getCaptureMask(piece,pos)
    
    
    
pawnDoubleMoveWhite = dict()
pawnDoubleMoveBlack = dict()   

dpBase = 0b10000000_10000000
for i in range(0,8):
    pawnDoubleMoveBlack[i,1] = (dpBase << 8*2)  >> i
    pawnDoubleMoveWhite[i,6] = (dpBase << 8*4)  >> i 
    
doublePawn = {BLACK: pawnDoubleMoveBlack, WHITE: pawnDoubleMoveWhite}

def getDoubleStepPawnMask(colour, pos):
    return doublePawn[colour][pos]

doublePawnRow = {BLACK: 1, WHITE: 6}

def canDoubleStepPawn(colour, pos):
    return doublePawnRow[colour] == pos[1]