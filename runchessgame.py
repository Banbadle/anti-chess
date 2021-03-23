import chess
import chessbot
import tkinter as tk
from PIL import ImageTk, Image
from playsound import playsound

SQUARESIZE = 100
boardColour = {0: "#769656", 1: "#eeeed2"}


root = tk.Tk()
root.title("Anti-Chess")
root.resizable(False, False)

canv = tk.Canvas(root)

# Initialises dictionary of images
pieceImages = dict()
for piece in chess.pieceArray:
    for colour in chess.colourArray:
        img = Image.open("images/" + str(piece+colour) + ".png").resize((SQUARESIZE, SQUARESIZE))
        pieceImages[piece+colour] = ImageTk.PhotoImage(img)

# Draws a plain checkerboard
def drawBlankBoard(root):
    
    canvas = tk.Canvas(root, width=8 * SQUARESIZE, height=8 * SQUARESIZE)
    for i in range(0,8):
        for j in range(0,8):
            resetSquare(canvas, (i,j))

    canvas.pack()
    
    return canvas

# Resets the colour of the square at pos, and redraws piece (if given)
def resetSquare(canvas, pos, piece=None):
    i,j = pos
    
    colour = boardColour[(i+j) % 2]
    canvas.create_rectangle(*rectAt(i,j), fill=colour, outline="")
    
    if piece != None:
        drawPiece(canvas, piece, pos)
            
# Returns a tuple which, when unpacked, gives rectangle corner co-ordinates 
# for use in tk.Canvas().create_rectangle
def rectAt(x,y):
    return (x*SQUARESIZE, y*SQUARESIZE, (x+1)*SQUARESIZE, (y+1)*SQUARESIZE)

def drawPiece(canvas, piece, pos):
    x,y = pos
    if piece != chess.NONE:
        canvas.create_image(100*x, 100*y, anchor=tk.NW, image=pieceImages[piece])

# Highlights the square at pos
def selectSquare(canvas, piece, pos):
    x,y = pos
    canvas.create_rectangle(*rectAt(x,y), fill="#CCCC00",  outline="")
    drawPiece(canvas, piece, pos)
    
# moves piece from fromPos to toPos on the canvas and gamestate
def movePiece(gamestate, canvas, piece, fromPos, toPos):

    gamestate.movePiece(piece, fromPos, toPos)

    for pos in [fromPos, toPos]:
        resetSquare(canvas, pos)

    drawPiece(canvas, piece, toPos)

# Draws a board representation of gamestate onto canvas
def drawGamestate(canvas, gamestate):
    for i in range(0,8):
        for j in range(0,8):
            piece = gamestate.getPiece((i,j))
            drawPiece(canvas, piece, (i,j))

lastPos = None
lastPiece = None
playerColour = chess.WHITE


def touchPiece(event):
    global canvas
    global lastPos
    global lastPiece
    global gamestate
    global playerColour

    print(lastPos)
    
    nextPos = (event.x // 100, event.y // 100)

    nextPiece = gamestate.getPiece(nextPos)

    pieceColour = nextPiece & 0b11
    pieceType   = nextPiece - pieceColour

    
    # If no piece is selected
    if lastPos == None:
        if pieceType in chess.pieceSet and pieceColour == playerColour:
            selectSquare(canvas, nextPiece, nextPos)
            lastPos = nextPos
            lastPiece = nextPiece

    else:
        # If Legal move is attempted
        if gamestate.isLegalMove(lastPiece, lastPos, nextPos):
            
            movePiece(gamestate, canvas, lastPiece, lastPos, nextPos)
            x,y = nextPos
            
            if chess.getPieceType(lastPiece) == chess.PAWN and y in [0,7]:
                
                # Give Choice of piece from chess.promotePieces via UI element
                # Promote to Queen for now
                promotePieceType = chess.QUEEN
                
                lastColour = chess.getColour(lastPiece)
                gamestate.promotePiece(lastColour, promotePieceType, nextPos)
                resetSquare(canvas, nextPos, promotePieceType + lastColour)
                
            lastPos = None
            lastPiece = None
            
            playerColour = chess.invColour(playerColour)
            
        # If Illegal move is attempted
        else:
            resetSquare(canvas, lastPos, lastPiece)
            
            lastPos = None
            lastPiece = None
            
            newPiece = gamestate.getPiece(nextPos)
            
            if pieceType in chess.pieceSet and pieceColour == playerColour:
                selectSquare(canvas, nextPiece, nextPos)
                lastPos = nextPos
                lastPiece = nextPiece

canvas = drawBlankBoard(root)
canvas.bind("<Button-1>", touchPiece)

gamestate = chess.Gamestate()
gamestate.default()
drawGamestate(canvas, gamestate)

root.mainloop()