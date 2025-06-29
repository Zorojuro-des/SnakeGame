from snake_env import SnakeGame
from dqn_agent import DQNAgent
import pygame
import numpy as np
import sys
import torch

def main():
    # Setup device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Initialize environment and agent
    env = SnakeGame(width=36, height=36, gui=True)
    state_dim = len(env._get_state())
    action_dim = 4
    
    # Load trained agent (you'll need to update this path)
    agent = DQNAgent(state_dim, action_dim, device)
    try:
        agent.load("models/snake_dqn_final.pth")  # Update with your model path
        agent.epsilon = 0.01  # Minimal exploration during play
        print("AI model loaded successfully!")
    except:
        print("No trained model found. AI will play randomly.")
        agent = None
    
    clock = pygame.time.Clock()
    human_wins = 0
    ai_wins = 0
    draws = 0
    
    # Game state
    action1 = None
    
    print("🐍 RETRO SNAKE BATTLE 🐍")
    print("Controls: Arrow Keys to move, R to restart")
    print("Human (Green) vs AI (Magenta)")
    
    while True:
        state = env.reset()
        done = False
        
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    env.close()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        action1 = 0
                    elif event.key == pygame.K_RIGHT:
                        action1 = 1
                    elif event.key == pygame.K_DOWN:
                        action1 = 2
                    elif event.key == pygame.K_LEFT:
                        action1 = 3
                    elif event.key == pygame.K_r and env.done:
                        # Update win statistics
                        if env.winner == "Snake1":
                            human_wins += 1
                        elif env.winner == "Snake2":
                            ai_wins += 1
                        elif env.winner == "Draw":
                            draws += 1
                        
                        print(f"Stats - Human: {human_wins}, AI: {ai_wins}, Draws: {draws}")
                        state = env.reset()
                        done = False
                        action1 = None
                    elif event.key == pygame.K_ESCAPE:
                        env.close()
                        sys.exit()
            
            # Get AI action
            if agent:
                action2 = agent.act(state, evaluation=True)
            else:
                # Random AI if no model loaded
                action2 = np.random.randint(0, 4)
            
            # Take step
            state, (_, _), done, winner = env.step(action1, action2)
            action1 = None  # Reset human action
            
            # Render the game
            env.render()
            
            clock.tick(12)  # Slightly faster for better gameplay feel
        
        # Wait for restart after game over
        waiting = True
        while waiting and env.done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    env.close()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Update win statistics
                        if env.winner == "Snake1":
                            human_wins += 1
                        elif env.winner == "Snake2":
                            ai_wins += 1
                        elif env.winner == "Draw":
                            draws += 1
                        
                        print(f"Stats - Human: {human_wins}, AI: {ai_wins}, Draws: {draws}")
                        waiting = False
                    elif event.key == pygame.K_ESCAPE:
                        env.close()
                        sys.exit()
            
            # Continue rendering during wait
            env.render()
            clock.tick(60)

if __name__ == "__main__":
    main()
