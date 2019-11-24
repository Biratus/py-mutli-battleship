class Lobby:
    players = {}

    requests = {}

    # Server

    def join(self, name):
        self.players[name] = Player(name)

    # return accepted or not
    def request(self, fromP, toP):
        if not(fromP) or not(toP): pass
        accept = bool(self.requests.get(toP.name) and fromP.name in self.requests.get(toP.name))
        if not(self.requests.get(fromP.name)):
            self.requests[fromP.name] = []
        self.requests[fromP.name].append(toP.name)
        return accept

    def getPlayers(self,forPlayer = None):
        ps = []
        for pName in self.players:
            if pName == forPlayer: continue
            p = self.players.get(pName)
            forAskTo = self.requests.get(forPlayer) and pName in self.requests.get(forPlayer)
            toAskFor = self.requests.get(pName) and forPlayer in self.requests.get(pName)
            if forAskTo and toAskFor:
                p.requestAccepted = True
            elif forAskTo:
                p.requestSend = True
            elif toAskFor:
                p.requestNeed = True
            ps.append(p)
        return ps

    def fromName(self, pName):
        return self.players.get(pName)

    #   Client
    def setPlayers(self, players):
        for p in players:
            self.players[p.get('name')] = Player(p.get('name'),p.get('requestSend'), p.get('requestNeed'))
    # return state button to send request

    def draw(self, canvas,actionMethod):
        y = 100
        # print(f'{len(self.players)} players')
        for pName in self.players:
            p = self.players.get(pName)
            opt = '=> Demander à jouer'
            fill = 'black'
            if p.requestSend:
                fill = '#0a7ddb'
                opt = 'Requète envoyé..'
            elif p.requestNeed:
                fill = '#20c528'
                opt = '=> Joue maintenant!'
            canvas.create_text(50, y, text=p.name, anchor='w')
            state = canvas.create_text(50, y+10, text=opt, fill=fill, anchor='w')
            
            def action(evt, player = p):
                return actionMethod(evt, player)
            canvas.tag_bind(state, '<Button-1>', action)
            y += 30
            return state

class Player:
    def __init__(self, name, requestSend = False, requestNeed = False,requestAccepted = False):
        self.name=name

        # Server
        # Client
        self.requestSend=requestSend
        self.requestNeed=requestNeed
        self.requestAccepted = requestAccepted
