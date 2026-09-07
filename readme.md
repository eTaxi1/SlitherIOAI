# 1. Project Overview: SlitherIOAI

 This is SlitherIOAI, A Multi-Agent Reinforcement Learning Project inspired by the popular Online multiplayer game Slither.IO.

The goal of this project was to show that is was possible to use Machine learning to learn and devise complex strategys within a non-trivial multiplayer game.

# 2. The Agents In Action

# 3. Current Status

# 4. Installation
The project was developed on Windows using Python 3.12.2. Run the command below from the project's root directory in PowerShell.

```
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

## Install PyTorch
The environment uses PyTorch 2.10.0 with Cude 12.8:
```
python -m pip install torch==2.10.0 --index-url https://download.pytorch.org/whl/cu128
```
GPU acceleration requires compatible NVIDIA GPU and driver. 
## Project Dependencies
```
python -m pip install -r requirements.txt
python -m pip check
```
The requirements cover Ray RLlib, PyTorch, Gymnasium, NumPy, Pygame, PettingZoo and TensorBoard.

Run the project from the root directory so relative paths are resolved correctly.
# 5. How to Run the Application
## Start Training
```
python ML4.py
```
As Training is underway, the terminal displays learner losses and gameplay metrics, including survival time, food collected and death causes. Training may take some time.

## Load and Render a Checkpoint
All checkpoints are saved in the checkpoints directory.

Set ```CHECKPOINT``` in ```render_checkpoint.py``` to the policy you wish to watch.

```
CHECKPOINT = (
    ROOT / "checkpoints" / "<YOUR_CHECKPOINT_GOES_HERE>"
    / "learner_group" / "learner"
    / "rl_module" / "shared_policy"
)
```
Then run:
```
python render_checkpoint.py
```
While the checkpoint is running you can control the viewer with the following controls:
| Controls | Action |
|---|---|
| Tab | Change Sanke View |
| Mouse wheel | Zoom in or out |
| Space | Pause or resume |
| Escape | Exit the viewer |
# 6. The Model Configuration
This is a multiple agent system where the agents share a common PPO policy and learn from observations from their surroundings.

**Algoritm:** PPO through Ray RLlib.

**Observation space:** position, direction, body, nearby food & enemies, speed, and boost.

**Action Space:** Target Movement Coordinates and Boost on/off.

**Rewards:** survival, food collection, death penalties, and interactions with opponents.

# 7. Configuration

# 8. Metrics and Evaluation

# 9. Checkpoints

# 10. Known limitations

# 11. Project Structure, roadmap and license


