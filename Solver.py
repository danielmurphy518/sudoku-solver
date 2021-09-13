# Solve a Suduko board
class SudukoSolver():
    def __init__(self, game):
        self.game = game

    # Apply the Suduko rules fpr column, row and block
    def solve(self):
        hits = 0
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                if self.game.board[row][col] == 0:
                    for pos in self.game.possibles[row][col]:
                        uniqueInRow = True
                        for c in range(self.game.cols):
                            if c != col:
                                if pos in self.game.possibles[row][c]:
                                    uniqueInRow = False
                        uniqueInCol = True
                        for r in range(self.game.rows):
                            if r != row:
                                if pos in self.game.possibles[r][col]:
                                    uniqueInCol = False

                        # check in box
                        uniqueInBox = True
                        firstRow = int((row / 3)) * 3
                        firstCol = int((col / 3)) * 3
                        for r in range(3):
                            for c in range(3):
                                r1 = firstRow + r
                                c1 = firstCol + c
                                if not (r1==row and c1==col):
                                    if pos in self.game.possibles[r1][c1]:
                                        uniqueInBox = False

                        if uniqueInRow or uniqueInCol or uniqueInBox:
                            self.game.setBoard(row, col, pos)
                            hits += 1
        return hits
