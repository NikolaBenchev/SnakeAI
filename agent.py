import torch
import random
from collections import deque
import numpy as np
from game import SnakeGameAI, Direction, Point, clockWiseDirections

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LEARNING_RATE = 0.001


class Agent:
    def __init__(self):
        self.currentNumberOfGames = 0
        self.epsilon = 0  # randomness
        self.gamma = 0  # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)
        # TODO: model, trainer
        self.model = None
        self.trainer = None

    def getState(self, game):
        surroundingPoints = {
            Direction.RIGHT: Point(game.playerPos.x + 1, game.playerPos.y),
            Direction.DOWN: Point(game.playerPos.x, game.playerPos.y + 1),
            Direction.LEFT: Point(game.playerPos.x, game.playerPos.x - 1),
            Direction.UP: Point(game.playerPos.x, game.playerPos.y - 1),
        }

        currentDirectionIndex = clockWiseDirections.index(game.direction)
        rightDirectionIndex = (currentDirectionIndex + 1) % len(clockWiseDirections)
        leftDirectionIndex = (currentDirectionIndex - 1) % len(clockWiseDirections)

        state = [
            # danger straight, right, left
            (game.isCollision(surroundingPoints[game.direction])),
            (game.isCollision(surroundingPoints[clockWiseDirections[rightDirectionIndex]])),
            (game.isCollision(surroundingPoints[clockWiseDirections[leftDirectionIndex]])),

            (Direction.LEFT == game.direction),
            (Direction.RIGHT == game.direction),
            (Direction.UP == game.direction),
            (Direction.DOWN == game.direction),

            game.food.x < game.playerPos.x,
            game.food.x > game.playerPos.x,
            game.food.y < game.playerPos.y,
            game.food.y > game.playerPos.y,
        ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, nextState, gameOver):
        self.memory.append((state, action, reward, nextState, gameOver))

    def trainLongMemory(self):
        if len(self.memory) > BATCH_SIZE:
            miniSample = random.sample(self.memory, BATCH_SIZE)
        else:
            miniSample = self.memory

        states, actions, rewards, nextStates, gameOvers = zip(*miniSample)

        self.trainer.trainStep(self, states, actions, rewards, nextStates, gameOvers)

    def trainShortMemory(self, state, action, reward, nextState, gameOver):
        self.trainer.trainStep(self, state, action, reward, nextState, gameOver)

    def getAction(self, state):
        self.epsilon = 80 - self.currentNumberOfGames
        finalMove = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
        else:
            stateTensor = torch.tensor(state, dtype=torch.float)
            prediction = self.model.predict(stateTensor)
            move = torch.argmax(prediction).item()

        finalMove[move] = 1

        return finalMove


def train():
    plotScores = []
    plotAverageScores = []
    totalScore = 0
    currentRecord = 0
    agent = Agent()
    game = SnakeGameAI()
    while True:
        oldState = agent.getState(game)

        finalMove = agent.getAction(oldState)

        reward, gameOver, score = game.playStep(finalMove)
        newState = agent.getState(game)

        agent.trainShortMemory(oldState, finalMove, reward, newState, gameOver)

        agent.remember(oldState, finalMove, reward, newState, gameOver)

        if gameOver:
            game.reset()
            agent.currentNumberOfGames += 1
            agent.trainLongMemory()

            if score > currentRecord:
                currentRecord = score

            print('Game:', agent.currentNumberOfGames, 'Score:', score, 'Record:', currentRecord)

            # TODO: Plot


if __name__ == '__main__':
    train()
