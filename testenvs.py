""" Directly running this script allows the user to test the code in envs """

import gym_threes.envs.threes_env as threes
import gym_threes.envs.render_img as img
from matplotlib.animation import FuncAnimation, PillowWriter
from pathlib import Path
import pickle

env = threes.ThreesEnv()

# Demonstration of setting the random seed
print('An example of seeding:')
print(env.currentSeed)
env.render() #render(mode = 'uint64) print the current state of the board in STDOUT. reder(mode='human') returns a matplotlib figure object containing a screenshot of the current state of the game.
for i in range(3):
    action = env.np_random.choice(env.legalNextMoves)
    print('Action: ', action)
    obs, reward, done, _ = env.step(action)
    env.render() 
print(env.currentSeed)
env.seed(seed = env.currentSeed)
print(env.currentSeed)
env.reset()
env.render()
for i in range(3):
    action = env.np_random.choice(env.legalNextMoves)
    print('Action: ', action)
    obs, reward, done, _ = env.step(action)
    env.render()
    fig = env.render('human')
    fig.savefig(Path(__file__).parent/'testoutput'/'img{}'.format(i))




# Run three fully random playthrough with middleStart = True, and save the large playthrough as .gif
print('The following is a fully random playthrough.')
env.seed(seed = env.currentSeed)
for i in range(3):
    obs = env.reset(middleStart= True)
    history = [[obs, env.nextTile, 0, None, None]]
    env.render()
    while True:
        action = env.np_random.choice(env.legalNextMoves)
        print('Action: ', action)
        obs, reward, done, _ = env.step(action)
        history.append([obs,  env.nextTile, env.score, action, reward])
        env.render()
        if done:
            break
recorder = img.RecordThrees(history)
anim = FuncAnimation(recorder.fig, func = recorder.anim_update, frames=range(len(history)), interval=1000)
writergif = PillowWriter(fps=1) 
outputdir = Path(__file__).parent/'testoutput'
anim.save( outputdir/'playthrough.gif', writer=writergif)

print('Now please play the same game by yourself.')
env.seed(seed = env.currentSeed)
env.reset()
env.render(mode='human_interact')

# Since the previous line open a tkinter window, the rest of the script will not run automatically.
outfile = 1
with open (Path(__file__).parent/'gym_threes'/'records'/'{}'.format(outfile), 'rb') as fp:
    history = pickle.load(fp)
recorder = img.RecordThrees(history)
anim = FuncAnimation(recorder.fig, func = recorder.anim_update, frames=range(len(history)), interval=1000)
writergif = PillowWriter(fps=1) 
anim.save(Path(__file__).parent/'testoutput'/'humaninteract.gif', writer=writergif)
