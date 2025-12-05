import pygame
import random
from enum import Enum
from collections import deque

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


(playerX, playerY) = (2, 0)
playerDirection = Direction.RIGHT
tail = deque()

score = 0

BOARD_WIDTH = int(SCREEN_WIDTH / CELL_WIDTH)
BOARD_HEIGHT = int(SCREEN_HEIGHT / CELL_WIDTH)
board = [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

# coordinates are (x, y)
tail.append((0, 0))
tail.append((1, 0))
tail.append((2, 0))

# indexes are (y, x)
board[0][0] = Colors.PLAYER.value
board[0][1] = Colors.PLAYER.value
board[0][2] = Colors.PLAYER.value

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

pygame.display.set_caption("Snake")


# def spawnFood():
# index = random()


def draw():
    global screen
    screen.fill((0, 0, 0))

    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            if board[y][x] == 0:
                continue
            rect = pygame.Rect(x * CELL_WIDTH, y * CELL_WIDTH, CELL_WIDTH, CELL_WIDTH)
            pygame.draw.rect(screen, board[y][x], rect)


gameOver = False
while not gameOver:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameOver = True

    if playerDirection == Direction.LEFT:
        playerX -= 1
    elif playerDirection == Direction.RIGHT:
        playerX += 1
    elif playerDirection == Direction.UP:
        playerY -= 1
    elif playerDirection == Direction.DOWN:
        playerY += 1

    if playerX < 0 or playerY < 0 or playerX >= BOARD_WIDTH or playerY >= BOARD_HEIGHT:
        gameOver = True

    if board[playerY][playerX] == Colors.FOOD.value:
        score += 1
    elif not board[playerY][playerX] == 0:
        gameOver = True
    else:
        removedTail = tail.popleft()
        board[removedTail[1]][removedTail[0]] = 0

    tail.append((playerX, playerY))
    board[playerY][playerX] = Colors.PLAYER.value

    draw()

    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        playerDirection = Direction.UP
    elif keys[pygame.K_a]:
        playerDirection = Direction.LEFT
    elif keys[pygame.K_d]:
        playerDirection = Direction.RIGHT
    elif keys[pygame.K_s]:
        playerDirection = Direction.DOWN

    pygame.display.flip()
    clock.tick(10)

pygame.quit()
print(score)
