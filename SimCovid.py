import pygame
from random import randint, random
from math import exp
from matplotlib import pyplot as plt
pygame.font.init()


#Declaration des parametres de la simulation
# 1 cycle = 1/60 secondes (c'est la durée d'actualisation de la boucle de simulation)
START = 600 # Effectifs de départ
WIN_W = 1700 # Largeur de la fenetre
WIN_H = 1000 # Hauteur de la fenetre
VEL = 1.5 # Distance parcourue par un individu en un cycle
MEDIAN_AGE = 40 # Age median de la population etudiée
POP_RISK = 0.02 * exp(MEDIAN_AGE*0.07) # Risque (proba de mort) calculée pour une population d'age donné
BED_CAP = 0.1*START # Capacité des hopitaux
DURATION = 800 # Durée d'infection en cycles
STAT_FONT = pygame.font.SysFont("comicsans", 35) # Mise en place de la police
CONF_RAD = 4000000 # Taille du carré de confinement.
'''Confinement:
-------------
|           |
|           |
|           |
|           |
-------------
Les individus sont coincés dans un carré de coté 2*CONF_RAD. Pour enlever 
le confinement, il suffit de faire en sorte que le carré soit plus grand que la taille de la fenetre.
J'ai mis une tres grande valeur ici pour que les limites de deplacement soient la fenetre en elle meme, et
pas le confinement
'''

PROB_INIT = 1 # Nombre d'individus infectes initialement
CONT_RAD = 20 # Distance a partir de laquelle une personne infectée en infecte une autre


win = pygame.display.set_mode((WIN_W, WIN_H)) # Création de la fenetre
pygame.display.set_caption("Simulation Covid") # Affichage du titre
win.fill((255,255,255)) # Couleur blanche pour la fenetre


def get_dist_bet(xa, ya, xb, yb):
	#Fonction qui donne la distance entre deux points
	#Pour savoir si un individu devra etre infecté
	return (((xb-xa)**2 + (yb-ya)**2))**0.5

class Person:
	#Une classe pour representer un individu
	color = (0,150,200) #Couleur bleu initiale
	GREEN = (150, 200, 0) # Vert
	GREY = (150,150,150) # Gris
	ORANGE = (255, 127, 80) # Orange
	RED = (255, 0, 0) # Rouge
	BLACK = (0,0,0) #Noir
	IMMUNE = False # Booleen decrivant l'etat infecté ou non de la personne

	def __init__(self, x, y, xvel, yvel, cont):
		# Constructeur de la classe, mise en place des parametres de l'individu
		self.x = x # Abscisse de depart
		self.y = y #Ordonnée de depart
		self.spx = x # coord x de depart du point pour appliquerle confinement autour de son depart
		self.spy = y # Idemme avec coord y
		self.XVEL = xvel # Vitesse X en pixel par cycle
		self.YVEL = yvel # Vitesse Y en pixel par cycle
		self.crit = False # La personne est-elle en etat critique (elle va bientot mourrir?)
		self.dead = False # La personne est-elle morte?
		self.TICKS_SICK = 0 # Depuis combien de cycles est elle malade
		self.cont = cont # La personne est-elle malade?
		if self.cont:
			# Si la personne est malade, sa couleur devient le vert
			self.color = self.GREEN


	def draw(self):
		#Fonction pour afficher la personne a l ecran
		pygame.draw.circle(win, self.color, (round(self.x), round(self.y)), 10)
		if self.color == self.GREEN:
			#Si la personne est infectée, et contagieuse, cercle vert qui delimite distance de contagiosité
			pygame.draw.circle(win, (150, 200, 0, 0.3), (round(self.x), round(self.y)), round(1 + (((self.TICKS_SICK%60)/59)*(CONT_RAD-1))), 1)


	def move(self):
		# Deplacement de l'individu
		
		# Si on depasse les bords du carré confinement, on rebondit
		# Pour rebondir, si on tappe a gauche ou a droite, on oppose
		# La vitesse sur l'axe des x, et sinon, si on tappe en haut ou en bas, 
		# On oppose la vitesse sur l'axe des y
		if abs(self.x - self.spx) >= CONF_RAD:
			self.XVEL = -self.XVEL
		if abs(self.y - self.spy) >= CONF_RAD:
			self.YVEL = -self.YVEL
		#Si on atteint les bords de la fenetre on rebondit
		if self.x < 50 or self.x > WIN_W-20:
			self.XVEL = -self.XVEL
		if self.y < 50 or self.y > WIN_H-20:
			self.YVEL = -self.YVEL

		# Une fois qu'on a verifié que l'on est pas sorti des limites,
		# On ajoute la distance parcourue en un cycle a la position
		self.x += self.XVEL
		self.y += self.YVEL


	def check_inf(self):
		#Fonction pour gerer la logique de la maladie
		if self.cont and not(self.crit):
			# Si on est malade mais on ne va pas mourrir
			self.TICKS_SICK += 1 # Incrementation du nombre de cycles pdt lesquelles on a ete malade
			if self.TICKS_SICK >= DURATION:
				# Lorsqu'on a ete malade pour la durée de la maladie, on gueri et divient immunisé
				self.cont = False # On est plus malade
				self.IMMUNE = True # On est immunisés
				if self in contamines:
					# SI on est dans la liste des malades non-hospitalises, on se retire
					contamines.remove(self)
				else:
					#Sinon, on se retire de la liste des hospitalisés
					inhosp.remove(self)
				# COuleur de l'immunisé
				self.color = self.GREY
				global immune_counter
				# Incrementation du compteur de personnes immunisées
				immune_counter += 1

		elif self.crit:
			# Si on est en etat critique et qu'on va mourrir
			self.TICKS_SICK += 1 # Incrementation du nombre de cycles de maladie
			if self.TICKS_SICK >= DURATION:
				# On suppose que si on est en etat critique de mort, on meurt au bout de la
				# Duree de la maladie
				self.cont = False # On est plus contaminé
				self.crit = False # ON est plus critique
				self.dead = True # ON est mort
				self.color = self.BLACK # COuleur mort est noir
				self.XVEL = 0 # ON ne bouge plus
				self.YVEL = 0 # ...
				self.IMMUNE = True # On est immunisé
				critical.remove(self) # On est plus dans la liste des critiques
				global dead
				dead += 1
				# Incrementation du nombre de morts

		elif not(self.IMMUNE):
			# Si on n'est pas encore rentré en contact avec la maladie
			to_add = False
			for case in contamines:
				# Pour chaque personne contagieuses, on calcul la distance a nous
				dist = get_dist_bet(self.x, self.y, case.x, case.y)
				if dist <= CONT_RAD:
					# Si la personne est trop proche, on devient infecté
					to_add = True

			if to_add:
				# La personne attrape la maladie
				nb = randint(0,10000)
				#Tirage aléatoire
				if len(inhosp) >= BED_CAP:
					# Si les hopitaux sont debordés
					if nb >= 1500:
						# 15% deviennent critique et meurent
						self.color = self.RED # On devient critique
						self.crit = True
						self.cont = True # On est donc contamines
						critical.append(self) 
					else:
						# Sinon, on est just contaminé
						self.cont = True 
						self.color = self.GREEN
						contamines.append(self)

				else:
					# SI les hopitaux de sont pas debordés
					if nb <= POP_RISK*100:
						# Si la personne est dans un etat critique (depend du risque de la population)
						self.color = self.RED # Meme chose que plua haut pour les critiques
						self.crit = True
						self.cont = True
						critical.append(self)
					elif nb<= 1500:
						# Dans envrions 15%, on est hospitalisé
						self.color = self.ORANGE # Couleur hospitalisation
						self.cont = True # ON est contaminés
						inhosp.append(self) # On occupe une place a l'hopital
					else:
						# Sinon, on est juste infecté
						self.cont = True
						self.color = self.GREEN
						contamines.append(self)

				global sucept_counter
				sucept_counter -= 1
				# Si on rentre en contact avec la maladie, il y a une personne
				# de moins qui est susceptible de l'attraper



contamines = [] # Liste pour stocker toutes les personnes contaminées
people = [] # Liste pour stocker toutes les personnes

for _ in range(START):
	# Création de la population de depart
	
	# Definition aleatoire de la direction et du sens de l'individu
	xvel = randint(0, VEL*100*2)/100 - VEL
	ysign = randint(0,1)
	yvel = (VEL**2 - xvel**2)**0.5

	if ysign == 0:
		yvel *= -1

	#Defintion aleatoire de la positon de départ
	xpos = randint(70, WIN_W-30)
	ypos = randint(70, WIN_H-30)
	
	# Introduction dans la population des premiers cas (PROB_init individus)
	cont  = False
	if len(contamines) < PROB_INIT:
		cont = True

	new_pers = Person(xpos, ypos, xvel, yvel, cont) # creation de la personne avec les parametres
	people.append(new_pers)
	if cont:
		contamines.append(new_pers)
		# Si ell est contaminée, on l'ajoute a la liste


immune_counter = 0 # Nombre d'immunisés au depart
sucept_counter = START - len(contamines) # Nombre de personnes jamais entrées en contact avec la maladie

tick_counter = 0 # Date de depart (en cycles) 

clock = pygame.time.Clock() # Création d'un regulateur de la boucle pour avoir 60 iterations par seconde
time_since_end = 0 # Pendule pour avoir un peu de temps apres la fin de la simulation

#Listes pour suivre la repartition des individus a chaque instant de la simulation
progr = [len(contamines) for _ in range(7)] #Pour les graphiques, ajout de quelques valeurs intiales pour simuler l'etat avant le demarrage
imm = [0 for _ in range(7)] #Nombre de personnes immunisés a chaque instant
sucept = [START - len(contamines) for _ in range(7)] # Nb de personnes susceptibles d'etre infectés

critical = [] # Personnes en etat critque
inhosp = [] # Personnes a l'hopital
inhosp_tracker = [0 for _ in range(7)] # Nombre de personnes a l'hopital a chaque instant

dead = 0 # Nb de morts
dead_tracker = [0 for _ in range(7)] # Nb morts a chaque instant




for person in people:
	# on dessine tt le monde au debut
	person.draw()

pygame.display.update()
# Actualisation de l'affichage


game_running = True

while game_running:
	#BOUCLE DE SIMULATION
	for event in pygame.event.get():
		
		if event.type == pygame.QUIT:
			# Arret de la simulation ?
			game_running = False
			break

	win.fill((255,255,255))
	# On vide la fenetre en la remplissant de blanc

	#affichage des données en haut de l'ecran
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
		# Pour chaque personne
		elt.move() # Deplacement
		elt.check_inf() # Verification de l'etat infectueux
		elt.draw() # Affichage de la personne apres son deplacement et peut etre changement de couleur

	if len(contamines) == 0:
		# Si plus personne n'est malade, on attend un peu de temps avant de termier la simulation
		time_since_end += 1
	if time_since_end >= 180:
		game_running = False

	pygame.display.update() # Mise a jour de l'affichage
	clock.tick(60) # Regulateur pour verifier qu'on fait bien 60 iteration de la boucle de simulation par seconde
	tick_counter+=1 # Incrementation de la date

	if tick_counter % 30 == 0:
		# Toute les 30 cycles = 1/2 seconde, on echantillonne l'etat de la population pour le graphique
		progr.append(len(contamines)+len(inhosp))
		imm.append(immune_counter)
		sucept.append(sucept_counter)
		inhosp_tracker.append(len(inhosp))
		dead_tracker.append(dead)

		
# Graphique pour le compte rendu
plt.title("Résultats Simulation")
plt.plot(progr, color='green', label='Personnes infectées')
plt.plot(imm, color = 'grey', label = "Personnes Immunisés")
plt.plot(sucept, color = (0, 150/255, 200/255), label = 'Personnes a risque')
plt.plot([BED_CAP for _ in range(len(progr))], color = 'red', label = 'Capacité des hopitaux')
plt.plot(inhosp_tracker, color = 'orange', label = 'Lits occupés')
plt.plot(dead_tracker, color = 'black', label = 'Morts')
plt.legend()
plt.show()









