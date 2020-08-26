import pygame

WHITE = 0
GREY = 1
BLACK = 2

NW = 0
NE = 1
SW = 2
SE = 3

class Node:
	def __init__(self, t=GREY, x=0.0, y=0.0):
		self.children = [None, None, None, None]
		self.x = x
		self.y = y
		self.info = None
		self.type = t

def compare(p, x, y):
	if p.x<x:
		if p.y>y:
			return SW
		else:
			return NW

	elif p.y>y:
		return SE
	else:
		return NE

class QuadTree:

	def __init__(self, width, height):
		self.XF = [-0.25,0.25,-0.25,0.25]
		self.YF = [-0.25,-0.25,0.25,0.25]

		self.width = float(width)
		self.height = float(height)

		self.box = pygame.Rect(0, 0, width, height)

		self.quadrant_color_green = (92,210,95)
		self.quadrant_color_red = (236,42,127)
		self.quadrant_color = self.quadrant_color_red
		self.point_color = (236,168,42)

		self.root = None

		self.size = 0

		## Drawing
		self.bb = False

	def add_point(self, x, y):
		lx = self.width
		ly = self.height
		center = [self.width/2, self.height/2]

		if self.root == None:
			self.root = Node(BLACK,x,y)
			self.size += 1
			return
		
		p = Node(BLACK,x,y)

		if self.root.type == BLACK:
			if self.root.x == x and self.root.y == y:
				return
			u = self.root
			self.root = Node(GREY)

			q = compare(u, *center)
			self.root.children[q] = u

		t = self.root
		q = compare(p,*center)

		while t.children[q] != None and t.children[q].type == GREY:
			t = t.children[q]
			center[0] += self.XF[q]*lx
			center[1] += self.YF[q]*ly

			lx /= 2
			ly /= 2

			q = compare(p,*center)

		if t.children[q] == None:
			t.children[q] = Node(BLACK,x,y)
		elif t.children[q].x == x and t.children[q].y == y:
			return
		else:
			u = t.children[q]
			uq = q

			while q==uq:
				t.children[q] = Node(GREY)
				t = t.children[q]

				center[0] += self.XF[q]*lx
				center[1] += self.YF[q]*ly

				lx /= 2
				ly /= 2

				q = compare(p,*center)
				uq = compare(u,*center)

			t.children[q] = Node(BLACK,x,y)
			t.children[uq] = u

		self.size += 1

	def recursive_draw(self, screen, node, x, y, w, h):
		if node.type == BLACK:
			pygame.draw.circle(screen, self.point_color, (int(node.x), int(node.y)), 2)
		elif node.type == GREY:
			if self.bb:
				pygame.draw.line(screen, self.quadrant_color, (x,y-h/2), (x,y+h/2), 2)
				pygame.draw.line(screen, self.quadrant_color, (x-w/2,y), (x+w/2,y), 2)

			for i in range(4):
				if node.children[i] != None:
					self.recursive_draw(screen,node.children[i],x+self.XF[i]*w,y+self.YF[i]*h,w/2,h/2)

	def draw(self, screen):
		pygame.draw.rect(screen, self.quadrant_color, self.box, 2)
		lx = self.width
		ly = self.height

		if self.root != None:
			self.recursive_draw(screen, self.root, self.width/2, self.height/2, self.width, self.height)


	def toggle_boundingbox(self):
		self.bb = not self.bb

	def manual_insert(self, flag):
		if flag:
			self.quadrant_color = self.quadrant_color_green
		else:
			self.quadrant_color = self.quadrant_color_red