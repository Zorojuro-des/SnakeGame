import numpy as np
import random
from collections import deque
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 512)
        self.fc2 = nn.Linear(512, 512)
        self.fc3 = nn.Linear(512, 256)
        self.fc4 = nn.Linear(256, output_dim)
        
        # Initialize weights using Kaiming initialization
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_normal_(m.weight, mode='fan_in', nonlinearity='relu')
                nn.init.zeros_(m.bias)
    
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        return self.fc4(x)

class DQNAgent:
    def __init__(self, state_dim, action_dim, device, lr=0.00025, gamma=0.99, 
                 epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.9995,
                 batch_size=128, target_update_freq=1000):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.memory = deque(maxlen=100000)  # Larger replay buffer
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq
        self.device = device
        
        # Main network
        self.model = DQN(state_dim, action_dim).to(device)
        
        # Target network (for stability)
        self.target_model = DQN(state_dim, action_dim).to(device)
        self.target_model.load_state_dict(self.model.state_dict())
        self.target_model.eval()
        
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr, eps=1e-4)
        self.loss_fn = nn.SmoothL1Loss()  # Huber loss
        
        self.steps = 0
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
    
    def act(self, state, evaluation=False):
        if not evaluation and random.random() <= self.epsilon:
            return random.randint(0, self.action_dim - 1)
        
        state = torch.FloatTensor(state).to(self.device)
        with torch.no_grad():
            q_values = self.model(state)
        return torch.argmax(q_values).item()
    
    def replay(self):
        if len(self.memory) < self.batch_size:
            return
        
        # Sample batch from memory
        minibatch = random.sample(self.memory, self.batch_size)
        
        # Convert to tensors and move to device
        states = torch.FloatTensor(np.array([t[0] for t in minibatch])).to(self.device)
        actions = torch.LongTensor(np.array([t[1] for t in minibatch])).to(self.device)
        rewards = torch.FloatTensor(np.array([t[2] for t in minibatch])).to(self.device)
        next_states = torch.FloatTensor(np.array([t[3] for t in minibatch])).to(self.device)
        dones = torch.FloatTensor(np.array([t[4] for t in minibatch])).to(self.device)
        
        # Current Q values
        current_q = self.model(states).gather(1, actions.unsqueeze(1))
        
        # Next Q values from target network
        with torch.no_grad():
            next_q = self.target_model(next_states).max(1)[0]
            target_q = rewards + (1 - dones) * self.gamma * next_q
        
        # Compute loss and update
        loss = self.loss_fn(current_q.squeeze(), target_q)
        
        self.optimizer.zero_grad()
        loss.backward()
        
        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), 10)
        self.optimizer.step()
        
        # Update target network
        if self.steps % self.target_update_freq == 0:
            self.target_model.load_state_dict(self.model.state_dict())
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        self.steps += 1
        return loss.item()
    
    def save(self, path):
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'target_model_state_dict': self.target_model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'steps': self.steps
        }, path)
    
    def load(self, path):
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.target_model.load_state_dict(checkpoint['target_model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint['epsilon']
        self.steps = checkpoint['steps']
        self.model.eval()
        self.target_model.eval()