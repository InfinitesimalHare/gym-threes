This is a customised Open-AI gym environment which simulate the puzzle video game [Threes](https://en.wikipedia.org/wiki/Threes) developed by Sirvo. 

# The Rules
The rules adoped in this simulaiton follows the speculation of [kamikaze28 on toucharcade](https://toucharcade.com/community/threads/threes-by-sirvo-llc.218248/page-27#post-3140044)

* **Board:** 4-by-4
* **Tiles:** with values 1, 2, 3, 6, 12,...
* **Operation:** Direction keys ['Up', 'Down', 'Left', 'Right']
* **Tile merging:** '1' and '2' merges and create '3'. The rest of the tiles merge with themselves. 
* **Scoring:** Tile '3*2^i' has a score of 3^(i+1). Tiles '1' and '2' have score 0. The score of the board is the sum of all tiles on the board.
* **Objective:** Achienve the highest score. 
* **How new tiles are drawn:** At the start of the game, a stack of 12 tiles consists of '1'* 4, '2'* 4 and '3' * 4 is drawn and randomly shuffled. This is called 'Basic card' stack. The first 9 tiles of the 'Basic card' stack are randomly inserted to the starting board. When the highest tile on the board is higher or equal to 48, there is a 1/21 probability that the next tile is drawn from 'Bonus card' stack. Otherwise, the new tiles are always drawn from the first card left in the 'Basic card' stack. If there is no tile left, 'Basic card' stack are refilled immediately with 12 new tiles.
'Bonus card' contains tiles from 6 to 'largest tile on the board divided by 8', drawn uniformly at random.

# Installation
```
cd 'parent folder of gym-threes'
pip install -e gym-threes
```
The package is tested on Python 3.9.1 and gym 0.10.5

# How to use 
```
import gym
import gym_threes
import pickle
from pathlib import Path


env = gym.make('threes-v0')

obs = env.reset()
history = [[obs[0], obs[1], 0, None, None]]
env.render() #render(mode = 'uint64) print the current state of the board in STDOUT. reder(mode='human') returns a matplotlib figure object containing a screenshot of the current state of the game.
while True:
    action = env.np_random.choice(env.legalNextMoves)
    obs, reward, done, _ = env.step(action)
    history.append([obs[0], obs[1], env.score, action, reward])
    env.render()
    if done:
        break

with open('outfile', 'wb') as fp:
    pickle.dump(history, fp)

# The following renders a Tk GUI that allows human player to play the game. The history of each play-through is saved as a pickle file in 'gym-threes/gym_threes/records'.
env.reset()
env.render(mode='human_interact')
```
If you want to generate an animation for the whole play-through, you can save the histroy as a list `history`, whose i-th entry is the status of the game after i steps, in the format `[env.board_h, env.nextTile, env.score, action, reward]`
```
from render_img.py import *
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

recorder = RecordThrees(history)
anim = FuncAnimation(recorder.fig, func = recorder.anim_update, frames=range(len(history)), interval=1000)
writergif = PillowWriter(fps=1) 
anim.save('output.gif', writer=writergif)
# anim.save('animation.mp4')
plt.show()
```

# Files
- *threes_env.py* defines the gym environment.
- *LeftTable.json, RightTable.json, scoreTable.json* contain dictionary of how the board rows react to actions and their scoring. This is to reduce the running time of env.step(action)
- *threes_tableGenerator.py*: Running this script alone generates the three .json files above.
- *Board_tkinter.py* creates the tkinter GUI for a human-interactive game.
- *render_img.py* provides image of the current state and animation of the whole play-through of a game, given the game histroy as input.