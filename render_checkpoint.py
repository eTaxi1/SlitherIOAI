from pathlib import Path
import os

import numpy as np
import pygame
import torch

from Enviornment.CustomEnv import CustomEnv
from ray.rllib.core.columns import Columns
from ray.rllib.core.rl_module.rl_module import RLModule
from ray.rllib.utils.numpy import flatten_inputs_to_1d_tensor
from ray.rllib.utils.spaces.space_utils import (
    get_base_struct_from_space,
    unsquash_action,
)


ROOT = Path(__file__).resolve().parent
CHECKPOINT = (
    ROOT / "checkpoints" / "Training20"
    / "learner_group" / "learner"
    / "rl_module" / "shared_policy"
)

FPS = 60
DETERMINISTIC = True  # False samples actions, as during training.


class FollowCamera:
    def __init__(self, dims, radius):
        self.width, self.height = dims
        self.radius = radius
        self.x = 0
        self.y = 0
        self.zoom = 0.8

    def translate(self, x, y):
        return (
            (x - self.x) * self.zoom + self.width / 2,
            (y - self.y) * self.zoom + self.height / 2,
            self.radius * self.zoom,
        )


def main():
    # Your game loads textures using paths relative to the project.
    os.chdir(ROOT)

    if not CHECKPOINT.is_dir():
        raise FileNotFoundError(f"Checkpoint not found: {CHECKPOINT}")

    module = RLModule.from_checkpoint(str(CHECKPOINT))
    module.to("cpu")
    module.eval()

    if module.is_stateful():
        raise RuntimeError(
            "This viewer expects the non-LSTM checkpoint."
        )

    pygame.init()
    env = CustomEnv("human")
    camera = FollowCamera(env.game.dims, env.mapSize)
    env.game.freeCamera = camera

    observation_struct = get_base_struct_from_space(
        env.observation_spaces["agent_0"]
    )
    action_struct = get_base_struct_from_space(
        env.action_spaces["agent_0"]
    )
    distribution_class = module.get_inference_action_dist_cls()

    clock = pygame.time.Clock()
    observations, _ = env.reset()
    running = True
    paused = False
    follow_index = 0
    episode_number = 1
    episode_reward = 0.0

    # Create the window before processing its events.
    env.render()
    pygame.display.set_caption("Training50 — checkpoint viewer")

    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        paused = not paused
                    elif event.key == pygame.K_TAB:
                        follow_index += 1
                elif event.type == pygame.MOUSEWHEEL:
                    camera.zoom = float(np.clip(
                        camera.zoom * (1.2 ** event.y), 0.1, 3.0
                    ))

            if not running:
                break

            if not paused:
                # Only request actions for currently active snakes.
                agent_ids = list(env.agents)

                flat_observations = np.stack([
                    flatten_inputs_to_1d_tensor(
                        inputs=observations[agent],
                        spaces_struct=observation_struct,
                        batch_axis=False,
                    )
                    for agent in agent_ids
                ]).astype(np.float32)

                with torch.inference_mode():
                    output = module.forward_inference({
                        Columns.OBS: torch.from_numpy(flat_observations)
                    })

                    distribution = distribution_class.from_logits(
                        output[Columns.ACTION_DIST_INPUTS]
                    )
                    if DETERMINISTIC:
                        distribution = distribution.to_deterministic()

                    sampled = distribution.sample()

                actions = {}
                for index, agent in enumerate(agent_ids):
                    raw_action = {
                        "move": sampled["move"][index].cpu().numpy(),
                        "speed_boost": int(
                            sampled["speed_boost"][index].item()
                        ),
                    }

                    # Match PPO's action scaling during training.
                    actions[agent] = unsquash_action(
                        raw_action, action_struct
                    )

                observations, rewards, terminated, truncated, _ = (
                    env.step(actions)
                )
                episode_reward += sum(rewards.values())

                if terminated["__all__"] or truncated["__all__"]:
                    print(
                        f"Episode {episode_number}: "
                        f"{env.num_moves} steps, "
                        f"total reward {episode_reward:.2f}"
                    )
                    episode_number += 1
                    episode_reward = 0.0
                    observations, _ = env.reset()

            if env.playersIn:
                target = env.playersIn[
                    follow_index % len(env.playersIn)
                ]
                camera.x = target.rect.centerx
                camera.y = target.rect.centery

            env.render()
            clock.tick(FPS)

    finally:
        env.close()
        pygame.quit()


if __name__ == "__main__":
    main()