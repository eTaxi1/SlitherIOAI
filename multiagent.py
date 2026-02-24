from pettingzoo.utils.conversions import parallel_to_aec
from ray import tune
from ray.rllib.algorithms.ppo import PPO
from ray.rllib.env import MultiAgentEnv
from ray.rllib.env import PettingZooEnv
from ray.rllib.env import ParallelPettingZooEnv
from ray.tune.registry import register_env
import supersuit as ss
import numpy as np
from Enviornment.CustomEnv import CustomEnv
import ray


env = CustomEnv('human')
register_env(
    "SnakeEnv-v0",
    lambda _: ParallelPettingZooEnv(env))
#register_env("SnakeEnv-v0", lambda config: env_creator(config))
#register_env("snake_env", lambda config: PettingZooEnv(env_creator(config)))
ray.init(object_store_memory=100 * 1024 * 1024)

#env = PettingZooEnv(env_creator({}))
temp_env = 9

obs_space = temp_env.observation_space
act_space = temp_env.action_space
config = {
    "env": "SnakeEnv-v0",
    "framework": "torch",
    "multiagent":{
        "policies":{
            "shared_policy": (None, obs_space, act_space, {}),
        },
        "policy_mapping_fn": lambda agent_id,  *args, **kwargs: "shared_policy",
    },
    "num_workers": 2,
    "num_gpus": 0,
}
print('###########################################Stop 0##############################################################')
ppo_trainer = PPO(config=config)
print('###########################################Stop 1##############################################################')


for i in range(1000):
    result = ppo_trainer.train()
    print(f'Iteration: {i}  |  Mean_Reward: {result['episode_reward_mean']}')
print('###########################################Stop 2##############################################################')

ppo_trainer.save("ppo_multiagent")

ppo_trainer.restore("ppo_multi_agent/checkpoint_001000/checkpoint-1000")

'''obs = env.reset()

dones = {"__all__": False}


while not dones["__all__"]:
    actions = {}
    
    for agent_id, agent_obs in obs.items():
        action = ppo_trainer.compute_single_action(agent_obs, policy_id="shared_policy")
        actions[agent_id] = action
        
    obs, rewards, dones, infos, = env.step(actions)
    env.render()
    print(f"Rewards: {rewards}, Dones: {dones}")'''