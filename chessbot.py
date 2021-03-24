import chess
import random


def getRandomMove(gs):
    
    colour      = gs.getTurnPlayer()
    legalMoves  = gs.getLegalMoveList(colour)
    
    randMove    = random.choice(legalMoves)
    
    return randMove

def forceCapture(gs):
    pass