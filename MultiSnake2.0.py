import pygame
from pygame.locals import *
import random
from PodSixNet.Connection import ConnectionListener, connection
from time import sleep

# ---------- constants ---------- #
SCREENSIZE = (800, 600)
SCREENRECT = pygame.Rect(0, 0, SCREENSIZE[0], SCREENSIZE[1])
CAPTION = 'MultiSnake'
FPS = 80

START_TILE1 = (20, 20) #snake 1 spawn
START_TILE2 = (59, 39)
START_SEGMENTS = 7     #starting snake size

MOVE_RATE = 2
DIFFICULTY_INCREASE_RATE = 0
MOVE_THRESHOLD = 10 # when moverate counts up to this the snake moves

TILE_SIZE = (10, 10) #the resolution is divided in blocks of 10x10 pixels
TILE_RECT = pygame.Rect(0, 0, TILE_SIZE[0], TILE_SIZE[1])

SCREENTILES = ((SCREENSIZE[0] / TILE_SIZE[0]) - 1, (SCREENSIZE[1] / TILE_SIZE[1]) - 1)

SNAKE_HEAD_RADIUS = 5
SNAKE_SEGMENT_RADIUS = 4
FOOD_RADIUS = 4

#colors
BACKGROUND_COLOR = (255, 255, 255)
SNAKE_HEAD_COLOR = (0, 0, 150)
SNAKE_SEGMENT_COLOR = (0, 0, 255)
SNAKE_HEAD_COLOR2 = (0, 150, 0)
SNAKE_SEGMENT_COLOR2 = (0, 255, 0)
FOOD_COLOR = (255, 0, 0)
COLORKEY_COLOR = (255, 255, 0)

SCORE_COLOR = (0, 0, 0)
SCORE_POS1 = (20, 20)
SCORE_PREFIX1 = 'Player 1: '
SCORE_POS2 = (740, 20)
SCORE_PREFIX2 = 'Player 2: '

MOVE_VECTORS = {'left' : (-1, 0),
		'right' : (1, 0),
		'up' : (0, -1),
		'down' : (0, 1)
		}
MOVE_VECTORS_PIXELS = { 'left' : (-TILE_SIZE[0], 0),
			'right' : (TILE_SIZE[0], 0),
			'up' : (0, -TILE_SIZE[1]),
			'down' : (0, TILE_SIZE[1])
		    }


# ----------- game objects ----------- #
class snake_segment(pygame.sprite.Sprite):
	def __init__(self, tilepos, segment_groups, color = SNAKE_SEGMENT_COLOR, radius = SNAKE_SEGMENT_RADIUS):
		pygame.sprite.Sprite.__init__(self)
		self.image = self.image = pygame.Surface(TILE_SIZE).convert()
		self.image.fill(COLORKEY_COLOR)
		self.image.set_colorkey(COLORKEY_COLOR)
		pygame.draw.circle(self.image, color, TILE_RECT.center, radius)
		
		self.tilepos = tilepos
		
		self.rect = self.image.get_rect()
		self.rect.topleft = (tilepos[0] * TILE_SIZE[0], tilepos[1] * TILE_SIZE[1])
		
		self.segment_groups = segment_groups
		for group in segment_groups:
			group.add(self)
		
		self.behind_segment = None
		self.tileposxAll= list()
		self.tileposyAll= list()
		self.movedir = 'left'
		
	def add_segment(self,color = SNAKE_SEGMENT_COLOR):
		seg = self
		#while not the last segment
		while True:
			if seg.behind_segment == None:
				x = seg.tilepos[0]
				y = seg.tilepos[1]
				if seg.movedir == 'left':
					x += 1
				elif seg.movedir == 'right':
					x -= 1
				elif seg.movedir == 'up':
					y += 1
				elif seg.movedir == 'down':
					y -= 1
				seg.behind_segment = snake_segment((x, y), seg.segment_groups,color)
				seg.behind_segment.movedir = seg.movedir
				break
			else:
				seg = seg.behind_segment
	
	def update(self):
		pass
	
	def move(self):
		self.tilepos = (self.tilepos[0] + MOVE_VECTORS[self.movedir][0], self.tilepos[1] + MOVE_VECTORS[self.movedir][1])
		self.rect.move_ip(MOVE_VECTORS_PIXELS[self.movedir])
		if self.behind_segment != None:
			self.behind_segment.move()
			self.behind_segment.movedir = self.movedir
			
	def return_tileposx(self):
		seg=self
		self.tileposxAll= list()
		self.tileposyAll= list()
		while seg.behind_segment != None:
			self.tileposxAll.append(seg.tilepos[0])
			self.tileposyAll.append(seg.tilepos[1])
			seg=seg.behind_segment
		self.tileposxAll.append(seg.tilepos[0])
		self.tileposyAll.append(seg.tilepos[1])
		tileposxAllList=self.tileposxAll
		return tileposxAllList
			
	def return_tileposy(self):
		tileposyAllList=self.tileposyAll
		return tileposyAllList	

class snake_head(snake_segment):
	def __init__(self, tilepos, movedir, segment_groups, color_choice = SNAKE_HEAD_COLOR):
		snake_segment.__init__(self, tilepos, segment_groups, color_choice, radius = SNAKE_HEAD_RADIUS)
		self.movedir = movedir
		self.movecount = 0
		self.move_rate = MOVE_RATE
		self.score = 0

	def update(self):
		self.movecount += self.move_rate
		if self.movecount > MOVE_THRESHOLD:
			self.move()
			self.movecount = 0
			
	def receive_tilepos(self, tileposxAll,tileposyAll, allOrHead = True):
		seg=self
		if (allOrHead == True):
			counter=0
			while seg.behind_segment != None:
				seg.tilepos=(tileposxAll[counter],tileposyAll[counter])
				counter = counter + 1
				seg=seg.behind_segment
		else:
			seg.tilepos=(tileposxAll,tileposyAll)

class food(pygame.sprite.Sprite):
	def __init__(self, takenupgroup):
		pygame.sprite.Sprite.__init__(self)
		self.image = self.image = pygame.Surface(TILE_SIZE).convert()
		self.image.fill(COLORKEY_COLOR)
		self.image.set_colorkey(COLORKEY_COLOR)
		pygame.draw.circle(self.image, FOOD_COLOR, TILE_RECT.center, FOOD_RADIUS)
		
		self.rect = self.image.get_rect()
		while True:
			self.rect.topleft = (random.randint(0, SCREENTILES[0]) * TILE_SIZE[0], random.randint(0, SCREENTILES[1]) * TILE_SIZE[1])
			for sprt in takenupgroup:
				if self.rect.colliderect(sprt):
					continue # collision, food cant go here
			break # no collision, food can go here

#function to test collision, collision between snakes not implemented yet
def SnakeCollision(client, snake, snakeheadgroup, snakegroup, foodgroup, foodgroup2, currentfood, currentfood2):
	lose = False
	pos = snake.rect.topleft
	if pos[0] < 0:
		lose = True
	if pos[0] >= SCREENSIZE[0]:
		lose = True
	if pos[1] < 0:
		lose = True
	if pos[1] >= SCREENSIZE[1]:
		lose = True
	# collisions
	# head -> tail
	col = pygame.sprite.groupcollide(snakeheadgroup, snakegroup, False, False)
	for head in col:
		for tail in col[head]:
			if not tail is snake:
				lose = True
	# head -> food1
	col = pygame.sprite.groupcollide(snakeheadgroup, foodgroup, False, True)
	for head in col:
		for tail in col[head]:
			currentfood = False
			client.Send({"action": "eatFood", "food": 1, "movement": snake.movedir, "posx": snake.return_tileposx(), "posy": snake.return_tileposy(), "player":client.player, "gameid": client.gameid})

	# head -> food2
	col = pygame.sprite.groupcollide(snakeheadgroup, foodgroup2, False, True)
	for head in col:
		for tail in col[head]:
			currentfood2 = False
			client.Send({"action": "eatFood", "food": 2, "movement": snake.movedir, "posx": snake.return_tileposx(), "posy": snake.return_tileposy(), "fps":client.localfps, "player":client.player, "gameid": client.gameid})
	
	if lose:
		client.Send({"action": "playerLose", "player":client.player, "gameid": client.gameid})
	return lose,currentfood,currentfood2


class GameClient(ConnectionListener):
	def __init__(self):
		self.Connect(("192.168.1.2",5000))
		self.player=0
		self.running=False
		self.newMove=False
		self.foodEaten=False
		self.playerLose=False
		self.localfps=0
		self.clientfps=0
		
	def Loop(self):
		self.Pump()
		connection.Pump()

	def Network_connected(self, data):
		print "connected to the server"
	
	def Network_error(self, data):
		print "error:", data['error'][1]
	
	def Network_disconnected(self, data):
		print "disconnected from the server"

	def Network_startgame(self, data):
	    self.running=True
	    self.player=data["player"]
	    self.gameid=data["gameid"]
	    self.timeRand=data["timeRand"]
	
	def Network_snakeMove(self, data):
		self.movement = data["movement"]
		self.player_mov = data["player"]
		self.posx = data["posx"]
		self.posy = data["posy"]
		self.clientfps = data["fps"]
		self.newMove=True
		
	def Network_eatFood(self, data):
		print "network eatFood"
		self.movement = data["movement"]
		self.player_mov = data["player"]
		self.posx = data["posx"]
		self.posy = data["posy"]
		self.food = data["food"]
		self.clientfps = data["fps"]
		self.newMove=True
		self.foodEaten=True
		
	def Network_playerLose(self, data):
		print "Player Lose"
		self.playerLose=True
	# -------------- game logic ------------ #
def main():
	pygame.init()
	screen = pygame.display.set_mode(SCREENSIZE)
	pygame.display.set_caption(CAPTION)
	bg = pygame.Surface(SCREENSIZE).convert()
	bg.fill(BACKGROUND_COLOR)
	screen.blit(bg, (0, 0))
	
	#create sprite groups
	snakegroup = pygame.sprite.Group()
	snakeheadgroup = pygame.sprite.Group()
	snakegroup2 = pygame.sprite.Group()
	snakeheadgroup2 = pygame.sprite.Group()
	foodgroup = pygame.sprite.Group()
	foodgroup2 = pygame.sprite.Group()
	takenupgroup = pygame.sprite.Group()
	all = pygame.sprite.RenderUpdates()
	
	#create snakes
	snake = snake_head(START_TILE1, 'right', [snakegroup, all, takenupgroup])
	snakeheadgroup.add(snake)

	snake2 = snake_head(START_TILE2, 'left', [snakegroup2, all, takenupgroup],SNAKE_HEAD_COLOR2)
	snakeheadgroup2.add(snake2)

	#add starting segments
	for index in range(START_SEGMENTS):
		snake.add_segment(SNAKE_SEGMENT_COLOR)
		snake2.add_segment(SNAKE_SEGMENT_COLOR2)
		
	global DIFFICULTY_INCREASE_RATE

	currentfood= False
	currentfood2= False
	player1Lose = False
	player2Lose = False
	
	client=GameClient()
	client.Loop()
	f = pygame.font.Font(None, 80)
	connectmessage = f.render("Connecting...", True, (0, 0, 0))
	connectrect = connectmessage.get_rect()
	connectrect.center = SCREENRECT.center
	screen.blit(connectmessage, connectrect)
	pygame.display.flip()
	# mainloop
	quit = False
	firstRun = True
	clock = pygame.time.Clock()
	while not quit:
		# quit or key pressed
		if client.player==1:
			currentmovedir = snake.movedir
			currentsnake = snake
			currentsnakeheadgroup = snakeheadgroup
			currentsnakegroup = snakegroup
			posx = snake.tilepos[0]
			posy = snake.tilepos[1]
		else:
			currentmovedir = snake2.movedir
			currentsnake= snake2
			currentsnakeheadgroup = snakeheadgroup2
			currentsnakegroup = snakegroup2
			posx = snake2.tilepos[0]
			posy = snake2.tilepos[1]
			
		for event in pygame.event.get():
			if event.type == QUIT:
				quit = True
			elif event.type == KEYDOWN and client.running:
				if event.key == K_UP:
					tomove = 'up'
					dontmove = 'down'
				elif event.key == K_DOWN:
					tomove = 'down'
					dontmove = 'up'
				elif event.key == K_LEFT:
					tomove = 'left'
					dontmove = 'right'
				elif event.key == K_RIGHT:
					tomove = 'right'
					dontmove = 'left'
				if not currentmovedir == dontmove:
					client.Send({"action": "snakeMove","movement": tomove, "posx": posx, "posy": posy, "fps":client.localfps,  "player":client.player, "gameid": client.gameid})
					currentsnake.movedir= tomove
		client.Loop()

		# clearing
		all.clear(screen, bg)
		
		# updates
		if client.newMove:
			print "New move"
			if (client.foodEaten == True and (client.player_mov != client.player)):
				print "food eaten"
				if (client.food==1):
					currentfood.kill()
					currentfood = False
					client.Send({"action": "foodAck", "food": client.food, "player":client.player, "gameid": client.gameid})
				else: 
					currentfood2.kill()
					currentfood2 = False
					client.Send({"action": "foodAck", "food": client.food, "player":client.player, "gameid": client.gameid})
			if client.player_mov==1:
				snake.movedir = client.movement
				snake.receive_tilepos(client.posx,client.posy,client.foodEaten)
				if client.foodEaten == True:
					snake.add_segment(SNAKE_SEGMENT_COLOR)
					snake.score += 1
					snake.move_rate += DIFFICULTY_INCREASE_RATE
					client.foodEaten=False
				for _ in xrange((client.clientfps-client.localfps)*snake.move_rate/MOVE_THRESHOLD):
					snake.move()
			else:
				snake2.movedir = client.movement
				snake2.receive_tilepos(client.posx,client.posy,client.foodEaten)
				if client.foodEaten == True:
					snake2.add_segment(SNAKE_SEGMENT_COLOR2)
					snake2.score += 1
					snake2.move_rate += DIFFICULTY_INCREASE_RATE
					client.foodEaten=False
				for _ in xrange((client.clientfps-client.localfps)*snake.move_rate/MOVE_THRESHOLD):
					snake.move()
			client.newMove=False
						
		if client.running:
			if firstRun:
				bg.fill(BACKGROUND_COLOR)
				screen.blit(bg, (0, 0))
				pygame.display.flip()
				random.seed(client.timeRand)
				firstRun = False
			client.localfps+=1
			all.update()
		
			#python uses function by value so I have to return it to modify it properly inside the function
			quit= player1Lose or player2Lose or quit
			player1Lose,currentfood,currentfood2= SnakeCollision(client, currentsnake, currentsnakeheadgroup, currentsnakegroup, foodgroup, foodgroup2, currentfood, currentfood2)
			player2Lose = client.playerLose
			
			#create eaten foods
			if currentfood == False:
				currentfood = food(takenupgroup)
				foodgroup.add(currentfood)
				takenupgroup.add(currentfood)
				all.add(currentfood)

			if currentfood2 == False:
				currentfood2 = food(takenupgroup)
				foodgroup2.add(currentfood2)
				takenupgroup.add(currentfood2)
				all.add(currentfood2)
		
			# score objects update
			d = screen.blit(bg, SCORE_POS1, pygame.Rect(SCORE_POS1, (50, 100)))
			f = pygame.font.Font(None, 12)
			scoreimage = f.render(SCORE_PREFIX1 + str(snake.score), True, SCORE_COLOR)
			d2 = screen.blit(scoreimage, SCORE_POS1)
			d3 = screen.blit(bg, SCORE_POS2, pygame.Rect(SCORE_POS2, (50, 100)))
			scoreimage = f.render(SCORE_PREFIX2 + str(snake2.score), True, SCORE_COLOR)
			d4 = screen.blit(scoreimage, SCORE_POS2)
		
			# drawing score objects
			dirty = all.draw(screen)
			dirty.append(d)
			dirty.append(d2)
			dirty.append(d3)
			dirty.append(d4)
		
			# updating
			pygame.display.update(dirty)
			#pygame.time.wait(500)
			# waiting
			clock.tick(FPS)
	
	# game over
	if quit or (player1Lose == True or player2Lose == True):
		if player1Lose == True and player2Lose == True: 
			loseMessage='Both Crashed'
		else:
			if player1Lose == True:
				loseMessage='You Lose!'
			else:
				loseMessage='You Win!'
		f = pygame.font.Font(None, 80)
		failmessage = f.render(loseMessage, True, (0, 0, 0))
		failrect = failmessage.get_rect()
		failrect.center = SCREENRECT.center
		screen.blit(failmessage, failrect)
		pygame.display.flip()
		pygame.time.wait(1000)


if __name__ == "__main__":
	main()
