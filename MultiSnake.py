import pygame
from pygame.locals import *
import random

# ---------- constants ---------- #
SCREENSIZE = (800, 600)
SCREENRECT = pygame.Rect(0, 0, SCREENSIZE[0], SCREENSIZE[1])
CAPTION = 'MultiSnake'
FPS = 40

START_TILE1 = (20, 20) #snake 1 spawn
START_TILE2 = (59, 39)
START_SEGMENTS = 7     #starting snake size

MOVE_RATE = 2
DIFFICULTY_INCREASE_RATE = .05
MOVE_THRESHOLD = 5 # when moverate counts up to this the snake moves

TILE_SIZE = (10, 10) #the resolution is divided in blocks os 10x10 pixels
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
def SnakeCollision(snake, snakeheadgroup, snakegroup, foodgroup,foodgroup2,currentfood,currentfood2,snake_color):
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
			snake.add_segment(snake_color)
			snake.score += 1
			snake.move_rate += DIFFICULTY_INCREASE_RATE

	# head -> food2
	col = pygame.sprite.groupcollide(snakeheadgroup, foodgroup2, False, True)
	for head in col:
		for tail in col[head]:
			currentfood2 = False
			snake.add_segment(snake_color)
			snake.score += 1
			snake.move_rate += DIFFICULTY_INCREASE_RATE

	return lose,currentfood,currentfood2

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
	
	pygame.display.flip()

	# mainloop
	quit = False
	snake1Move = False
	clock = pygame.time.Clock()
	while not quit:
		# quit or key pressed
		for event in pygame.event.get():
			if event.type == QUIT:
				quit = True
			elif event.type == KEYDOWN:
				if event.key == K_UP:
					currentmovedir = snake2.movedir
					tomove = 'up'
					dontmove = 'down'
				elif event.key == K_DOWN:
					currentmovedir = snake2.movedir
					tomove = 'down'
					dontmove = 'up'
				elif event.key == K_LEFT:
					currentmovedir = snake2.movedir
					tomove = 'left'
					dontmove = 'right'
				elif event.key == K_RIGHT:
					currentmovedir = snake2.movedir
					tomove = 'right'
					dontmove = 'left'
				elif event.key == K_w:
					currentmovedir = snake.movedir
					snake1Move = True
					tomove = 'up'
					dontmove = 'down'
				elif event.key == K_s:
					currentmovedir = snake.movedir
					snake1Move = True
					tomove = 'down'
					dontmove = 'up'
				elif event.key == K_a:
					currentmovedir = snake.movedir
					snake1Move = True
					tomove = 'left'
					dontmove = 'right'
				elif event.key == K_d:
					currentmovedir = snake.movedir
					snake1Move = True
					tomove = 'right'
					dontmove = 'left'
				else:
					raise RuntimeError, 'not expected'
				if not currentmovedir == dontmove:
					if snake1Move:
						snake.movedir = tomove
						snake1Move = False
					else:
						snake2.movedir = tomove
		
		# clearing
		all.clear(screen, bg)
		
		# updates
		all.update()
		
		#python uses function by value so I have to return it to modify it properly inside the function
		player1Lose,currentfood,currentfood2= SnakeCollision(snake,snakeheadgroup, snakegroup, foodgroup,foodgroup2,currentfood,currentfood2,SNAKE_SEGMENT_COLOR)
		player2Lose,currentfood,currentfood2= SnakeCollision(snake2,snakeheadgroup2, snakegroup2, foodgroup,foodgroup2,currentfood,currentfood2,SNAKE_SEGMENT_COLOR2)
		quit= player1Lose or player2Lose or quit

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
	if player1Lose == True or player2Lose == True:
		if player1Lose == True and player2Lose == True: 
			loseMessage='Both Crashed'
		else:
			if player1Lose == True:
				loseMessage='Player 1 Crashed'
			else:
				loseMessage='Player 2 Crashed'
		f = pygame.font.Font(None, 80)
		failmessage = f.render(loseMessage, True, (0, 0, 0))
		failrect = failmessage.get_rect()
		failrect.center = SCREENRECT.center
		screen.blit(failmessage, failrect)
		pygame.display.flip()
		pygame.time.wait(2000)


if __name__ == "__main__":
	main()
