from snake_env import SnakeGame
from dqn_agent import DQNAgent
import numpy as np
import torch
import time
import os
from datetime import datetime

def train():
    # Setup device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Environment setup
    env = SnakeGame(width=36, height=36, gui=False)
    state_dim = len(env._get_state())
    action_dim = 4
    
    # Training parameters
    episodes = 4000
    batch_size = 128
    save_interval = 100
    eval_interval = 50
    eval_episodes = 10
    
    # Create directories for saving models and logs
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_dir = f"models/snake_dqn_{timestamp}"
    os.makedirs(model_dir, exist_ok=True)
    
    # Initialize agent
    agent = DQNAgent(
        state_dim=state_dim,
        action_dim=action_dim,
        device=device,
        lr=0.00025,
        gamma=0.99,
        epsilon=1.0,
        epsilon_min=0.01,
        epsilon_decay=0.9995,
        batch_size=batch_size,
        target_update_freq=1000
    )
    
    # Training metrics
    rewards_history = []
    loss_history = []
    eval_results = []
    
    # Training loop
    for e in range(1, episodes + 1):
        state = env.reset()
        total_reward = 0
        episode_loss = 0
        steps = 0
        done = False
        
        while not done:
            # Agent acts in the environment
            action = agent.act(state)
            next_state, (reward, _), done, _ = env.step(action2=action)
            
            # Store experience
            agent.remember(state, action, reward, next_state, done)
            
            # Train the agent
            loss = agent.replay()
            if loss is not None:
                episode_loss += loss
            
            state = next_state
            total_reward += reward
            steps += 1
        
        # Calculate average loss
        avg_loss = episode_loss / steps if steps > 0 else 0
        
        # Store metrics
        rewards_history.append(total_reward)
        loss_history.append(avg_loss)
        
        # Evaluation
        if e % eval_interval == 0:
            avg_eval_reward = evaluate_agent(agent, env, eval_episodes, device)
            eval_results.append((e, avg_eval_reward))
            print(f"Evaluation after episode {e}: Average Reward = {avg_eval_reward:.2f}")
        
        # Print progress
        print(f"Episode: {e}/{episodes}, Reward: {total_reward:.2f}, "
              f"Avg Loss: {avg_loss:.4f}, Epsilon: {agent.epsilon:.4f}, "
              f"Steps: {steps}")
        
        # Save model
        if e % save_interval == 0:
            model_path = os.path.join(model_dir, f"snake_dqn_episode_{e}.pth")
            agent.save(model_path)
            print(f"Model saved to {model_path}")
    
    # Save final model
    final_path = os.path.join(model_dir, "snake_dqn_final.pth")
    agent.save(final_path)
    print(f"Final model saved to {final_path}")
    
    # Save training metrics
    np.save(os.path.join(model_dir, "rewards_history.npy"), np.array(rewards_history))
    np.save(os.path.join(model_dir, "loss_history.npy"), np.array(loss_history))
    np.save(os.path.join(model_dir, "eval_results.npy"), np.array(eval_results))

def evaluate_agent(agent, env, num_episodes, device):
    total_reward = 0
    
    for _ in range(num_episodes):
        state = env.reset()
        episode_reward = 0
        done = False
        
        while not done:
            action = agent.act(state, evaluation=True)
            next_state, (reward, _), done, _ = env.step(action2=action)
            state = next_state
            episode_reward += reward
        
        total_reward += episode_reward
    
    return total_reward / num_episodes

if __name__ == "__main__":
    train()