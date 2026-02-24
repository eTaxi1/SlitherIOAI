from Enviornment.CustomEnv import CustomEnv
from ray.rllib.core.rl_module.multi_rl_module import MultiRLModuleSpec
from ray.rllib.core.rl_module.rl_module import RLModuleSpec
from ray.rllib.core import DEFAULT_MODULE_ID
from ray.rllib.algorithms.callbacks import DefaultCallbacks
from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv
from ray.tune.registry import get_trainable_cls, register_env
from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.connectors.env_to_module import FlattenObservations
import ray
import os
ray.shutdown()
os.system("ray stop")

num_cpus = os.cpu_count()
runtime_env = {"py_modules": ["Enviornment/"]}
ray.init(log_to_driver=False, runtime_env=runtime_env)
SAVE_INTERVAL = 50
ITERATIONS = 10000

class RenderCallback(DefaultCallbacks):
    def __init__(self):
        super().__init__()
        self.render_interval = 1
        self.episode_steps = 0
    
    def on_episode_step(self, *, worker, base_env, episode, env_index, **kwargs):
        # Call the render function on the first environment
        
        for env in base_env.get_sub_environments():
            # Assumes only one environment instance
            if(self.episode_steps >=0):
                if hasattr(env, "render"):
                    env.render()
        
        if episode.is_done(env_index):
            self.episode_steps+=1
            print(f'Episode: {self.episode_steps}')

def env_creator(_):
    return CustomEnv('None')
#print(f'SPACE: {ParallelPettingZooEnv(CustomEnv('human')).action_space}')

#env=CustomEnv("None")

if __name__ == "__main__":
    print("Starting Configuration... #################################################################")
    register_env(
        "SnakeEnv-v0",
        env_creator
    )

    base_config = (
        PPOConfig()
        .api_stack(
            enable_rl_module_and_learner=True,
            enable_env_runner_and_connector_v2=True
        )
        .learners(
            num_learners=1,
            num_gpus_per_learner=1
        )
        .rl_module(
            rl_module_spec=MultiRLModuleSpec(
                rl_module_specs={
                DEFAULT_MODULE_ID: RLModuleSpec(
                    model_config={
                        "use_lstm": True,
                        "lstm_cell_size": 256,
                        "max_seq_len": 20,
                        "lstm_use_prev_reward": True,
                        "fcnet_hiddens": [256],
                        "fcnet_activation": "relu",
                        #"lstm_use_prev_action": True,
                        #"_disable_action_flattening": True
                    }
                )
            })

        )
        .training(
            gamma=0.9,
            lr=0.0005,
            minibatch_size=64,
            train_batch_size_per_learner=512,
            num_epochs=20,
            vf_clip_param=10.0,
            entropy_coeff=0.01,
        )
        .environment(env="SnakeEnv-v0")
        .framework(
            "torch"
        )
        .env_runners(
            env_to_module_connector=lambda env, spaces, device: FlattenObservations(multi_agent=True),
            num_env_runners = 1,
            num_gpus_per_env_runner = 1,
            num_envs_per_env_runner = 1,
            sample_timeout_s = 30,
            rollout_fragment_length=256
        )
        .multi_agent(
            #policies={"agent_0"},
            
            policy_mapping_fn=lambda aid, *args, **kwargs: DEFAULT_MODULE_ID,
            count_steps_by="env_steps"
        )
        .evaluation(
            evaluation_num_env_runners=0, # Dont evaluate during training
            evaluation_interval=0
        )
        #.callbacks( ### Rendering
         #   RenderCallback
        #)
    )
    print('Starting Build... ##############################')
    algo = base_config.build_algo()
    print('Finished Build... ###############################')
    #algo.restore("Training11/")
    #print(algo.evaluate())
    print('Finished Restoring - if applicable #######################')
    for iter in range(ITERATIONS):
        print('Before Training #############################')
        result = algo.train()
        print("After Training #######################")
        if iter % SAVE_INTERVAL== 0:
            print('HERE IN SAVE')
            try:
                algo.save(f"checkpoints/Training{iter}")

            except Exception as e:
                print(f'Error during saving: {e}')
        print(f"Iteration: {iter+1}")
    print('Finished Training ############################')
    #algo.evaluate()
    #print('Finished Evaluation ############################')