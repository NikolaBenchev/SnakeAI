import pygame
import random
from enum import Enum
from collections import namedtuple, deque
import numpy as np

CELL_WIDTH = 50
(SCREEN_WIDTH, SCREEN_HEIGHT) = (1000, 1000)


class Direction(Enum):
    LEFT = 'left',
    RIGHT = 'right',
    UP = 'up',
    DOWN = 'down'


class Colors(Enum):
    PLAYER = pygame.Color('blue'),
    FOOD = pygame.Color('red')


Point = namedtuple('Point', 'x, y')

BOARD_WIDTH = int(SCREEN_WIDTH / CELL_WIDTH)
BOARD_HEIGHT = int(SCREEN_HEIGHT / CELL_WIDTH)

clockWiseDirections = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]


class SnakeGameAI:
    def __init__(self):
        self.setupWindow()
        self.reset()

    def reset(self):
        self.playerPos = Point(2, 0)
        self.direction = Direction.RIGHT
        self.tail = deque()
        self.score = 0

        self.board = [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

        # coordinates are (x, y)
        self.tail.append(Point(0, 0))
        self.tail.append(Point(1, 0))
        self.tail.append(Point(2, 0))

        # indexes are (y, x)
        self.board[0][0] = Colors.PLAYER.value
        self.board[0][1] = Colors.PLAYER.value
        self.board[0][2] = Colors.PLAYER.value

        # every cell in the board is currently empty besides the cells the player spawns in
        self.emptyCells = [i for i in range(BOARD_WIDTH * BOARD_HEIGHT) if i > 2]

        self.spawnFood()

    def setupWindow(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Snake")

    def spawnFood(self):
        index = random.randint(0, len(self.emptyCells))
        self.food = Point(self.emptyCells[index] % BOARD_WIDTH, self.emptyCells[index] // BOARD_HEIGHT)
        self.board[self.food.y][self.food.x] = Colors.FOOD.value
        self.emptyCells.remove(self.emptyCells[index])

    def draw(self):
        self.screen.fill((0, 0, 0))

        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if self.board[y][x] == 0:
                    continue
                rect = pygame.Rect(x * CELL_WIDTH, y * CELL_WIDTH, CELL_WIDTH, CELL_WIDTH)
                pygame.draw.rect(self.screen, self.board[y][x], rect)

    def move(self, action):
        # straight, right, left
        global clockWiseDirections

        index = clockWiseDirections.index(self.direction)

        if np.array_equal(action, [0, 1, 0]):
            index = (index + 1) % len(clockWiseDirections)
        elif np.array_equal(action, [0, 0, 1]):
            index = (index - 1) % len(clockWiseDirections)

        self.direction = clockWiseDirections[index]

        x, y = self.playerPos
        if self.direction == Direction.LEFT:
            x -= 1
        elif self.direction == Direction.RIGHT:
            x += 1
        elif self.direction == Direction.UP:
            y -= 1
        elif self.direction == Direction.DOWN:
            y += 1

        self.playerPos = Point(x, y)

    def playStep(self, action):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.gameOver = True
                self.quit()

        self.move(action)

        reward = 0
        gameOver = False
        if self.isCollision():
            gameOver = True
            reward = -10
            return reward, gameOver, self.score

        if self.board[self.playerPos.y][self.playerPos.x] == Colors.FOOD.value:
            self.score += 1
            self.spawnFood()
            reward = 10
        else:
            (tailX, tailY) = self.tail.popleft()
            self.board[tailY][tailX] = 0
            self.emptyCells.append(tailY * BOARD_WIDTH + tailX)
            self.emptyCells.remove(self.playerPos.y * BOARD_WIDTH + self.playerPos.x)

        self.tail.append((self.playerPos.x, self.playerPos.y))
        self.board[self.playerPos.y][self.playerPos.x] = Colors.PLAYER.value

        self.draw()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] and not self.direction == Direction.DOWN:
            self.direction = Direction.UP
        elif keys[pygame.K_a] and not self.direction == Direction.RIGHT:
            self.direction = Direction.LEFT
        elif keys[pygame.K_d] and not self.direction == Direction.LEFT:
            self.direction = Direction.RIGHT
        elif keys[pygame.K_s] and not self.direction == Direction.UP:
            self.direction = Direction.DOWN

        pygame.display.flip()
        self.clock.tick(15)
        return reward, gameOver, self.score

    def isCollision(self, point=None):
        if point is None:
            point = self.playerPos
        if point.x < 0 or point.y < 0 or point.x >= BOARD_WIDTH or point.y >= BOARD_HEIGHT:
            return True
        if not self.board[self.playerPos.y][self.playerPos.x] == 0 and not self.board[self.playerPos.y][
                                                                               self.playerPos.x] == Colors.FOOD.value:
            return True

        return False

    def quit(self):
        print(self.score)


game = SnakeGameAI()

while True:
    reward, gameOver, score = game.playStep([1, 0, 0])

    if gameOver:
        print(score)
        break
