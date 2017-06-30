import PodSixNet.Channel
import PodSixNet.Server
from time import sleep,time
class ClientChannel(PodSixNet.Channel.Channel):
	def Network(self, data):
		print data
		
	def Network_snakeMove(self, data):
	    #deconsolidate all of the data from the dictionary
	    #player number (1 or 2)
		player=data["player"]
	    #id of game given by server at start of game
		self.gameid = data["gameid"]
	    #tells server
		self._server.snakeMove(data, self.gameid, player)
		
	def Network_eatFood(self, data):
		player=data["player"]
		self.gameid = data["gameid"]
		food=data["food"]
		self._server.eatFood(food, data, self.gameid, player)
		
	def Network_playerLose(self, data):
		player=data["player"]
		self.gameid = data["gameid"]
		self._server.playerLose(data, self.gameid, player)
		
	def Network_foodAck(self, data):
		player=data["player"]
		self.gameid = data["gameid"]
		food = data["food"]
		self._server.foodAck(food, data, self.gameid, player)
 
class SnakeServer(PodSixNet.Server.Server):
	def __init__(self, *args, **kwargs):
	    PodSixNet.Server.Server.__init__(self, *args, **kwargs)
	    self.games = []
	    self.queue = None
	    self.currentIndex=0

	channelClass = ClientChannel
 
	def Connected(self, channel, addr):
		print 'new connection:', channel
		if self.queue==None:
		    self.currentIndex+=1
		    channel.gameid=self.currentIndex
		    self.queue=Game(channel, self.currentIndex)
		else:
		    channel.gameid=self.currentIndex
		    self.queue.player2=channel
		    timeRand = time() 
		    self.queue.player1.Send({"action": "startgame","player":1, "timeRand":timeRand, "gameid": self.queue.gameid})
		    self.queue.player2.Send({"action": "startgame","player":2, "timeRand":timeRand, "gameid": self.queue.gameid})
		    self.games.append(self.queue)
		    self.queue=None

	def snakeMove(self, data, gameid, player):
	 	game = [a for a in self.games if a.gameid==gameid]
    		if len(game)==1:
        		game[0].snakeMove(data, player)
				
	def eatFood(self, food, data, gameid, player):
	 	game = [a for a in self.games if a.gameid==gameid]
    		if len(game)==1:
        		game[0].eatFood(food, data, player)
				
	def playerLose(self, data, gameid, player):
	 	game = [a for a in self.games if a.gameid==gameid]
    		if len(game)==1:
        		game[0].playerLose(data, player)
				
	def foodAck(self, food, data, gameid, player):
	 	game = [a for a in self.games if a.gameid==gameid]
    		if len(game)==1:
        		game[0].foodAck(food, data, player)

class Game:
	def __init__(self, player1, currentIndex):
		#initialize the players including the one who started the game
		self.player1=player1
		self.player2=None
		self.foodList = [[True, True],[True, True]]
		#gameid of game
		self.gameid=currentIndex
			
	def snakeMove(self, data, player):
		if player == 2:
			self.player1.Send(data)
		else:
			self.player2.Send(data)
		
	def eatFood(self, food, data, player):
		print "entrei food: ", player, food
		if (self.foodList[player-1][food-1] == True):
			if player == 2:
				self.foodList[0][food-1]=False
			else:
				self.foodList[1][food-1]=False
			print "Food eaten"
			self.player1.Send(data)
			self.player2.Send(data)

	def playerLose(self, data, player):
		if player == 2:
			self.player1.Send(data)
		else:
			self.player2.Send(data)
			
	def foodAck(self, food, data, player):
		self.foodList[player-1][food-1] = True
			
print "STARTING SERVER"
snakeServer=SnakeServer(localaddr=("192.168.1.2",5000))
while True:
    snakeServer.Pump()
    sleep(0.002)	
