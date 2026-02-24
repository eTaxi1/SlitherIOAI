import re
import os
import ray

os.environ["RAY_PICKLE_VERBOSE_DEBUG"] = "1"

from Enviornment.CustomEnv import CustomEnv
from ray.rllib.algorithms.callbacks import DefaultCallbacks
from ray.rllib.connectors.env_to_module import FlattenObservations
from ray.rllib.core.rl_module.multi_rl_module import MultiRLModuleSpec
from ray.rllib.core.rl_module.rl_module import RLModuleSpec
from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv
from ray.rllib.utils.test_utils import (
    add_rllib_example_script_args,
    run_rllib_example_script_experiment,
)
from ray.tune.registry import get_trainable_cls, register_env





class RenderCallback(DefaultCallbacks):
    def __init__(self):
        super().__init__()
        self.render_interval = 1
        self.episode_steps = 0
    
    def on_episode_step(self, *, worker, base_env, episode, env_index, **kwargs):
        # Call the render function on the first environment
        self.episode_steps+=1
        for env in base_env.get_sub_environments():
            # Assumes only one environment instance
            if hasattr(env, "render"):
                env.render()
        
        if episode.is_done(env_index):
            self.episode_steps = 0





parser = add_rllib_example_script_args(
    default_iters=50,
    default_timesteps=200000,
    default_reward=6.0,
)
parser.add_argument(
    "--use-lstm",
    action="store_true",
    help="Whether to use an LSTM wrapped module instead of a simple MLP one. With LSTM "
    "the reward diff can reach 7.0, without only 5.0.",
)

RAY_PICKLE_VERBOSE_DEBUG=1

def env_creator(_):
    return ParallelPettingZooEnv(CustomEnv('human'))
register_env(
    "SnakeEnv-v0",
    env_creator
)


if __name__ == "__main__":
    args = parser.parse_args()

   # assert args.num_agents == 20
    #assert (
       # args.enable_new_api_stack
   # ), "Must set --enable-new-api-stack when running this script!"
    print("HERE 1#################################################################")
    base_config = (
        get_trainable_cls(args.algo)
        .get_default_config()
        .environment("SnakeEnv-v0")
        .rollouts(
            num_rollout_workers = 1
        )
        .resources(
            num_cpus_per_worker=7
        )
        .env_runners(
            env_to_module_connector=lambda env: FlattenObservations(multi_agent=True),
        )
        .multi_agent(
            policies={"agent_0"},
            # `player_0` uses `p0`, `player_1` uses `p1`.
            policy_mapping_fn=lambda aid, *args, **kwargs: "agent_0",
        )
        .training(
            vf_loss_coeff=0.005,
        )
        .rl_module(
            model_config_dict={
                "use_lstm": args.use_lstm,
                # Use a simpler FCNet when we also have an LSTM.
                "fcnet_hiddens": [32] if args.use_lstm else [256, 256],
                "lstm_cell_size": 256,
                "max_seq_len": 15,
                "vf_share_layers": True,
            },
            rl_module_spec=MultiRLModuleSpec(
                module_specs={
                    "agent_0": RLModuleSpec(),
                }
            ),
        )
        #.callbacks(RenderCallback)
    )
    
    #base_config.callbacks = RenderCallback
    print('here 2###############################################################')
    run_rllib_example_script_experiment(base_config, args)
    
    print("END#######################################")