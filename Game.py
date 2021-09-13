from copy import deepcopy
from tkinter import *
from Solver import SudukoSolver
import time
import threading

# Represent the game state of a Suduko game
class Game:

    # init a game
    def __init__(self, window):
        self.solver = SudukoSolver(self)
        self.rows = 9
        self.cols = 9
        self.moves = 0

        self.window = window
        self.window.title("Daniel's Suduko Solver")
        self.window.geometry('500x500')
        gridFrame = Frame(self.window, bg='blue')
        buttonFrame = Frame(self.window) #, bg='green')

        self.board = []
        self.possibles = []
        self.debug = 0
        self.guess_stack = []
        self.longest_stack = 0

        # Create the grid UI
        self.uiCells = []
        self.uiCellValues = []
        font = ('Arial', 24)
        for row in range(self.rows):
            uiRow = []
            uiRowValues = []
            for col in range(self.cols):
                if (row < 3 or row > 5) and (col < 3 or col > 5):
                    color = 'gray'
                elif row in [3, 4, 5] and col in [3, 4, 5]:
                    color = 'gray'
                else:
                    color = 'white'
                var = StringVar()
                uiRowValues.append(var)
                lbl = Label(gridFrame, bg=color, width=2, font=font, borderwidth=1, relief="groove", textvariable=var)
                uiRow.append(lbl)
                lbl.grid(column=col, row=row)
            self.uiCells.append(uiRow)
            self.uiCellValues.append(uiRowValues)

        # Create the game controls
        gridFrame.pack(expand=True)
        self.fastMode = 0
        self.fastModeBox = IntVar()
        Checkbutton(window, text='Fast UI?', command=self.setSpeed, variable=self.fastModeBox, onvalue=1, offvalue=0).pack()
        Button(buttonFrame, text="Start Solver", command=self.startGame).pack()
        self.status = StringVar()
        self.statusLbl = Button(buttonFrame, textvariable=self.status, borderwidth=2)
        self.statusLbl.pack()
        buttonFrame.pack() #expand=True)

        self.setGame()
        self.showBoardUI()
        self.determinePossibles()
        self.window.mainloop()

    def setSpeed(self):
        self.fastMode = self.fastModeBox.get() == 1

    # create data for the game and setup possible cell values
    def setGame(self):
        if True:
            #https://punemirror.indiatimes.com/pune/cover-story/worlds-toughest-sudoku-is-here-can-you-crack-it/articleshow/32299679.cms
            self.board.append([1,0,5,3,0,0,0,0,0])
            self.board.append([8,0,0,0,0,0,0,2,0])
            self.board.append([0,7,0,0,1,0,5,0,0])

            self.board.append([4,0,0,0,0,5,3,0,0])
            self.board.append([0,1,0,0,7,0,0,0,6])
            self.board.append([0,0,3,2,0,0,0,8,0,])

            self.board.append([0,6,0,5,0,0,0,0,9])
            self.board.append([0,0,4,0,0,0,0,3,0])
            self.board.append([0,0,0,0,0,9,7,0,0])
        else:
            self.board.append([6, 7, 2, 0, 0, 8, 0, 0, 1])
            self.board.append([8, 3, 0, 0, 0, 5, 6, 0, 0])
            self.board.append([0, 4, 0, 6, 3, 0, 8, 0, 7])

            self.board.append([0, 2, 0, 0, 1, 6, 0, 0, 4])
            self.board.append([0, 0, 0, 4, 9, 0, 1, 8, 0])
            self.board.append([0, 1, 5, 3, 8, 0, 0, 0, 2])

            self.board.append([0, 0, 7, 0, 0, 0, 0, 0, 6])
            self.board.append([3, 0, 6, 0, 5, 0, 0, 1, 8])
            self.board.append([0, 0, 0, 0, 0, 9, 7, 5, 3])

        for row in range(self.rows):
            self.possibles.append([])
            for col in range(self.cols):
                if self.board[row][col] == 0:
                    self.possibles[row].append([1,2,3,4,5,6,7,8,9])
                else:
                    self.possibles[row].append([])

    # Start the solver in a thread so the UI updates
    def startGame(self):
        threading.Thread(target=self.solveGame).start()

    # Solve the game and try new exploratory moves if we hit a dead end
    def solveGame(self):
        tries = 0
        guesses = 0
        while not self.allDone():
            hits = False
            if self.solver.solve() > 0:
                hits = True
                tries += 1
                self.status.set("Moves: "+str(tries))
            if self.allDone():
                print('SOLVED')
            else:
                if (not hits):
                    if self.guessMove():
                        guesses += 1
                    else:
                        print('========> GIVE UP')
                        break
        msg = 'SOLVED Moves:'+str(self.moves) + ', exploratory moves:' + str(guesses) +  ', deepest exploratory stack:' + str(self.longest_stack)
        print(msg)
        self.status.set(msg)

    # Show the board in the UI
    def showBoardUI(self):
        for row in range(self.rows):
            for col in range(self.cols):
                val = self.board[row][col]
                if val > 0:
                    self.uiCellValues[row][col].set(val)

    # Determine which values are possible for cell given its row, column and black
    def determinePossibles(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] == 0:
                    self.possibles[row][col] = [1,2,3,4,5,6,7,8,9]
                    # check in row
                    for c in range(self.cols):
                        if not c == col:
                            boardVal = self.board[row][c]
                            if boardVal != 0 and boardVal in self.possibles[row][col]:
                                self.possibles[row][col].remove(boardVal)
                    # check in col
                    for r in range(self.cols):
                        if not r == row:
                            boardVal = self.board[r][col]
                            if boardVal != 0 and boardVal in self.possibles[row][col]:
                                self.possibles[row][col].remove(boardVal)
                    # check in box
                    firstRow = int((row / 3)) * 3
                    firstCol = int((col / 3)) * 3
                    for r in range(3):
                        for c in range(3):
                            r1 = firstRow + r
                            c1 = firstCol + c
                            if not (r1 == row and c1 == col):
                                boardVal = self.board[r1][c1]
                                if boardVal != 0 and boardVal in self.possibles[row][col]:
                                    self.possibles[row][col].remove(boardVal)
                else:
                    self.possibles[row][col] = []

    # Set a value in a board cell
    def setBoard(self, row, col, val):
        self.board[row][col] = val
        self.possibles[row][col] = []
        self.uiCellValues[row][col].set(str(val))
        self.determinePossibles()
        self.moves += 1
        if not self.fastMode:
            time.sleep(0.12)

    # Logic cannot determine the cells value so now guess the value and see if the game can complete
    def guessMove(self):
        min = 1000
        minRC = None
        for row in range(self.rows):
            for col in range(self.cols):
                l = len(self.possibles[row][col])
                if l > 0 and l < min:
                    min = l
                    minRC = (row, col, self.possibles[row][col])

        if minRC is None: #have taken a wrong guess somewhere - board is invalid
            while len(self.guess_stack) > 0:
                last = len(self.guess_stack) - 1
                stackEntry = self.guess_stack[last]
                options = stackEntry[2]
                newBoard = stackEntry[3]
                self.board = deepcopy(newBoard)
                if len(options) > 0:
                    guess_val = options[0]
                    self.setBoard(stackEntry[0], stackEntry[1], guess_val)
                    del self.guess_stack[last][2][0]
                    #print('--- Guess pop:', stack_entry[:3], ' stack size:', len(self.guess_stack), ' board setto:', guess_val)
                    return True
                else:
                    del self.guess_stack[last]
            return False
        else:
            options = minRC[2]
            option = options[0]
            boardSaved = deepcopy(self.board)
            self.setBoard(minRC[0], minRC[1], option)
            del options[0]
            stackEntry = (minRC[0], minRC[1], options, boardSaved)
            self.guess_stack.append(stackEntry)
            print ('--- Guess push:', stackEntry[:3], ' stack size:', len(self.guess_stack),  ' board setto:', option)
            if len(self.guess_stack) > self.longest_stack:
                self.longest_stack = len(self.guess_stack)
            return True

    # Determine if game solved
    def allDone(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] == 0:
                    return False
        return True

    # Show the Suduko board
    def showBoard(self, msg):
        line = '----------------------'
        print ("--", msg)
        for r in range(self.rows):
            if r % 3 == 0:
                print (line)
            for c in range(self.cols):
                val = self.board[r][c]
                if c%3 == 0:
                    print('|', end='')
                if val == 0:
                    val = ' '
                print (val,  end =" ")
            print('|')
        print (line)

