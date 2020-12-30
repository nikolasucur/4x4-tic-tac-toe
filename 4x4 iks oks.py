import math
import random
from sys import exit
from collections import defaultdict
import pygame
from pygame.locals import *


# Framerate Constant (relativno nepotrebno, ali da pokazem da znam)
FPS = 15

# Vrednosti za bota i igraca
computer = 1
human = 2


   
# vrednosti ya terminal za biranje tezine
easy = 6
medium = 7
hard = 8 


empty = 0
O = 3  
X = 4

# Boje
black = (0, 0, 0)
white = (255, 255, 255)
red = (200, 0, 0)
blue = (0, 0, 200)


# Klase za igrace
class Player:
    # Inicijacija
    def __init__(self, type, symbol, name):
        self.type = type  # type of player
        self.symbol = symbol  # X or O
        self.name = name  # name
        

    # Tabla
    def SetBoard(self, board):
        self.board = board

    
    def GetMove(self):
        pass

    # ocitavanje klika
    def MouseClick(self, cell):
        pass

    # oponentov simbol
    def OppositeSign(self, symbol):
        if symbol == O:
            return X
        return O


# Klasa za Igraca
class HumanPlayer(Player):
    # inicijacija igraca
    def __init__(self, symbol, name):
        super().__init__(human, symbol, name)  # call Player constructor
        self.lastmove = -1

    # cekanje klika misa da bude odradjeno
    def GetMove(self):
        if(self.lastmove != -1):
            move = self.lastmove
            self.lastmove = -1
            return move

    # postavlja simbol na obelezeno mesto 
    def MouseClick(self, cell):
        if cell not in self.board.moves:  # proverava da li je to mesto vec popunjeno
            self.lastmove = cell


# klasa za bota
class ComputerPlayer(Player):
    # inicijacija bota
    def __init__(self, symbol, name, difficulty=hard):
        super().__init__(computer, symbol, name)  # call Player contructor
        self.lastmove = -1
        self.maxnodes = difficulty
      
        self.cutoff = False  
        
        self.currnodes = 0  
        self.maxprune = 0  
        self.minprune = 0  
        self.turn = 0


    # sledeci na potezu
    def GetMove(self):
        possiblemoves = [mv for mv in self.board.possiblecells if mv not in
        self.board.moves]  

        
        if len(possiblemoves) == 16:
            self.turn += 1
            print("Static Optimized First Move.")
            return (0, 0)

        if len(possiblemoves) == 14 and (0, 1) in possiblemoves:
            self.turn += 1
            print("Static Optimized Second Move.")
            return (0, 1)
        elif len(possiblemoves) == 14:
            self.turn += 1
            print("Static Optimized Second Move.")
            return (0, 2)

        self.loop = 0  

        
        self.cutoff = False  
        maxdepth = 0  
        self.currnodes = 0  
        self.maxprune = 0  
        self.minprune = 0  

     
        self.turn += 1

        val, move, maxdepth = self.MaxValue(-1000, 1000)  
       
        print("\nTurn", self.turn)
        if self.cutoff:
            print("Cutoff Reached")
        print("Maximum depth:", maxdepth)
        print("Number of nodes generated:", self.currnodes + 1)
        print("Number of max prunings:", self.maxprune)
        print("Number of min prunings:", self.minprune)
        return move

    
    def GetScore(self):
        if self.board.Draw():
            return 0  # draw
        elif self.board.GetWinner() == self.symbol:
            return 1  # computer win
        return -1  # player win

   
    def MaxValue(self, alpha, beta, height=0):
        self.currnodes += 1
        height += 1
        depth = height
        maxpos = None
        maxval = -1000  

        for move in self.board.getFreePositions():
            self.loop += 1 
            self.board.Move(move, self.symbol)  

            if self.currnodes >= self.maxnodes:
                self.cutoff = True
                playerlines1 = 0
                playerlines2 = 0
                playerlines3 = 0
                opponentlines1 = 0
                opponentlines2 = 0
                opponentlines3 = 0
                for line in self.board.alllines:
                    p1, p2, p3, p4 = line
                    val = self.board.board[p1] + self.board.board[p2] + self.board.board[p3] + self.board.board[p4]
                    val2 = self.board.board[p1] + self.board.board[p2] + self.board.board[p3] + self.board.board[p4]
                    for i in range(3):
                        if val == self.symbol * 3:
                            playerlines3 += 1
                            break
                        if val == self.symbol * 2:
                            playerlines2 += 1
                            break
                        if val == self.symbol:
                            playerlines1 += 1
                            break
                        val -= self.OppositeSign(self.symbol)

                    for i in range(3):
                        if val2 == self.OppositeSign(self.symbol) * 3:
                            opponentlines3 += 1
                            break
                        if val2 == self.OppositeSign(self.symbol) * 2:
                            opponentlines2 += 1
                            break
                        if val2 == self.OppositeSign(self.symbol):
                            opponentlines1 += 1
                            break
                        val2 -= self.symbol

                v = 6 * playerlines3 + 3 * playerlines2 + playerlines1\
                  - (6 * opponentlines3 + 3 * opponentlines2 + opponentlines1)
            else:
                if self.board.GameOver():  
                    v = self.GetScore() 
                else:  
                    v, movepos, depth = self.MinValue(alpha, beta, height)  

            self.board.UndoMove() 

            if v >= beta:
                return v, move, depth
            if v > alpha:
                alpha = v  

            if v > maxval:
                maxval = v  
                maxpos = move  

            if v == 1:
                self.maxprune += 1
                break
        return maxval, maxpos, depth

    
    def MinValue(self, alpha, beta, height=0):
        height += 1
        depth = height
        minpos = None
        minval = 1000  

        for move in self.board.getFreePositions():
            self.loop += 1  
            self.board.Move(move, self.OppositeSign(self.symbol))  

            if self.board.GameOver():  
                v = self.GetScore()  
            else:
                v, movepos, depth = self.MaxValue(alpha, beta, height) 

            self.board.UndoMove()  

            if v < alpha:
                return v, move, depth
            if v < beta:
                beta = v 

            if v < minval:
                minval = v 
                minpos = move  
            if v == -1:
                self.minprune += 1
                break

        return minval, minpos, depth


# interfejs
class BackEndBoard:
    # all cell tuples
    possiblecells = [(a, b) for a in range(0, 4) for b in range(0, 4)]
    # sve direktne linije/moguce pobede
    alllines = [[(a, b) for a in range(0, 4)] for b in range(0, 4)] +\
               [[(b, a) for a in range(0, 4)] for b in range(0, 4)] +\
               [[(0, 0), (1, 1), (2, 2), (3, 3)],
               [(0, 3), (1, 2), (2, 1), (3, 0)]]

    # inicijacij
    def __init__(self):
        self.moves = []  
        self.gameover = False 
        self.draw = False  
        self.board = defaultdict(lambda: empty)  

   
    def getFreePositions(self):
        return [x for x in self.possiblecells if x not in self.moves]

    def Move(self, position, symbol):
        if self.board[position] != empty:
            return False  
        self.board[position] = symbol 
        self.moves.append(position)  
        self.CheckGameOver()  
        return True  

    
    def UndoMove(self):
        if len(self.moves) == 0:
            return False  
        self.board[self.moves.pop()] = empty  
        self.gameover = False  
    def GameOver(self):
        return self.gameover 

    def Draw(self):
        return self.draw #Izbacuje neresen rezultat

    # izbacuje pobednika
    def GetWinner(self):
        if self.GameOver() and not self.Draw():
            return self.winner  # pobednik

    # proverava da li je kraj partije
    def CheckGameOver(self):
        for line in self.alllines:
            p1, p2, p3, p4 = line  
            if self.board[p1] != empty and\
               self.board[p1] == self.board[p2]\
               == self.board[p3] == self.board[p4]:
                self.gameover = True  # true if equal
                self.winner = self.board[p1]  # set winner
                self.draw = False  # deny draw
                break
        else:
            if len(self.moves) == 16:
                self.draw = True  # draw if all moves made
                self.gameover = True  # end game
            else:
                self.gameover = False  # do not end


# Izgled table(volim minimalisticke)
class FrontBoard:
    # boje su ranije definisane
    gridcolor = black
    colorO = red
    colorX = blue

    # frontend
    def __init__(self, boardsize=500):
        self.players = [] 
        self.boardsize = boardsize  
        self.gameboard = BackEndBoard()  
        self.font = pygame.font.Font(None, 50)  

    # resets and clears board
    def reset(self):
        self.gameboard = BackEndBoard()  
        for player in self.players:
            player.SetBoard(self.gameboard)  
        self.player1, self.player2 = self.player2, self.player1  

    # print winner/loser
    def printstatus(self, screen):
        textstr = ''  # output string
        if game.gameboard.GameOver():
            if game.gameboard.Draw():
                textstr = "Draw."
            else:
                textstr = self.player1.name + " wins."
        else:
            textstr = self.player1.name + "'s turn"
        text = self.font.render(textstr, 1, black)  # render settings
        textpos = text.get_rect(centerx=screen.get_width() / 2,
                  y=self.boardsize - 5)  # text position
        screen.blit(text, textpos)  # text to screen

   
    def AddPlayer(self, player):
        player.SetBoard(self.gameboard)  # set players board
        self.players.append(player)  # player list
        if(len(self.players) > 1):
            self.player1 = self.players[0]  # individual setting
            self.player2 = self.players[1]  # individual setting

    # actuall board drawing
    def draw(self, screen):
        tolerance = 20  # limit edges before edge of screen

        # drawing each line of the grid
        pygame.draw.line(screen, self.gridcolor,
                        (self.boardsize / 4, tolerance),
                        (self.boardsize / 4, self.boardsize - tolerance), 10)
        pygame.draw.line(screen, self.gridcolor,
                        ((2 * self.boardsize) / 4, tolerance),
                        ((2 * self.boardsize) / 4,
                        self.boardsize - tolerance), 10)
        pygame.draw.line(screen, self.gridcolor,
                        ((3 * self.boardsize) / 4, tolerance),
                        ((3 * self.boardsize) / 4,
                        self.boardsize - tolerance), 10)
        pygame.draw.line(screen, self.gridcolor,
                        (tolerance, (self.boardsize) / 4),
                        (self.boardsize - tolerance,
                        (self.boardsize) / 4), 10)
        pygame.draw.line(screen, self.gridcolor,
                        (tolerance, (2 * self.boardsize) / 4),
                        (self.boardsize - tolerance,
                        (2 * self.boardsize) / 4), 10)
        pygame.draw.line(screen, self.gridcolor,
                        (tolerance, (3 * self.boardsize) / 4),
                        (self.boardsize - tolerance,
                        (3 * self.boardsize) / 4), 10)

        # draw each X or O
        for move in self.gameboard.moves:
            mx, my = move  # move x and y coordinates
            quarter = int(self.boardsize / 4)  # 1/4 of board size

            if self.gameboard.board[move] == O:
                # draw a O in that position
                pos = mx * quarter + int(quarter / 2), my * quarter +\
                      int(quarter / 2)
                pygame.draw.circle(screen, self.colorO, pos,
                                   int(quarter / 4) + 10, 8)
            elif self.gameboard.board[move] == X:
                # draw an X in that position
                tl = mx * quarter + int(quarter / 5), my * quarter +\
                     int(quarter / 5)

                tr = (mx + 1) * quarter - int(quarter / 5),\
                     my * quarter + int(quarter / 5)

                bl = mx * quarter + int(quarter / 5),\
                     (my + 1) * quarter - int(quarter / 5)

                br = (mx + 1) * quarter - int(quarter / 5),\
                     (my + 1) * quarter - int(quarter / 5)

                pygame.draw.line(screen, self.colorX, tl, br, 10)
                pygame.draw.line(screen, self.colorX, tr, bl, 10)

    # find the position of the mouse click
    def MouseClick(self, position):
        mx, my = position  # x and y coordinates
        if my < self.boardsize:  # if on board
            quarter = int(self.boardsize / 4)
            cx = int(math.floor(mx / quarter))
            cy = int(math.floor(my / quarter))
            cell = cx, cy  # convert to cell coordinates
            self.player1.MouseClick(cell)  # pass to player
        elif self.gameboard.GameOver():
            self.reset()  # reset board

    # update board screen
    def update(self):
        if not self.gameboard.GameOver():
            nextpos = self.player1.GetMove()
            if nextpos is not None:
                # place players symbol
                self.gameboard.Move(nextpos, self.player1.symbol)
                if not self.gameboard.GameOver():
                    # switch players for next turn
                    self.player1, self.player2 = self.player2, self.player1


# main function
if(__name__ == "__main__"):
    difficulty = input("Please select difficulty (easy, medium, hard): ").lower()
    first = random.randint(1,2)
    if first == 1 :
        print("human will go first.")

    if first == 2:
        print("computer will go first.")
    pygame.init()  # initialization required by module
    boardsize = 500  # board size
    # screen display
    screen = pygame.display.set_mode((boardsize, boardsize + 35))
    pygame.display.set_caption('iks oks 4x4')  # toolbar name
    gameover = False  # gameover starts false
    clock = pygame.time.Clock()  # clock for FPS
    game = FrontBoard()  # creation of board

    if difficulty == "hard":
        if first == 1:
            game.AddPlayer(HumanPlayer(O, "Player"))  # player 1
            game.AddPlayer(ComputerPlayer(X, "Computer", hard))  # player 2
        else:
            game.AddPlayer(ComputerPlayer(X, "Computer", hard))  # player 1
            game.AddPlayer(HumanPlayer(O, "Player"))  # player 2
    elif difficulty == "medium":
        if first == 1:
            game.AddPlayer(HumanPlayer(O, "Player"))  # player 1
            game.AddPlayer(ComputerPlayer(X, "Computer", medium))  # player 2
        else:
            game.AddPlayer(ComputerPlayer(X, "Computer", medium))  # player 1
            game.AddPlayer(HumanPlayer(O, "Player"))  # player 2
    elif difficulty == "easy":
        if first == 1:
            game.AddPlayer(HumanPlayer(O, "Player"))  # player 1
            game.AddPlayer(ComputerPlayer(X, "Computer", easy))  # player 2
        else:
            game.AddPlayer(ComputerPlayer(X, "Computer", easy))  # player 1
            game.AddPlayer(HumanPlayer(O, "Player"))  # player 2
    else:
        if first == 1:
            game.AddPlayer(HumanPlayer(O, "Player"))  # player 1
            game.AddPlayer(ComputerPlayer(X, "Computer"))  # player 2
        else:
            game.AddPlayer(ComputerPlayer(X, "Computer"))  # player 1
            game.AddPlayer(HumanPlayer(O, "Player"))  # player 2
    while not gameover:
        clock.tick(FPS)  # frame settings
        screen.fill(white)  # screen background
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONUP:
                game.MouseClick(event.pos)  # mouse click event

        game.update()  # update game
        game.draw(screen)  # update display
        game.printstatus(screen)  # print prompt
        pygame.display.update()  # render display update
