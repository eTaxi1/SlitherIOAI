from CustomEnv import CustomEnv
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env


#env = make_vec_env(lambda: CustomEnv(),n_envs=75)
env = CustomEnv()
#model = PPO(ppo_params)
model = {agent: PPO("MlpPolicy", env, verbose=1) for agent in env.agents}
n_episodes = 10000
max_timesteps = 1000
for episode in range(n_episodes):
    obs = env.reset()
    total_rewards = {agent: 0 for agent in env.agents}
    for t in range(max_timesteps):
        actions =  {}
        for agent in env.agents:
            action, _states = model[agent].predict(obs[agent])
            actions[agent] = action
        next_obs, rewards, dones, infos = env.step(actions)
        
        for agent in env.agents:
            total_rewards[agent] += rewards[agent]
            
        obs = next_obs
        
        if all(dones.values()):
            break
    print(f'Episode {episode + 1}: Total Rewards: {total_rewards}')
    
    for agent in env.agents:
        model[agent].learn(total_timesteps=100)
        
for agent, model in model.items():
    model.save(f'PPO_{agent}')
