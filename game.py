import time
class Game:
    bothReady = False
    def __init__(self,p1,p2):
        self.p1=Player(p1)
        self.p2=Player(p2)
        self.grid={}

    def touch(self,cell,pName):
        gridCell = self.grid.get((cell.get('x'),cell.get('y')))
        if not(gridCell): gridCell={}
        if self.bothReady: #playing
            print('!TOUCH!')
            return 
        elif self.p1.name==pName: #p1 touch
            if not(self.p1.ready): #placing
                gridCell['placed'+pName] = not(gridCell.get('placed'+pName))  
            else: gridCell['ready'+pName] = True
        elif self.p2.name==pName: #p2 touch
            if not(self.p2.ready): #placing
                gridCell['placed'+pName] = not(gridCell.get('placed'+pName))
            else: gridCell['ready'+pName] = True
        self.grid[(cell.get('x'),cell.get('y'))] = gridCell
    
    def getGridState(self,pName):
        for coord in self.grid:
            for state in cell_states:
                self.grid[coord]['state'] = ''
                if self.grid[coord].get(state+pName): 
                    self.grid[coord]['state'] = state
        jsonGrid = {}
        for key in self.grid:
            jsonGrid[str(key)]=self.grid.get(key)
        if self.bothReady:
            return {'grid':jsonGrid,'turn':(self.p2.name,self.p1.name)[self.p1.active]}
        else:
            return {'grid':jsonGrid}
    
    def drawGrid(self,grid,canvas,gridSize,cellNb):
        global cell_states
        cellSize = gridSize/cellNb
        print(f'{grid}')
        for x in range(0,cellNb+1):
            dX = x*cellSize
            canvas.create_line(0,dX,gridSize,dX)
            canvas.create_line(dX,0,dX,gridSize)
        for cStr in grid:
            c = tupleFromStr(cStr)
            color = cell_states.get(grid.get(cStr).get('state'))
            canvas.create_rectangle(c[0]*cellSize,c[1]*cellSize,(c[0]+1)*cellSize,(c[1]+1)*cellSize,fill=color)
        
    def readyClient(self,getPlayers):
        self.p1.ready = True
        c = 100
        while c > 0:
            c-=1
            time.sleep(1)
            players = getPlayers()
            for p in players:
                if p.get('name') == self.p2.name and p.get('ready'):#all good
                    return
        return 
    def readyServer(self,pName):
        if self.p1.name == pName: self.p1.ready = True
        elif self.p2.name == pName: self.p2.ready = True
        self.bothReady = self.p1.ready and self.p2.ready
        if self.bothReady:
            self.p1.active = True


class Player:
    ready = False
    active = False
    def __init__(self,name):
        self.name = name


cell_states = {
    'placed':'#b3b3cc',
    'ready':'#4d4d33',
    'missed':'#a3c2c2',
    'touched':'#ffa64d',
    'sunk':'#ff1a25'
}

def tupleFromStr(str):
    str = str.replace('(','')
    str = str.replace(')','')
    t = tuple(list(map(lambda i : int(i),str.split(', '))))
    return t