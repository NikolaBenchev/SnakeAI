import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os

class Linear_QNet(nn.Module):
    def __init__(self, inputSize, hiddenSize, outputSize):
        super(Linear_QNet, self).__init__()
        self.inputLayer = nn.Linear(inputSize, hiddenSize)
        self.outputLayer = nn.Linear(hiddenSize, outputSize)

    def forward(self, x):
        x = F.relu(self.inputLayer(x))
        return self.outputLayer(x)

    def save(self, filename='model.pth'):
        modelFolderPath = './modelData'
        if not os.path.exists(modelFolderPath):
            os.makedirs(modelFolderPath)

        filePath = os.path.join(modelFolderPath, filename)
        torch.save(self.state_dict(), filePath)

class QTrainer:
    def __init__(self, model, learningRate, gamma):
        self.model = model
        self.learningRate = learningRate
        self.gamma = gamma
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learningRate)
        self.criterion = nn.MSELoss()

    def trainStep(self, state, action, reward, nextState, gameOver):
        state = torch.tensor(state, dtype=torch.float)
        nextState = torch.tensor(nextState, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)

        if len(state.shape) == 1:
            # convert it to list (1, state)
            state = torch.unsqueeze(state, 0)
            nextState = torch.unsqueeze(nextState, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            gameOver = (gameOver, )

        prediction = self.model(state)
        target = prediction.clone()
        for index in range(len(gameOver)):
            Q_new = reward[index]
            if not gameOver[index]:
                Q_new += self.gamma * torch.max(self.model(nextState[index]))

            target[index][torch.argmax(action).item()] = Q_new

        self.optimizer.zero_grad()
        loss = self.criterion(target, prediction) # maybe swap the parameters
        loss.backward()

        self.optimizer.step()