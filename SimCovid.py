import pygame
from random import randint, random
from math import exp
from matplotlib import pyplot as plt
pygame.font.init()



START = 600
WIN_W = 1700
WIN_H = 1000
VEL = 1.5
MEDIAN_AGE = 40
POP_RISK = 0.02 * exp(MEDIAN_AGE*0.07)
BED_CAP = 0.1*START
DURATION = 800
STAT_FONT = pygame.font.SysFont("comicsans", 35)
CONF_RAD = 4000000

PROB_INIT = 1
CONT_RAD = 20


win = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("Simulation Covid")
win.fill((255,255,255))


def get_dist_bet(xa, ya, xb, yb):
	return (((xb-xa)**2 + (yb-ya)**2))**0.5

class Person:

	color = (0,150,200)
	GREEN = (150, 200, 0)
	GREY = (150,150,150)
	ORANGE = (255, 127, 80)
	RED = (255, 0, 0)
	BLACK = (0,0,0)
	IMMUNE = False

	def __init__(self, x, y, xvel, yvel, cont):
		self.x = x
		self.y = y
		self.spx = x
		self.spy = y
		self.XVEL = xvel
		self.YVEL = yvel
		self.crit = False
		self.dead = False
		self.TICKS_SICK = 0 
		self.cont = cont
		if self.cont:
			self.color = self.GREEN


	def draw(self):
		pygame.draw.circle(win, self.color, (round(self.x), round(self.y)), 10)
		if self.color == self.GREEN:
			pygame.draw.circle(win, (150, 200, 0, 0.3), (round(self.x), round(self.y)), round(1 + (((self.TICKS_SICK%60)/59)*(CONT_RAD-1))), 1)


	def move(self):

		if abs(self.x - self.spx) >= CONF_RAD:
			self.XVEL = -self.XVEL
		if abs(self.y - self.spy) >= CONF_RAD:
			self.YVEL = -self.YVEL

		if self.x < 50 or self.x > WIN_W-20:
			self.XVEL = -self.XVEL
		if self.y < 50 or self.y > WIN_H-20:
			self.YVEL = -self.YVEL


		self.x += self.XVEL
		self.y += self.YVEL


	def check_inf(self):
		if self.cont and not(self.crit):
			self.TICKS_SICK += 1
			if self.TICKS_SICK >= DURATION:

				self.cont = False
				self.IMMUNE = True
				if self in contamines:
					contamines.remove(self)
				else:
					inhosp.remove(self)
				self.color = self.GREY
				global immune_counter
				immune_counter += 1

		elif self.crit:
			self.TICKS_SICK += 1
			if self.TICKS_SICK >= DURATION/4:
				self.cont = False
				self.crit = False
				self.dead = True
				self.color = self.BLACK
				self.XVEL = 0
				self.YVEL = 0
				self.IMMUNE = True
				critical.remove(self)
				global dead
				dead += 1

		elif not(self.IMMUNE):
			to_add = False
			for case in contamines:
				dist = get_dist_bet(self.x, self.y, case.x, case.y)
				if dist <= CONT_RAD:
					to_add = True

			if to_add:
				nb = randint(0,10000)
				if len(inhosp) >= BED_CAP:
					if nb >= 1500:
						self.color = self.RED
						self.crit = True
						self.cont = True
						critical.append(self)
					else:
						self.cont = True
						self.color = self.GREEN
						contamines.append(self)

				else:
					if nb <= POP_RISK*100:
						self.color = self.RED
						self.crit = True
						self.cont = True
						critical.append(self)
					elif nb<= 1500:
						self.color = self.ORANGE
						self.cont = True
						inhosp.append(self)
					else:
						self.cont = True
						self.color = self.GREEN
						contamines.append(self)

				global sucept_counter
				sucept_counter -= 1



contamines = []
people = []

for _ in range(START):
	xvel = randint(0, VEL*100*2)/100 - VEL
	ysign = randint(0,1)
	yvel = (VEL**2 - xvel**2)**0.5

	if ysign == 0:
		yvel *= -1

	xpos = randint(70, WIN_W-30)
	ypos = randint(70, WIN_H-30)

	cont  = False
	if len(contamines) < PROB_INIT:
		cont = True

	new_pers = Person(xpos, ypos, xvel, yvel, cont)
	people.append(new_pers)
	if cont:
		contamines.append(new_pers)


immune_counter = 0
sucept_counter = START - len(contamines)

tick_counter = 0 

clock = pygame.time.Clock()
time_since_end = 0

progr = [len(contamines) for _ in range(7)]
imm = [0 for _ in range(7)]
sucept = [START - len(contamines) for _ in range(7)]

critical = []
inhosp = []
inhosp_tracker = [0 for _ in range(7)]

dead = 0
dead_tracker = [0 for _ in range(7)]




for person in people:
	person.draw()

pygame.display.update()


game_running = True

while game_running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			game_running = False
			break

	win.fill((255,255,255))

	text0 = STAT_FONT.render(f"Suceptibles: {sucept_counter}", 1, (0, 150, 200))
	win.blit(text0, (10, 10))
	text1 = STAT_FONT.render(f"Contaminés: {len(contamines)}", 1, (150 , 200, 0))
	win.blit(text1, (WIN_W * 0.2-text1.get_width()/2, 10))
	text2 = STAT_FONT.render(f"Immunisés: {immune_counter}", 1, (150, 150, 150))
	win.blit(text2, (WIN_W * 0.4-text2.get_width()/2, 10))
	text3 = STAT_FONT.render(f"Hospitalisés: {len(inhosp)}", 1, (255, 127, 80))
	win.blit(text3, (WIN_W * 0.6-text3.get_width()/2, 10))
	text4 = STAT_FONT.render(f"État critique: {len(critical)}", 1, (255, 0, 0))
	win.blit(text4, (WIN_W * 0.8-text4.get_width()/2, 10))
	text5 = STAT_FONT.render(f"Morts: {dead}", 1, (0, 0, 0))
	win.blit(text5, (WIN_W-10-text5.get_width(), 10))




	for elt in people:
		elt.move()
		elt.check_inf()
		elt.draw()

	if len(contamines) == 0:
		time_since_end += 1
	if time_since_end >= 180:
		game_running = False

	pygame.display.update()
	clock.tick(60)
	tick_counter+=1

	if tick_counter % 30 == 0:
		progr.append(len(contamines)+len(inhosp))
		imm.append(immune_counter)
		sucept.append(sucept_counter)
		inhosp_tracker.append(len(inhosp))
		dead_tracker.append(dead)

plt.title("Résultats Simulation")
plt.plot(progr, color='green', label='Personnes infectées')
plt.plot(imm, color = 'grey', label = "Personnes Immunisés")
plt.plot(sucept, color = (0, 150/255, 200/255), label = 'Personnes a risque')
plt.plot([BED_CAP for _ in range(len(progr))], color = 'red', label = 'Capacité des hopitaux')
plt.plot(inhosp_tracker, color = 'orange', label = 'Lits occupés')
plt.plot(dead_tracker, color = 'black', label = 'Morts')
plt.legend()
plt.show()









