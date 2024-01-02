import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import datetime
import os

class DeepQNet(nn.Module):
    def __init__(self, input_size, output_size):
        super(DeepQNet, self).__init__()
        self.hidden1 = nn.Linear(input_size, 128)
        self.hidden2 = nn.Linear(128, 64)
        self.output = nn.Linear(64, output_size)

    def forward(self, x):
        x = F.relu(self.hidden1(x))
        x = F.relu(self.hidden2(x))
        x = self.output(x)
        return x

    def save(self, file_name='model.pth'):
        model_folder_path = './models'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamped_file_name = f"{os.path.splitext(file_name)[0]}_{timestamp}.pth"
        file_path = os.path.join(model_folder_path, timestamped_file_name)
        torch.save(self.state_dict(), file_path)


class DQNTrainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr #tune lr
        self.gamma = gamma # tune gamma [0.9, 0.99]
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.HuberLoss() # tune delta

    # reward = immediate reward after performing the action
    # next_state = state after action is performed
    # all values can be either single value or batch of values
    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)

        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done, )

        predicted_q_values = self.model(state)

        target_q_values = predicted_q_values.clone()
        for idx in range(len(done)):
            updated_q_value = reward[idx]

            if not done[idx]:
                future_q_values = self.model(next_state[idx])
                max_future_q = torch.max(future_q_values) # or use mean, because environment is nondeterministic
                discounted_max_future_q = self.gamma * max_future_q
                updated_q_value = reward[idx] + discounted_max_future_q

            action_taken_index = torch.argmax(action[idx]).item()
            target_q_values[idx][action_taken_index] = updated_q_value
    
        self.optimizer.zero_grad()
        self.criterion(target_q_values , predicted_q_values).backward()
        self.optimizer.step()


