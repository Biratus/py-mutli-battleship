from http.server import *
import json
import lobby
import game

client_id = 0


class BattleshipHandler(BaseHTTPRequestHandler):
    battles = {}
    lobby = lobby.Lobby()

    def htmlThis(self, htmlBody):
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

    def returnHtml(self, htmlStr):
        self.wfile.write(bytes(htmlStr.encode(encoding='utf-8')))

    def do_GET(self):
        path = self.path
        if path == '/grid':
            self.sendGridState()
        elif path == '/players':
            self.sendPlayerList()

    def do_POST(self):
        path = self.path
        self.ok()
        if path == '/join':
            self.lobby.join(self.headers['clientName'])
        elif path == '/request':
            response = self.data()
            fromP = self.player()
            toP = self.player(response.get('name'))
            accept = self.lobby.request(fromP, toP)
            if accept:
                self.battles[(fromP.name, toP.name)] = game.Game(fromP.name, toP.name)
            self.wfile.write(json.dumps({'accept': accept}).encode(encoding='utf-8'))
        elif path == '/touch':
            cell = self.data()
            battle = self.getGame()
            battle.touch(cell,self.headers['clientName'])
        elif path == '/ready':
            battle = self.getGame()
            battle.readyServer(self.headers['clientName'])

    def player(self, name=None):
        if name == None:
            name = self.headers['clientName']
        return self.lobby.fromName(name)

    def ok(self):
        self.send_response(200)
        self.end_headers()

    def sendGridState(self):
        battle = self.getGame()
        # for t in self.battles:
        # 	if (t[0]==name or t[1]==name) && (!self.battles[t].p1.ready or !self.battles[t].p2.ready): content = {}
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(battle.getGridState(self.headers['clientName'])).encode(encoding='utf-8'))
    
    def getGame(self):
        p1 = self.headers['clientName']
        p2 = self.headers['opponent']
        p1p2 = self.battles.get((p1, p2))
        p2p1 = self.battles.get((p2, p1))
        if p1p2:
            return p1p2
        if p2p1:
            return p2p1
        return None

    def sendPlayerList(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        g = self.getGame()
        if g:
            self.wfile.write(json.dumps({'players': jsonPlayers(self.getGame().getPlayers())}).encode(encoding='utf-8'))
        else:
            self.wfile.write(json.dumps({'players': jsonPlayers(self.lobby.getPlayers(self.headers['clientName']))}).encode(encoding='utf-8'))
    
    def data(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        return json.loads(post_data)



def jsonPlayers(players):
    return list(map(lambda p: p.__dict__, players))

class Game:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2


port = 8082
print('Listening on localhost:%s' % port)
server = HTTPServer(('', port), BattleshipHandler)
server.serve_forever()
