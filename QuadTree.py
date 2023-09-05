import pygame
from math import fabs
import queue

WHITE = 0
GREY = 1
BLACK = 2

NW = 0
NE = 1
SW = 2
SE = 3


class Node:
    def __init__(self, t=GREY, x=0.0, y=0.0, i=0):
        self.children = [None, None, None, None]
        self.x = x
        self.y = y
        self.info = i
        self.type = t

        self.selected = False


def compare(p, x, y):
    if p.x < x:
        if p.y > y:
            return SW
        else:
            return NW
    elif p.y > y:
        return SE
    else:
        return NE


class QuadTree:
    def __init__(self, width, height):
        self.XF = [-0.25, 0.25, -0.25, 0.25]
        self.YF = [-0.25, -0.25, 0.25, 0.25]

        self.width = float(width)
        self.height = float(height)

        self.box = pygame.Rect(0, 0, width, height)

        self.quadrant_color_green = (92, 210, 95)
        self.quadrant_color_red = (236, 42, 127)
        self.quadrant_color = self.quadrant_color_red

        self.point_color = (236, 168, 42)
        self.point_color_accent = (235, 0, 54)

        self.root = None

        self.size = 0

        # Drawing
        self.bb = False
        # for drawing
        self.searching = False

    def add_point(self, x, y, i=0):
        lx = self.width
        ly = self.height
        center = [self.width/2.0, self.height/2.0]

        p = Node(BLACK, x, y, i)

        if not self.root:
            self.root = p
            self.size += 1
            return

        if self.root.type == BLACK:
            if self.root.x == x and self.root.y == y:
                return
            u = self.root
            self.root = Node(GREY)

            q = compare(u, *center)
            self.root.children[q] = u

        t = self.root
        q = compare(p, *center)

        while t.children[q] and t.children[q].type == GREY:
            t = t.children[q]
            center[0] += self.XF[q]*lx
            center[1] += self.YF[q]*ly

            lx /= 2
            ly /= 2

            q = compare(p, *center)

        if not t.children[q]:
            t.children[q] = p
        elif t.children[q].x == x and t.children[q].y == y:
            return
        else:
            u = t.children[q]
            uq = q

            while q == uq:
                t.children[q] = Node(GREY)
                t = t.children[q]

                center[0] += self.XF[q]*lx
                center[1] += self.YF[q]*ly

                lx /= 2
                ly /= 2

                q = compare(p, *center)
                uq = compare(u, *center)

            t.children[q] = p
            t.children[uq] = u

        self.size += 1

    def remove_point(self, x, y):
        lx = self.width
        ly = self.height
        center = [self.width/2.0, self.height/2.0]

        p = Node(BLACK, x, y)

        if not self.root:
            return
        elif self.root.type == BLACK:
            if self.root.x == p.x and self.root.y == p.y:
                self.root = None
                self.size -= 1
            return

        t = self.root
        f = None

        while True:
            q = compare(p, *center)

            if not t.children[q]:
                return

            if t.children[q].type == GREY and (t.children[q ^ 1] or
                                               t.children[q ^ 2] or
                                               t.children[q ^ 3]):
                f = t
                qf = q

            ft = t
            t = t.children[q]

            center[0] += self.XF[q]*lx
            center[1] += self.YF[q]*ly

            lx /= 2
            ly /= 2

            if not t or t.type != GREY:
                break

        if not t or t.x != p.x or t.y != p.y:
            return

        self.size -= 1

        ft.children[q] = None
        siblings = 0
        for i in range(4):
            if ft.children[i]:
                if ft.children[i].type == GREY:
                    return
                siblings += 1

        if siblings > 1:
            return

        t = self.root if not f else f.children[qf]

        while t and t.type == GREY:
            q = 0
            while not t.children[q]:
                q += 1

            tmp = t.children[q]
            t.children[q] = None
            t = tmp

        if not f:
            self.root = t
        else:
            f.children[qf] = t

    def recursive_draw(self, screen, node, x, y, w, h):
        if node.type == BLACK:
            if self.searching:
                pygame.draw.circle(screen,
                                   self.point_color_accent if node.selected
                                   else self.point_color,
                                   (int(node.x), int(node.y)), 2)
            else:
                pygame.draw.circle(screen, self.point_color,
                                   (int(node.x), int(node.y)), 2)
        elif node.type == GREY:
            if self.bb:
                pygame.draw.line(screen, self.quadrant_color, (x, y-h/2),
                                 (x, y+h/2), 1)
                pygame.draw.line(screen, self.quadrant_color, (x-w/2, y),
                                 (x+w/2, y), 1)

            for i in range(4):
                if node.children[i]:
                    self.recursive_draw(screen, node.children[i],
                                        x+self.XF[i]*w, y+self.YF[i]*h,
                                        w/2, h/2)

    def draw(self, screen):
        pygame.draw.rect(screen, self.quadrant_color, self.box, 2)

        if self.root:
            self.recursive_draw(screen, self.root, self.width/2, self.height/2,
                                self.width, self.height)

    def toggle_boundingbox(self):
        self.bb = not self.bb

    def manual_insert(self, flag):
        if flag:
            self.quadrant_color = self.quadrant_color_green
        else:
            self.quadrant_color = self.quadrant_color_red

    def set_searching(self, s):
        self.searching = s

    def recursive_region_search(self, node, x, y, w, h,
                                r_c, r_w, r_h, f_lambda):
        if node.type == BLACK:
            if fabs(node.x-r_c[0])*2 <= r_w and fabs(node.y-r_c[1])*2 <= r_h:
                node.selected = True
                f_lambda(node)
            return
        for i in range(4):
            if node.children[i] and fabs(x+self.XF[i]*w-r_c[0])*2 <= w+r_w \
                                and fabs(y+self.YF[i]*h-r_c[1])*2 <= h+r_h:
                self.recursive_region_search(node.children[i],
                                             x+self.XF[i]*w, y+self.YF[i]*h,
                                             w/2, h/2, r_c, r_w, r_h, f_lambda)

    def search_region(self, center, w, h, f_lambda):
        if not self.root:
            return

        # Clean selected ones
        q = queue.Queue()

        q.put(self.root)

        while not q.empty():
            n = q.get()
            if n.type == GREY:
                for i in range(4):
                    if n.children[i]:
                        q.put(n.children[i])
            else:
                n.selected = False

        self.recursive_region_search(self.root, self.width/2, self.height/2,
                                     self.width, self.height,
                                     center, w, h, f_lambda)
