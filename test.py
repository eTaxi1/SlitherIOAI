from pettingzoo.test import parallel_api_test
from CustomEnv import CustomEnv
import numpy as np
env = CustomEnv("human")
parallel_api_test(env, num_cycles=1000)