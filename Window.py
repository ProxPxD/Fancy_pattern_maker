import time
import pygame
import random
from itertools import chain

class Window:
    
    GRID_COLOR = [40, 40, 40]
    WHITE = [255, 255, 255]
    BLACK = [0, 0, 0]

    class Point:

        def __init__(self, x, y):
            self.x = x
            self.y = y

        def __eq__(self, other):
            return self.x == other.x and self.y == other.y

        def __mul__(s, o):
            if s.x < o.x:
                return 'l'
            elif s.x > o.x:
                return 'r'
            if s.y < o.y:
                return 'd'
            elif s.y > o.y:
                return 'u'
            return ''

        def __copy__(self):
            return self.copy()

        def __str__(self):
            return "({}, {})".format(self.x, self.y)

        def copy(self):
            return type(self)(self.x, self.y)

        def up(self):
            self.y += 1
            return self

        def down(self):
            self.y -= 1
            return self

        def right(self):
            self.x += 1
            return self

        def left(self):
            self.x -= 1
            return self


    def __init__(self, width, height, rows, cols):

        #self.height = 560
        #self.width = 840
        self.width = width
        self.height = height

        self.rows = rows
        self.cols = cols
        self.starting_x = 20
        self.starting_y = 20

        self.init_board()
        self.tick_value = 0.01

        pygame.init()
        pygame.display.set_caption("Kangurator")
        self.screen = pygame.display.set_mode((self.width, self.height))

    def reset(self):
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.waiting = []
        self.current = self.random_point()
        self.white = []

    def init_board(self):
        self.reset()
        self.gap_size = 0
        if self.cols > self.rows:
            self.block_size = (self.height - self.starting_y) // self.cols
        else:
            self.block_size = (self.width - self.starting_x) // self.rows

        self.block_size -= self.gap_size
        self.ended = False
        self.current = self.random_point()
        self.drawed = False

    def set_tick_value(self, val):
        self.tick_value = val

    def random_point(self):
        return self.Point(random.randint(0, self.rows - 1), random.randint(0, self.cols - 1))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.ended = True

    def run(self):

        #tick = 0
        while not self.ended:

            self.handle_events()

            self.draw()
            if not self.drawed:
                self.move()
            else:
                #time.sleep(self.tick_value)
                self.reset()
                self.drawed = False

            pygame.display.flip()
            #time.sleep(self.tick_value)

    def make_rect(self, x, y):
        rect = [x, y, self.block_size, self.block_size]
        return rect

    def draw(self):
        self.screen.fill(self.BLACK)
        pygame.draw.rect(self.screen, self.GRID_COLOR, [self.starting_x, self.starting_y, self.rows*self.block_size, self.cols*self.block_size])
        for p in chain(self.waiting, self.white):
            x = self.starting_x + p.x * (self.block_size + self.gap_size)
            y = self.starting_y + p.y * (self.block_size + self.gap_size)
            rect = self.make_rect(x, y)
            pygame.draw.rect(self.screen, Window.WHITE, rect)
            if True and self.Point(p.x, p.y) == self.current:
                pygame.draw.rect(self.screen, [255, 0, 100], rect)

        '''
        for i in range(self.cols):
            for j in range(self.rows):
                x = self.starting_x + i * (self.block_size + self.gap_size)
                y = self.starting_y + j * (self.block_size + self.gap_size)
                pygame.draw.rect(self.screen, self.GRID_COLOR,
                                 [x - self.gap_size, y - self.gap_size, self.block_size + 2 * self.gap_size,
                                  self.block_size + 2 * self.gap_size])

                if self.board[i][j]:
                    rect = self.make_rect(x, y)
                    pygame.draw.rect(self.screen, Window.WHITE, rect)
                    if True and self.Point(i, j) == self.current:
                        pygame.draw.rect(self.screen, [255, 0, 100], rect)
        '''
    def move(self):
        c = self.current
        #print(c, len(self.waiting))
        self.board[c.x][c.y] = 1
        near = self.generate_moves()
        possible = self.filter_points(near)
        if len(possible):
            self.waiting.append(c)
            self.current = possible[0]
            #self.no_go.extend(possible[0:])
        else:
            if len(self.waiting):
                last = self.waiting.pop()
                self.current = last
                self.white.append(last)
            else:
                self.drawed = True

    def is_by_white(self, point):
        neighbours = self.generate_neighbours(point)
        for p in self.filter_coords(neighbours):
            if p == self.current:
                continue
            if self.board[p.x][p.y]:
                return True
        return False

    def filter_coords(self, points):
        return [p for p in points if 0 <= p.x < self.rows and 0 <= p.y < self.cols]

    def filter_points(self, points):
        check_coords = lambda p: 0 <= p.x < self.cols and 0 <= p.y < self.rows
        is_black = lambda p: not self.board[p.x][p.y]
        return [p for p in self.filter_coords(points) if is_black(p) and not self.is_by_white(p)]

    def generate_neighbours(self, point):
        near = self.generate_moves(point)
        m = point * self.current
        if m == 'u':
            near.append(point.copy().up().right())
            near.append(point.copy().up().left())
        elif m == 'd':
            near.append(point.copy().down().right())
            near.append(point.copy().down().left())
        elif m == 'l':
            near.append(point.copy().left().down())
            near.append(point.copy().left().up())
        elif m == 'r':
            near.append(point.copy().right().down())
            near.append(point.copy().right().up())
        return near

    def generate_moves(self, point=None):
        point = self.current if point is None else point
        near = [point.copy() for _ in range(4)]
        near[0].up()
        near[1].down()
        near[2].right()
        near[3].left()
        random.shuffle(near)
        return near