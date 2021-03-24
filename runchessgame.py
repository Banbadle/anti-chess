import chess
import chessbot
import tkinter as tk
import time
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
def drawBlankBoard(canvas):

    for i in range(0,8):
        for j in range(0,8):
            resetSquare(canvas, (i,j))

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
    move = chess.Move(piece, fromPos, toPos)
    gamestate.makeMove(move)

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

def touchPiece(event):
    global canvas
    global lastPos
    global lastPiece
    global gamestate
    
    playerColour = gamestate.getTurnPlayer()

    print(lastPos)
    
    nextPos = (event.x // 100, event.y // 100)
    
    if 0<= nextPos[0] <= 7 and 0 <= nextPos[1] <= 8:
    
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
                
                root.update()
                
                root.after(1000, botResponse())
                
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
                    
def resetGame(event):
    global canvas
    global gamestate
    
    drawBlankBoard(canvas)
    gamestate.default()
    drawGamestate(canvas, gamestate)
    
def randomMove(event):
    global canvas
    global gamestate
    
    move = chessbot.getRandomMove(gamestate)
    movePiece(gamestate, canvas, *move.unpack())
    
    
def setBotRandom(event):
    global aiMode
    aiMode = "Random"
    
def setBotOff(event):
    global aiMode
    aiMode = "Off"
    
aiMode = "Off"
    
def botResponse():
    
    if aiMode == "Off":
        return
    
    if aiMode == "Random":
        randomMove(None)

canvas = tk.Canvas(root, width=8 * SQUARESIZE, height=8 * SQUARESIZE)        
canvas.pack(side=tk.LEFT)
drawBlankBoard(canvas)
canvas.bind("<Button-1>", touchPiece)

gamestate = chess.Gamestate()
gamestate.default()
drawGamestate(canvas, gamestate)

buttonFrame = tk.Frame(root, width = 200, height = 800)
buttonFrame.pack(side=tk.LEFT)

resetButton = tk.Button(buttonFrame, text="Reset", fg="Black", height=2, width = 16)
resetButton.bind("<Button-1>", resetGame)
resetButton.pack(side=tk.BOTTOM, padx=8, pady=8)

resetButton = tk.Button(buttonFrame, text="AI Random", fg="Black", height=2, width = 16)
resetButton.bind("<Button-1>", setBotRandom)
resetButton.pack(side=tk.TOP, padx=8, pady=8)

resetButton = tk.Button(buttonFrame, text="AI Off", fg="Black", height=2, width = 16)
resetButton.bind("<Button-1>", setBotOff)
resetButton.pack(side=tk.TOP, padx=8, pady=8)

root.mainloop()