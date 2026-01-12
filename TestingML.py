import CustomEnv
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import DummyVecEnv
from stable_baselines3.common.env_checker import check_env
from pettingzoo.utils.conversions import parallel_to_aec
from supersuit import pad_observations_v0, pad_action_space_v0, pettingzoo_env_to_vec_env_v1
import supersuit as ss
# Create the environment
#parallel_env = CustomEnv.CustomEnv("human")
def env():
    env_ = CustomEnv.CustomEnv("human")
    env_ = ss.pettingzoo_env_to_vec_env_v1(env_)
    env_ = ss.concat_vec_envs_v1(env_, 1, base_class="stable_baselines3")
    return env_
# Convert the parallel environment to AEC environment for compatibility
#aec_env = parallel_to_aec(parallel_env)
#aec_env.reset()
#print('HERE:  ', aec_env.observation_space(aec_env.agents[0]))
# Add necessary wrappers
#wrapped_env = pad_observations_v0(aec_env)
#wrapped_env = pad_action_space_v0(wrapped_env)

# Convert to a format suitable for stable-baselines3
#vec_env = pettingzoo_env_to_vec_env_v1(parallel_env)
#vec_env = DummyVecEnv([lambda: vec_env])  # Vectorize the environment
vec_env = env()
# Check if the environment follows the Gym API
print("########################Check######################")
check_env(vec_env)

# Create the PPO model
print("####################MODEL#######################")

model = PPO("MlpPolicy", vec_env, verbose=1)
# Train the model
print("################LEARN###################")
model.learn(total_timesteps=10000)

# Evaluate the trained model
'''bservations = parallel_env.reset()
while parallel_env.agents:
    # Use the trained model to predict actions
    actions = {agent: model.predict(observations[agent])[0] for agent in parallel_env.agents}
    
    observations, rewards, terminations, truncations, infos = parallel_env.step(actions)

# Close the environment
parallel_env.close()'''
