"""Sudoku Solver, by Richard Ngo
Solves sudoku using deduction and informed trial and error.
Input and output in GUI window."""

class square:
    #represents one square on sudoku grid.
    #stores all possibilities and value, if found
    def __init__(self):
        self.poss = {1,2,3,4,5,6,7,8,9}
        self.value = 0
        self.size = 9
        self.x = None
        self.y = None

    def setPoint(self,i,j):
        self.x = i
        self.y = j

    def setValue(self,val):
        self.poss = {val}
        self.value = val
        self.size = 1

    def copy(self):
        new = square()
        new.poss = set()
        for item in list(self.poss):
            new.poss.add(item)
        new.value = self.value
        new.size = self.size
        new.x = self.x
        new.y = self.y
        return new

    def getAPoss(self):
        if self.poss:
            return min(self.poss)
        else:
            return None

    def __str__(self):
        return str(self.value)
    
class queue:
    #quick queue implementation for waitlist
    #note: can't store multiple copies of same item
    def __init__(self):
        self.body = dict()
        self.body["head"] = None
        self.tail = None

    def enq(self, val):
        if val not in self.body:
            if self.tail:
                self.body[self.tail] = val
                self.tail = val
            else:
                self.body["head"] = val
                self.tail = val
            self.body[val] = None

    def deq(self):
        val = self.body["head"]
        if val != None:
            self.body["head"] = self.body[val]
            del self.body[val]
            if self.tail == val:
                self.tail = None
        return val

    def clear(self):
        self.body.clear()
        self.body["head"] = None
        self.tail = None

    def __str__(self):
        string = ""
        val = self.body["head"]
        while val != None:
            string = string + str(val) + ", "
            val = self.body[val]
        if len(string) >= 2:
            return string[:-2]
        else:
            return string
    
class sudoku:
    #main class for sudoku object
    def __init__(self,values=None):
        self.board = []
        self.solveable = True
        for i in range(9):
            row = []
            for j in range(9):
                sq = square()
                sq.setPoint(j,i)
                row.append(sq)
            self.board.append(row)
        if values != None:
            self.initialise(values)

    def initialise(self, values):
        #initialises values to input. Also initialises any squares
        #for which only one possibility remains. If a contradiction
        #is found, records that the input is unsolveable
        global changelog;
        changelog = [{}] #irrelevant during initialisation
        for x in range(9):
            for y in range(9):
                val = values[y][x]
                if val != 0:
                    if val in self.getPoss(x,y):
                        self.setValue(x,y,val)
                    else:
                        self.solveable = False
        changelog = [{}] #reset to remove initial values

    def __str__(self):
        count = 0
        s = " -----------------------------" + "\n"
        for row in self.board:
            s = s + "| "
            for sq in row:
                count += 1
                s = s + str(sq)
                if count %3 == 0:
                    s = s + " | "
                else:
                    s = s + "  "
            s = s[:-1] + "\n"
            if count % 27 == 0:
                s = s + " -----------------------------" + "\n"
        return s

    def getValue(self,x,y):
        return self.board[y][x].value
    
    def getSize(self,x,y):
        return self.board[y][x].size

    def getPoss(self,x,y):
        return self.board[y][x].poss

    def getAPoss(self,x,y):
        return self.board[y][x].getAPoss()

    def getRow(self,y):
        row = set()
        for i in range(9):
            row.add((i,y))
        return row

    def getCol(self,x):
        col = set()
        for i in range(9):
            col.add((x,i))
        return col

    def getBox(self,x,y):
        box = set()
        for i in range((x//3)*3, (((x+3)//3)*3)):
            for j in range((y//3)*3, (((y+3)//3)*3)):
                box.add((i,j))
        return box

    def setValue(self,x,y,val):
        self.board[y][x].setValue(val)
        
    def getASquare(self):
        #finds first square whose value hasn't yet been set
        x = 0
        y = 0
        while x < 9 and y < 9:
            if self.getValue(x,y) == 0:
                return (x,y)
            else:
                x += 1
                if x == 9:
                    y+=1
                    x=0
        return None

    def setValue(self,x,y,val):
        #Sets the value of a first square, then also all other
        #squares whose value is uniquely determined after first change
        #(these stored in waitlist temporarily). If a contradiction
        #is found, then sets flag to true and finishes.
        #Also records original state of changed squares in changelog
        global flag
        global waitlist
        global changelog            
        if (x,y) not in changelog[-1]:
            changelog[-1][(x,y)] = self.board[y][x].copy()
        self.board[y][x].value = val
        self.board[y][x].poss = {val}
        self.board[y][x].size = 1
        self.updateOn(x,y)
        nxt = waitlist.deq()
        if nxt: #if there are any squares with values waiting to be set
            nxtval = self.getAPoss(nxt[0],nxt[1])
            if not nxtval: #if that square has lost its last possibility
                           #since being put on the waitlist
                flag = True
            if flag:
                waitlist.clear()
            else:
                self.setValue(nxt[0],nxt[1],nxtval)

    def updateOn(self,x,y):
        #Calls remPoss on all squares affected by a value assignment at (x,y).
        world = (self.getRow(y) | self.getCol(x) | self.getBox(x,y))
        world.remove((x,y))
        val = self.getValue(x,y)
        for (i,j) in world:
            self.remPoss(i,j,val)

    def remPoss(self,x,y,val):
        #Removes a particular value from the possibilities of a square.
        #If this would leave the square with no options, raises flag.
        #If this leaves a square with exactly one option, enqueues it.
        #Records original state of changed squares in changelog.
        global flag
        global waitlist
        global changelog
        
        if val == self.getValue(x,y): #i.e. repeated number in one row/col/box
            flag = True
        elif val in self.getPoss(x,y): #if still a possibility, remove it
            if (x,y) not in changelog[-1]:
                changelog[-1][(x,y)] = self.board[y][x].copy()
            self.board[y][x].size -= 1
            self.board[y][x].poss.remove(val)
            if self.getSize(x,y) == 1:
                waitlist.enq((x,y))

    def solve(self):
        #While free squares exist, uses trial and error to give them values.
        #When a flag is raised, reverts to state before last guess and calls
        #remPoss on the value which caused the problem (stored in testlog).
        #Stops after approx. 30 seconds, to prevent a search of all possible
        #boards for unsolveable sudokus.
        global flag
        global waitlist
        global changelog
        testlog = []
        if self.solveable == False:
            return False
        count = 0
        nxtsq = self.getASquare()
        while nxtsq: #if there is still a square empty
            flag = False
            waitlist.clear()
            nxtval = self.getAPoss(nxtsq[0],nxtsq[1])
            if nxtval:
                newdic = dict()
                changelog.append(newdic) #adds a new entry to changelog
                                         #to store changes after this guess
                testlog.append((nxtsq[0],nxtsq[1],nxtval))                    
                self.setValue(nxtsq[0],nxtsq[1],nxtval)
            else:
                flag = True
            if flag:
                for key, value in changelog.pop().items():
                    self.board[key[1]][key[0]] = value
                if not changelog: #if all guesses have lead to contradictions
                    self.solveable = False
                    return False
                #next square processed is square with last wrong guess
                try:
                    (testX,testY,testVal) = testlog.pop()
                    self.remPoss(testX,testY,testVal)
                    nxtsq = (testX,testY)
                except(IndexError):
                    return False
            else: #guess works (so far), so go onto next free square
                nxtsq = self.getASquare() 
            count += 1
            if count == 30000:
                return False
        return True

def solveClick():
    #Runs when "solve" button is clicked. Reads numbers input so far,
    #creates a new sudoku object, solves it, and writes solution to screen.
    #If sudoku is unsolveable, opens dialog box saying so.
    board = []
    for i in range(9):
        row = []
        for j in range(9):
            num = entries[j][i].get()
            if num=="":
                num = 0
            else:
                num = int(num)
            row.append(num)
        board.append(row)
    sudo = sudoku(board)
    result = sudo.solve()
    if result == True:
        for i in range(9):
            for j in range(9):
                entries[j][i].delete(0,'end')
                string = str(sudo.getValue(j,i))
                if string=="0":
                    string=""
                entries[j][i].insert(0,string)
    else: #notification if sudoku is unsolveable
        toplevel = Toplevel()
        label1 = Label(toplevel, text="This sudoku is unsolveable", height=0, width=30)
        label1.pack()
        okbutton = Button(toplevel, text="Okay",command=toplevel.destroy)
        okbutton.pack()

def resetClick():
    #deletes all numbers in window (whether input by user or part of solution)
    for i in range(9):
        for j in range(9):
            entries[j][i].delete(0,'end')

#Here the GUI is set up and necessary global variables initialised
from tkinter import *
root = Tk()
root.title("Sudoku Solver")
root.geometry("414x445")

flag = False
changelog = [{}]
waitlist = queue()

frame = Frame(root)
frame.grid()
entries = []
for i in range(9):
    entries.append([])
    for j in range(9):
        entries[i].append( Entry(frame, width=2, justify=CENTER, font = "Helvetica 28"))
        entries[i][j].grid(row=j, column=i)
solveButton = Button(frame, width=3, text = "Solve", command=solveClick)
solveButton.grid(row=9, column=3)
resetButton = Button(frame, width=3, text = "Reset", command = resetClick)
resetButton.grid(row=9, column=5)

root.mainloop()
