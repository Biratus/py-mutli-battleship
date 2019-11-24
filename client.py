import requests
import json
from math import *
from tkinter import *
import lobby
import game

api_url = 'http://localhost:8082'

size = 600
gridSize = 500
cellNb = 10
cellSize = gridSize/cellNb
opponent = None
ready = False
lobby = lobby.Lobby()
battle = None
drawInterval = None

def cellFromMouseClick(event):
	return (floor(event.x/cellSize),floor(event.y/cellSize))

def onclick(event):
	global battle
	if not(battle): return
	cell = cellFromMouseClick(event)
	if cell[0]>=cellNb or cell[1]>=cellNb: return
	requests.post(api_url+'/touch',data=json.dumps({'x':cell[0],'y':cell[1]}),headers=headers())
	drawCanvasBattle()

# def drawCanvasBattle():
# 	global ready
# 	canvas.delete("all")
# 	drawGrid()
	# if not(ready):
	# 	txt = canvas.create_text(510,20,text='I am Ready'+' '+opt,anchor='w')
	# 	canvas.tag_bind(txt,'<Button-1>',ready) 
	
	# grid = requests.get(api_url+'/grid',headers=headers()).json()['grid']
	# for cell in grid:
	# 	if not(ready):
	# 		canvas.create_rectangle(b[0]*cellSize,b[1]*cellSize,(b[0]+1)*cellSize,(b[1]+1)*cellSize,fill='#eeeeee')
	# 	else:
	# 		if cell[2] == name: canvas.create_rectangle(cell[0]*cellSize,cell[1]*cellSize,(cell[0]+1)*cellSize,(cell[1]+1)*cellSize,fill='#00ffbe')
	# 		else: canvas.create_rectangle(cell[0]*cellSize,cell[1]*cellSize,(cell[0]+1)*cellSize,(cell[1]+1)*cellSize,fill='#ff00be')
	# canvas.after(50,drawCanvasBattle)

def readyPlayer(event):
	req = requests.post(api_url+'/ready',headers=headers())
	if req.status_code == 200:
		battle.readyClient(getPlayers)

# def placeBoat(event):
# 	cell = cellFromMouseClick(event)
# 	boats.append(cell)
def getGrid():
	return requests.get(api_url+'/grid',headers=headers()).json()
def drawCanvasBattle():
	canvas.delete("all")
	canvas.create_text(gridSize+20,20,text='En combat avec '+battle.p2.name,anchor='w')
	grid = getGrid()
	print(f'{grid}')
	if not(battle.bothReady):
		ready = canvas.create_text(gridSize+20,50,text='=> Prêt! ',anchor='w')
		canvas.tag_bind(ready,'<Button-1>',readyPlayer)
	elif grid.get('turn'):
		canvas.create_text(gridSize+20,50,text='=> A '+grid.get('turn')+' de jouer !',anchor='w')
	battle.drawGrid(grid['grid'],canvas,gridSize,cellNb)
def getPlayers():
	return requests.get(api_url+'/players',headers=headers()).json()['players']
def drawCanvasLobby():
	global drawInterval
	players = getPlayers()
	for p in players:
		if p.get('requestAccepted'):
			initGame(p.get('name'))
			return
	lobby.setPlayers(players)
	canvas.delete("all")
	canvas.create_text(size/2,20,text='Interface de '+name,anchor='center')
	lobby.draw(canvas,sendPlayerRequest)
	drawInterval = canvas.after(50,drawCanvasLobby)

def initGame(opp):
	global battle
	canvas.bind('<Button-1>', onclick)
	canvas.after_cancel(drawInterval)
	battle = game.Game(name,opp)
	drawCanvasBattle()

def sendPlayerRequest(evt,player):
	accept = requests.post(api_url+'/request',data=json.dumps({'name':player.name}),headers=headers()).json()['accept']
	if accept:
		initGame(player.name)

def headers():
	head = {
		'Content-Type': 'application/json',
		'User-Agent': 'fuck',
		'Accept': 'application/json',
		'clientName' : name
	}
	if battle:
		head['opponent']=battle.p2.name
	return  head

print("Enter your name here:")
name = input()
res = requests.post(api_url+'/join',headers=headers())
if(res.status_code == 200): 
	print(f'Joined successfully')
else: print('There was a problem connection to the server')

window = Tk()
window.title("Battleship")
window.resizable(0,0)
canvas = Canvas(window,width=size,height=size,bd=0,highlightthickness=0)
canvas.pack()

drawCanvasLobby()

window.mainloop()
