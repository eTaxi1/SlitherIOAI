from CustomEnv import CustomEnv
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
#ray.init(object_store_memory=10 * 10**9)


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
    return ParallelPettingZooEnv(CustomEnv('human'))
#print(f'SPACE: {ParallelPettingZooEnv(CustomEnv('human')).action_space}')
register_env(
    "SnakeEnv-v0",
    env_creator
)


if __name__ == "__main__":
    print("HERE 1#################################################################")
    base_config = (
        PPOConfig()
        .training(
            gamma=0.9,
            lr=0.0005,
            model={
                "use_lstm": True,
                "lstm_cell_size": 256,
                "max_seq_len": 20,
                "lstm_use_prev_reward": True,
                #"lstm_use_prev_action": True,
                "fcnet_hiddens": [256],
                "fcnet_activation": "relu"
                #"_disable_action_flattening": True
            },
            train_batch_size=2048,
            sgd_minibatch_size=256,
            num_sgd_iter=20,
            vf_clip_param=10.0,
            entropy_coeff=0.01
        )
        .environment("SnakeEnv-v0")
        .framework(
            "torch"
        )
        .env_runners(
            env_to_module_connector=lambda env: FlattenObservations(multi_agent=True),
            num_env_runners = 1,
            num_cpus_per_env_runner = num_cpus-1,
            num_envs_per_env_runner = 1,
            sample_timeout_s = 10,
            rollout_fragment_length=200
        )
        .multi_agent(
            policies={"agent_0"},
            
            policy_mapping_fn=lambda aid, *args, **kwargs: "agent_0",
            count_steps_by="env_steps"
        )
        .evaluation(
            evaluation_num_env_runners=0,
            evaluation_interval=0
        )
        .callbacks(
            RenderCallback
        )
    )
    print('HERE 2 ##############################')
    algo = base_config.build()
    print('HERE 3 ###############################')
    algo.restore("Training11/")
    #print(algo.evaluate())
    print('RESTORED#######################')
    for _ in range(10000):
        print(algo.train())
        if _ % 12== 0:
            print('HERE IN SAVE')
            try:
                algo.save(f"Training{_}/")
            except Exception as e:
                print(f'Error during saving: {e}')
        print(f"HERE {_+1}")
    print('HERE 4 ############################')
    #algo.evaluate()
    print('HERE 5 ############################')