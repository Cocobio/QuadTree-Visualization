##########################################################################################################################
#
# Key bindings:
#	- B: Toggle the bounding box.
#	- L: Lock the manual insertion. Denoted with bounding box on red.
#
#	- S: Toggles the search function and drawing the rect.
#	- ARROW UP: Grow searching rect, verticaly.
#	- ARROW DOWN: Shrink searching rect, verticaly.
#	- ARROW LEFT: Shrink searching rect, horizontaly.
#	- ARROW RIGHT: Grow searching rect, horizontaly.
#
#
#	##### Must have the user_insert flag set as True #####
#	- 1: Insert 1 city from data set.
#	- 2: Insert 10 city from data set.
#	- 3: Insert 100 city from data set.
#	- 4: Insert 1000 city from data set.
#	- 5: Insert 10000 city from data set.
#
##########################################################################################################################


import pygame
import numpy as np
from QuadTree import QuadTree

def read_and_parse_from(f):
	line = f.readline().split(";")
	data = [float(i) for i in line[-1][:-2].split(',')]
	data.append(int(line[4]))
	return data

background = (34,34,34)

# Screen size
scale_factor = 5
width = 360*scale_factor
height = 180*scale_factor

pygame.init()

# Create screen, set title and icon
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Quadtree")

q = QuadTree(width,height)

search_rect = pygame.Rect(0, 0, 80, 80)
search_color = (81,243,157)

text_color = (0,255,0)
text_background = (0,0,255)

modes = ['n of points: ', 'total population: ', 'REMOVING!']
mode = 0

font = pygame.font.Font('freesansbold.ttf', 32)
text = font.render('n of points: ', True, text_color, text_background)
textRect = text.get_rect()
textRect.left = 2
textRect.top = height - textRect.height - 2

#############################################################
filename = "C:/worldcitiespop_fixed.csv"
city_n = 20000

## FLAGS
running = True
user_insert = True
manual_insert = False
searching = False

if not user_insert:
	with open(filename, 'r', encoding="utf8") as f:
		f.readline()

		for i in range(city_n):
			data = read_and_parse_from(f)
			q.add_point((data[1]+180)*scale_factor, (data[0]-90)*(-scale_factor),data[2])
else:
	f = open(filename, 'r', encoding="utf8")
	f.readline()
#############################################################

while running:
	# timer
	# pygame.time.wait(2)
	
	# event attender
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

			if manual_insert:
				p = [i for i in pygame.mouse.get_pos()]
				q.add_point(*p)

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_b:
				q.toggle_boundingbox()
			elif event.key == pygame.K_l:
				manual_insert = not manual_insert
				q.manual_insert(manual_insert)

			elif event.key == pygame.K_1:
				if user_insert:
					data = read_and_parse_from(f)
					q.add_point((data[1]+180)*scale_factor, (data[0]-90)*(-scale_factor),data[2])
			elif event.key == pygame.K_2:
				if user_insert:
					for j in range(10):
						data = read_and_parse_from(f)
						q.add_point((data[1]+180)*scale_factor, (data[0]-90)*(-scale_factor),data[2])
			elif event.key == pygame.K_3:
				if user_insert:
					for j in range(100):
						data = read_and_parse_from(f)
						q.add_point((data[1]+180)*scale_factor, (data[0]-90)*(-scale_factor),data[2])
			elif event.key == pygame.K_4:
				if user_insert:
					for j in range(1000):
						data = read_and_parse_from(f)
						q.add_point((data[1]+180)*scale_factor, (data[0]-90)*(-scale_factor),data[2])
			elif event.key == pygame.K_5:
				if user_insert:
					for j in range(10000):
						data = read_and_parse_from(f)
						q.add_point((data[1]+180)*scale_factor, (data[0]-90)*(-scale_factor),data[2])

			elif event.key == pygame.K_n:
				mode = (mode+1)%len(modes)
			

			## Modify the searching rect
			elif event.key == pygame.K_s:
				searching = not searching
				q.set_searching(searching)
			

	keys = pygame.key.get_pressed()  #checking pressed keys

	if keys[pygame.K_UP]:
		search_rect.inflate_ip(0,1)
	if keys[pygame.K_DOWN]:
		search_rect.inflate_ip(0,-1)
	if keys[pygame.K_LEFT]:
		search_rect.inflate_ip(-1,0)
	if keys[pygame.K_RIGHT]:
		search_rect.inflate_ip(1,0)


	# OpenGL Stuff
	screen.fill(background)

	# Draw rect for searching
	l = []
	if searching:
		m_pos = pygame.mouse.get_pos()
		search_rect.move_ip(m_pos[0]-search_rect.left-search_rect.width/2, m_pos[1]-search_rect.top-search_rect.height/2)
		q.search_region((search_rect.left+search_rect.width/2, search_rect.top+search_rect.height/2), search_rect.width, search_rect.height, (lambda x, listing=l: listing.append(x)))
		if(mode == len(modes)-1):
			for node in l:
				q.remove_point(node.x, node.y)

	# Draw quadtree
	q.draw(screen)

	if searching:
		pygame.draw.rect(screen, search_color, search_rect, 2)


	## Text
	if mode == 0:
		text = font.render(modes[mode]+str(len(l)), True, text_color, text_background) 
	elif mode == 1:
		population = 0
		for node in l:
			population += node.info
		text = font.render(modes[mode]+str(population), True, text_color, text_background)
	else:
		text = font.render(modes[mode], True, text_color, text_background)

	screen.blit(text, textRect)

	pygame.display.update()

