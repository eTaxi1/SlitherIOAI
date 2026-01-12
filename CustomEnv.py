import numpy as np
import pygame
from collections import OrderedDict
from pettingzoo.utils import ParallelEnv
from pettingzoo.utils import AECEnv
#from pettingzoo.utils import spaces
import gymnasium as gym
from gymnasium import spaces as gym_spaces
from MainGame import MainGame
import math
from Food import Food
from Snake import Snake
from Segment import Segment
NUM_ITERS = 2000
class CustomEnv(ParallelEnv):
    metadata = {
    "rendermode": ["human"],  # List of supported render modes
    "name": "SnakeEnv-v0",                 # Optional: Name of the environment
    }
    def __init__(self, rendermode):
        super().__init__()
        self.render_mode = rendermode
        self.num_moves = 0
        self.clock = pygame.time.Clock()
       
        # Define agent names based on the number of players
        self.game = MainGame()
        #self.game.init()
        self.window = pygame.display.set_mode(self.game.dims)
        self.grid = self.game.get_grid()
        self.food = self.game.get_food_states()
        self.mapSize = self.game.range
        self.epoch = 0
        self.num_players = len(self.game.get_players())
        self.num_food = len(self.food)
        self.playersIn = self.game.players.copy()
        self.agents = [f'agent_{i}' for i in range(self.num_players)]
        self.possible_agents = self.agents[:]
        self.agent_to_player = {f'agent_{i}': self.game.players[i] for i in range(self.num_players)}
        
        # Define action space
        self.action_spaces = {
            agent: gym_spaces.Dict({
                "move": gym_spaces.Box(low=-self.mapSize, high=self.mapSize, shape=(2,), dtype=np.float32),  # Continuous (x, y)
                "speed_boost": gym_spaces.Discrete(2)  # Discrete on/off
            })
            for agent in self.agents
        }
        
        # Define observation space
        # Observations include position, distances, angles, grid info, and turning speed
        self.observation_spaces = {
            agent: gym_spaces.Dict({
                "head_position": gym_spaces.Box(low=-1, high=1, shape=(4,), dtype=np.float32),
                "current_size": gym_spaces.Box(low=0, high=1, shape=(1,), dtype=np.float32),
                "body_positions": gym_spaces.Box(low=-1, high=1, shape=(50, 4), dtype=np.float32),  # Assuming 8 body segments
                "enemy_head": gym_spaces.Box(low=-1, high=1, shape=(self.num_players - 1, 8), dtype=np.float32),
                "enemy_body":gym_spaces.Box(low=-1, high=1, shape=((self.num_players-1)*50, 8), dtype=np.float32),# distance and angle to enemy head and body
                "food_info": gym_spaces.Box(low=-1, high=1, shape=(self.num_food*5, 6), dtype=np.float32),  # distance and angle to nearby food (assuming max 50 foods)
                "turning_speed": gym_spaces.Box(low=-1, high=1, shape=(1,), dtype=np.float32),
                "snake_speed": gym_spaces.Box(low=0, high=1, shape=(1,), dtype=np.float32),
                "boost_remaining": gym_spaces.Box(low=0, high=1, shape=(1,), dtype=np.float32)
            })
            for agent in self.agents
        }
        #print(np.shape(self.observation_spaces))
        #print(self.observation_spaces[self.possible_agents[0]])
        
        #self.observation_space = self.observation_spaces[self.agents[0]]
        #self.action_space = self.action_spaces[self.agents[0]]
        self._seed = None
        # Initialize environment state variables
        self.reset()

    
    def observation_space(self, agent):
        return self.observation_spaces[agent]
    
    def action_space(self,agent):
        return self.action_spaces[agent]
    
    def reset(self, seed = None, options=None):
        # Reset the game state
        self._seed = seed
        if seed is not None:
            np.random.seed(seed)
        
        self.game.reset()  # This will initialize players, food, etc.
        self.grid = self.game.get_grid()
        self.food = self.game.get_food_states()
        self.playersIn = self.game.players.copy()
        #self.game.init()
        self.timesteps_no_direction_change = {agent: 0 for agent in self.agents}
        self.epoch += 1
        #print(f'{self.epoch}')
        self.num_moves = 0
        #self.lifetime = {agent: 0 for agent in self.agents}
        self.score_change_over_n_timesteps = {agent: 0 for agent in self.agents}
        #print('here')
        self.agents = self.possible_agents[:]
        #print("MADE IT")
        self.agent_to_player = {f'agent_{i}': self.game.players[i] for i in range(self.num_players)}
        observations = {agent: self._get_observation(agent) for agent in self.agents}
        #print("Reset Observations:", observations)
        infos = {agent: {} for agent in self.agents}
        return observations, infos

    def step(self, actions):
        # Implement how actions affect the environment state
        #print(f'{self.num_moves}')
        rewards = {agent: 0 for agent in self.agents}
        dones = {agent: False for agent in self.agents}
        infos = {agent: {} for agent in self.agents}
        #print(f'Food Start: {len(self.food)}')
        # Update environment state based on agent actions
        for agent, action in actions.items():
            player = self.agent_to_player[agent]
            #player = self.game.players[int(agent_id.split('_')[1])]
            #self.lifetime[agent] += 1
            self._apply_action(player, action)
            reward, dones = self._calculate_reward(player, dones, agent)
            rewards[agent] += reward
             
        if(len(self.food) < self.num_food):
            newFood = self.game.stableFood()
            self.food.append(newFood)
            self.grid.addToCell(newFood)

        # Remove dead agents
        self.agents = [agent for agent in self.agents if not dones[agent]]
        
        
        
        # Get new observations
        observations = {agent: self._get_observation(agent) for agent in self.agents}
        self.num_moves +=1
        env_truncation = self.num_moves >= NUM_ITERS
        truncations = {agent: env_truncation for agent in self.agents}
        if env_truncation:
            dones = {agent: True for agent in self.agents}
        infos = {agent: {} for agent in self.agents}
        self.agents = [agent for agent in self.agents if not truncations[agent]]
        self.agent_to_player = {agent: self.agent_to_player[agent] for agent in self.agents}
        #print("Step Observations:", observations)
        #print("Rewards:", rewards)
        #print("Dones:", dones)
        #print("Infos:", infos)
        #print(f'Food End: {len(self.food)}')
        return observations, rewards, dones, truncations, infos

    def _apply_action(self, player, action):
        # Apply the action to update the player's state
        move_action = action["move"]
        speed_boost = action["speed_boost"]
        self.grid.deleteFromCell(player)
        for seg in player.segments:
            self.grid.deleteFromCell(seg)                   
        direction = [move_action[0] - player.rect.x, move_action[1] - player.rect.y] #### Moving snake it the direction of xy
        l = (direction[0]**2 + direction[1]**2) ** (1/2)
        direction[0] /= l
        direction[1] /= l
        desired_angle = math.degrees(math.atan2(direction[1], direction[0]))
        angle_difference = (desired_angle - player.angle + 180) % 360 - 180
        if abs(angle_difference) > player.turnSpeed:
            player.angle += player.turnSpeed if angle_difference > 0 else -player.turnSpeed
        else:
            player.angle = desired_angle
        player.angle = math.radians(player.angle)
        # Update player state based on action
        player.boost = bool(speed_boost)
        newFood = player.boostSnake()
        if newFood != None:
            self.food.append(newFood)
            self.grid.addToCell(newFood)
        player.rect.x += math.cos(player.angle) * player.speed
        player.rect.y += math.sin(player.angle) * player.speed
        player.angle = math.degrees(player.angle)
        player.updateSegments()
        self.grid.addToCell(player)
        for seg in player.segments:
            self.grid.addToCell(seg)
        # Check if direction has changed
        current_direction = direction
        if np.array_equal(np.array(current_direction), np.array(player.direction)):
            self.timesteps_no_direction_change[player] += 1
        else:
            self.timesteps_no_direction_change[player] = 0
        player.direction = direction

    def getGridObjects(self, snake):
        return self.grid.getNearByCellPopulation(snake)
     
    def _get_observation(self, agent_id):
        # Construct the observation dictionary for the given agent
        #player = self.game.players[int(agent_id.split('_')[1])]
        player = self.agent_to_player[agent_id]
        # Assuming MainGame or Snake class has necessary methods to fetch data for observations
        foodInfo, SnakeHeadInfo, SnakeBodyInfo = self.getGridObjects(player) # ADD DETAILS LIKE SIZE OF FOOD/BODYPART
       # print(f'EnemyHead: {SnakeHeadInfo}      ||||||   EnemyBody: {SnakeBodyInfo}')
        boost_remaining = (player.score-10) // 2
        max_boost = 10000
        max_w = 100
        body_pos = np.zeros((50, 4))
        body_pos[:len(player.segments), :] = np.array([[seg.rect.x/self.mapSize, seg.rect.y/self.mapSize, seg.direction[0], seg.direction[1]] for seg in player.segments])
        
        num_enemy = self.num_players - 1
        enemy_head = np.zeros((num_enemy, 8), dtype=np.float32)
        enemy_body = np.zeros((num_enemy * 50, 8), dtype=np.float32)
        
        if len(SnakeHeadInfo) > 0:
            enemy_head[:len(SnakeHeadInfo)] = SnakeHeadInfo
        if len(SnakeBodyInfo) > 0:
            enemy_body[:len(SnakeBodyInfo)] = SnakeBodyInfo
        food_pos = np.zeros((self.num_food*5, 6))
        #print(f'Food in grid: {len(foodInfo)}     |    Food in game: {len(self.food)}')
        if len(foodInfo)>0:
            food_pos[:len(foodInfo), :] = np.array(foodInfo)
        observation = {
            "head_position": np.array([player.rect.x/self.mapSize, player.rect.y/self.mapSize, player.direction[0], player.direction[1]]),
            "current_size":np.array([player.rect.w/max_w]),
            "body_positions": body_pos,
            "enemy_head": enemy_head,
            "enemy_body": enemy_body,
            "food_info": food_pos,
            "turning_speed": np.array([player.turnSpeed / (5)]),
            "snake_speed": np.array([player.speed / (2*player.dspeed)]),
            "boost_remaining": np.array([boost_remaining/max_boost])
        }
        #print(observation)
        
        return observation

    def _calculate_reward(self, player, dones, agent_id):
        cellpop = self.grid.getCellPopulation(player)
        reward = 0
        reward += 0.01
        if self._out_of_bounds(player): ## penalty for dying on boundary  
            reward-=40
            self.grid.deleteFromCell(player)
            for seg in player.segments:
                self.grid.deleteFromCell(seg)
            dones[agent_id] = True
            self.playersIn.remove(player)
            normReward = reward / 100
            return normReward, dones
        for pop in cellpop:
            if player.rect.colliderect(pop.rect):
                if type(pop) is Food: # If player eats food give reward
                    self.food.remove(pop)
                    self.grid.deleteFromCell(pop)
                    player.score += round(pop.score/10) 
                    seg = player.adjustSize()
                    if seg is not None:
                        self.grid.addToCell(seg)
                    reward+= 15 + 0.8*math.sqrt(pop.score/10)/100 #### TODO Adjust so that bigger food give higher rewards
                elif type(pop) is Segment: # If agent dies on body of another snake penalty
                    reward -= 70
                    dones[agent_id] = True
                    newFood = self.game.dropFood(player)
                    #print(f'Food Before Death: {len(self.food)}')
                    for new in newFood:
                        self.food.append(new)
                        self.grid.addToCell(new)
                    self.grid.deleteFromCell(player)
                    #print(f'Food after Death: {len(self.food)}')
                    for seg in player.segments:
                        self.grid.deleteFromCell(seg)
                    self.playersIn.remove(player)
                    normReward = reward / 100
                    return normReward, dones
        for snake in self.playersIn:
            if snake == player:
                continue
            for body in snake.segments: # Penalty for moving towards another agents body
                # Getting the direction and distance between agent head and body of other agents
                direction = [body.rect.x - player.rect.x, body.rect.y-player.rect.y]
                dist = (direction[0]**2 + direction[1]**2)**(0.5)
                direction[0] /= dist
                direction[1] /= dist
                # Getting the direction of the agent which is already normalised
                move_dir = player.direction
                #Calculating the dot product of the 2 directions to see if they are aligned
                #if they're aligned penalise based on how close to the body the snake is
                dot_product = (direction[0] * move_dir[0] + direction[1] * move_dir[1])
                if abs(dot_product) > 0.3  and dist < 60:
                    penalty = (1 - abs(dot_product)) * ((60 - dist)/60)
                    reward -= 0.05 * penalty
            for seg in player.segments: # Reward for another agents head moving towards the agents body and for killing another snake
                #Getting the direction and distnace between other agents head and agents segments
                direction = [snake.rect.x - seg.rect.x, snake.rect.y - seg.rect.y]
                dist = (direction[0]**2 + direction[1]**2)**0.5
                direction[0] /= dist
                direction[1] /= dist
                #Getting the direction of the agent which is already normalised
                move_dir = snake.direction
                #Calculating the dot product of the directions to see if they are aligned
                #if they're aligned reward based on how close to the other agent is to the body
                dot_product = (direction[0] * move_dir[0] + direction[1] * move_dir[1])
                if abs(dot_product) > 0.3 and dist < 60:
                    bonus = (1 - abs(dot_product)) * ((60 - dist)/60)
                    reward += 0.05 * bonus
                if snake.rect.colliderect(seg.rect): # If the other snake collides with the body reward the player
                    reward+= min(30+0.8*math.sqrt(snake.score),40)/100 ### TODO Adjust so killing bigger snakes give more rewards than smaller ones
        
        # Penalty for speed boost
        if player.boost==True:
            if(player.score < 30):
                reward_penalty = 2/100
            else:
                reward_penalty = 2-0.3* math.log(player.score-20, 2)/100
            reward-= reward_penalty  ### Adjust so that if are much bigger the boost Doesn't penalise as much 

        # Penalty for not changing direction for a certain timeframe
        if self.timesteps_no_direction_change[player] > 50:  # Example threshold of 10 timesteps
            reward -= 1/100  # Negative reward for lack of movement
            
        normReward = reward
        return normReward, dones

    def _out_of_bounds(self, player):
        # Check if the player's head position is out of bounds
        if(player.rect.x**2 + player.rect.y**2 > (self.mapSize-1)**2):
            return True
        return False

    def render(self, mode='human'):
        # Implement rendering logic to visualize the environment (optional)
        #self.window = self.game.window
        self.window.fill(self.game.winColour)
        camera = self.game.freeCamera
        transform = camera.translate(0,0)
        pygame.draw.circle(self.window, (75,75,75), (transform[0], transform[1]), transform[2], width=0)
        for f in self.food:
            f.draw(self.window, camera)
        for player in self.playersIn:
            player.draw(self.window, camera)
        font = pygame.font.Font(None, 100)
        Epoch_text = font.render(f'Current Epoch: {self.epoch-2}', True, (15, 15, 15))
        self.window.blit(Epoch_text, (10, 10))
        self.game.spectate.draw(self.window, camera)
        pygame.display.update()
        #self.clock.tick(30)
        #self.game.render()

    def close(self):
        # Implement any cleanup logic (optional)
        pass

