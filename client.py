import requests
import json
from math import *
from tkinter import *

api_url = 'http://localhost:8082'

size = 600
gridSize = 500
cellNb = 10
cellSize = gridSize/cellNb
opponent = None
inGame = False
ready = False

def cellFromMouseClick(event):
	return (floor(event.x/cellSize),floor(event.y/cellSize))

def onclick(event):
	cell = cellFromMouseClick(event)
	requests.post(api_url+'/touch',data=json.dumps({'cell':{'x':cell[0],'y':cell[1]}}),headers=headers())

def drawCanvasBattle():
	global ready
	canvas.delete("all")
	drawGrid()
	if not(ready):
		txt = canvas.create_text(510,20,text='I am Ready'+' '+opt,anchor='w')
		canvas.tag_bind(txt,'<Button-1>',ready) 
	
	grid = requests.get(api_url+'/grid',headers=headers()).json()['grid']
	for cell in grid:
		if not(ready):
			canvas.create_rectangle(b[0]*cellSize,b[1]*cellSize,(b[0]+1)*cellSize,(b[1]+1)*cellSize,fill='#eeeeee')
		else:
			if cell[2] == name: canvas.create_rectangle(cell[0]*cellSize,cell[1]*cellSize,(cell[0]+1)*cellSize,(cell[1]+1)*cellSize,fill='#00ffbe')
			else: canvas.create_rectangle(cell[0]*cellSize,cell[1]*cellSize,(cell[0]+1)*cellSize,(cell[1]+1)*cellSize,fill='#ff00be')
	canvas.after(50,drawCanvasBattle)

def ready():
	global ready
	requests.post(api_url+'/ready',headers=headers());
	ready = True

def placeBoat(event):
	cell = cellFromMouseClick(event)
	boats.append(cell)

# def drawCanvasBattle():
# 	canvas.delete("all")
# 	drawGrid()
# 	grid = requests.get(api_url+'/grid',data=json.dumps({'opponent':opponent}),headers=headers()).json()['grid']
# 	for cell in grid:
# 		if cell[2] == name: canvas.create_rectangle(cell[0]*cellSize,cell[1]*cellSize,(cell[0]+1)*cellSize,(cell[1]+1)*cellSize,fill='#00ffbe')
# 		else: canvas.create_rectangle(cell[0]*cellSize,cell[1]*cellSize,(cell[0]+1)*cellSize,(cell[1]+1)*cellSize,fill='#ff00be')
# 	canvas.after(50,drawCanvasBattle)

def drawCanvasLobby():
	global inGame
	if inGame: 
		drawCanvasBattle()
		return
	canvas.delete("all")
	players = requests.get(api_url+'/players',headers=headers()).json()['players']
	canvas.create_text(size/2,20,text='Interface de '+name,anchor='center')
	y = 100
	for p in players:
		if p.get('name')==name: continue
		opt = ''
		if p.get('requestSend'): opt = 'requête envoyé'
		elif p.get('requestNeed'): opt = 'requête demandé'
		elif p.get('inGame'): 
			inGame = True
			opponent = p.get('name')
		txt = canvas.create_text(50,y,text=p.get('name')+' '+opt,anchor='w')
		def send(evt, player=p):
			return sendPlayerRequest(evt,player)
		canvas.tag_bind(txt,'<Button-1>',send)
		y+=30
	canvas.after(50,drawCanvasLobby)

def sendPlayerRequest(evt,player):
	if player.get('requestNeed'): 
		requests.post(api_url+'/accept',data=json.dumps({'name':player.get('name')}),headers=headers())
		inGame = True
		opponent = player.get('name')
	else: requests.post(api_url+'/request',data=json.dumps({'name':player.get('name')}),headers=headers())

def drawGrid():
	for x in range(0,cellNb):
		dX = x*cellSize
		canvas.create_line(0,dX,size,dX)
		canvas.create_line(dX,0,dX,size)


def headers():
	return  {
		'Content-Type': 'application/json',
		'User-Agent': 'fuck',
		'Accept': 'application/json',
		'clientName' : name
	}

print("Enter your name here:")
name = input()
res = requests.post(api_url+'/join',headers=headers())
if(res.status_code == 200): 
	print(f'Joined successfully')
else: print('There was a problem connection to the server')

window = Tk()
window.title("Chat Session")
window.resizable(0,0)
canvas = Canvas(window,width=size,height=size,bd=0,highlightthickness=0)
canvas.pack()

drawCanvasLobby()

window.mainloop()
