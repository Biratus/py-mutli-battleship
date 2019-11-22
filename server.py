from http.server import *
import json

client_id = 0

class BattleshipHandler(BaseHTTPRequestHandler):
	players = {}
	grid = []

	requests = {}

	games = {}

	def htmlThis(self,htmlBody):
		return """<!DOCTYPE html>
			<head>
				<meta charset="utf-8"></meta>
				<title>BLOUBLOU</title>
			</head>
			<body>
			"""+htmlBody+"""
			</body>
			</html>
		"""

	def returnHtml(self,htmlStr):
		self.wfile.write(bytes(htmlStr.encode(encoding='utf-8')))

	def do_GET(self):
		print(f'clientName: {self.headers["clientName"]}')
		path = self.path 	
		if path == '/grid':
			self.sendGridState()
		elif path == '/players':
			self.sendPlayerList()

	def do_POST(self):
		print(f'clientName: {self.headers["clientName"]}')
		path = self.path
		if path == '/join' : 
			self.join()
			pass
		elif path == '/request':
			response = data(self)
			player = None
			for p in self.players:
				if p == response.get('name'):
					player = self.players[p]
					break
			self.requests[self.headers['clientName']]=player.name
			self.send_response(200)
			self.end_headers()
		elif path == '/accept':
			response = data(self)
			player = None
			acceptor = None
			for p in self.players:
				if p == response.get('name'):
					player = self.players[p]
				elif p == self.headers['clientName']:
					acceptor = self.players[p]
			self.requests.pop(player.name)
			self.games[(acceptor.name,player.name)] = Game(acceptor,player)
			self.send_response(200)
			self.end_headers()
		elif path=='/ready':
			self.players[self.headers['clientName']].ready=True
			self.send_response(200)
			self.end_headers()
		elif path=='/touch':
			response = data(self)
			p = self.players[self.headers['clientName']]
			if not(p.ready):
				p.boats.append(response.cell)



	def join(self):
		name = self.headers['clientName']
		print(f'{name} is joining')
		self.players[name] = Player(name)
		self.send_response(200)
		self.send_header('Content-type','application/json')
		self.end_headers()

	def sendGridState(self):
		name = self.headers['clientName']
		player = self.players[name]
		content = {} #display grid
		if not(player.ready):
			content = player.boats
		# for t in self.games:
		# 	if (t[0]==name or t[1]==name) && (!self.games[t].p1.ready or !self.games[t].p2.ready): content = {}

		self.send_response(200)
		self.send_header('Content-type','application/json')
		self.end_headers()
		self.wfile.write(json.dumps(content).encode(encoding='utf-8'))

	def sendPlayerList(self):
		self.send_response(200)
		self.send_header('Content-type','application/json')
		self.end_headers()
		playerList = []
		for pName in self.players:
			p = self.players[pName]
			playerList.append({
				'name':p.name,
				'requestSend': self.requests.get(self.headers['clientName']) == p.name,
				'requestNeed': self.requests.get(p.name) == self.headers['clientName'],
				'requestAccepted': self.games.get((p.name,self.headers['clientName'])) or self.games.get((self.headers['clientName'],p.name))
			})

		self.wfile.write(json.dumps({'players':playerList}).encode(encoding='utf-8'))


def data(http):
	content_length = int(http.headers['Content-Length'])
	post_data = http.rfile.read(content_length)
	return json.loads(post_data)

class Player:
	boats=[]
	def __init__(self,name):
		self.name=name

class Game:
	def __init__(self,p1,p2):
		self.p1=p1
		self.p2=p2
		


port = 8082
print('Listening on localhost:%s' % port)
server = HTTPServer(('', port), BattleshipHandler)
server.serve_forever()	