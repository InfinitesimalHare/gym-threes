import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

import numpy as np
import pickle

bg_color={ # background colour of tiles
        '1': '#2796fe', # blue
        '2': '#fe4d27', # red
        '3+': '#fffcf0' # white
    }
color={ # character colour of tiles
        'largest': '#c40000',
        'else': '#000000',
        '1/2': '#ffffff'
    }
def maxTile(board_h) -> int:
    maxTile = 0
    for i in range(16):
        temp = board_h >> 4*i & 0xf
        maxTile = temp if temp>maxTile else maxTile
    return maxTile
class RecordThrees:
    def __init__(self, history) -> None:
        self.fig = plt.figure(figsize=(3,5))
        self.axesText =[]
        self.anim_init()
        self.history = history
    def render_img(self, history_row):
        """ INPUT: env.history, list of 
        [(current board, next tile in player's knowledge) , real next tile, current score, last action, last reward]
    """ 
        axes = self.fig.axes
        (board_h, next), _, currentScore =  history_row[0:3]
        nexttile_setting = ['', '#817d82', '#817d82'] 
        for i, axText in enumerate(self.axesText[4:]):
            digit = board_h >> 4*(15-i) & 0xf
            tile_setting = []*3 # [text, background colour, font colour]
            if digit==0:
                tile_setting = ['','#817d82', '#817d82'] #font colour doesn't matter here
            elif digit == 1:
                tile_setting = [str(digit), bg_color['1'], color['1/2']]
            elif digit == 2:
                tile_setting = [str(digit), bg_color['2'], color['1/2']]   
            elif digit == maxTile(board_h):
                tile_setting = [str(3*2**(digit-3)), bg_color['3+'], color['largest']]
            else:
                tile_setting = [str(3*2**(digit-3)), bg_color['3+'], color['else']]
            axText.update({'text': tile_setting[0], 'color': tile_setting[2], 'weight': 'bold', 'size':'large'})
            axes[i+4].set_facecolor(tile_setting[1])
        # paint nextTile Area
        if next is None: 
            nexttile_setting = ['Over', '#817d82', '#c40000'] 
        elif next <2:
            nexttile_setting = ['', bg_color[str(next+1)], '#ffffff'] # font colour doesn't matter
        elif next == 2:
            nexttile_setting = ['3', bg_color['3+'], color['else']]
        else:
            nexttile_setting = ['6-{}'.format(3*2**(maxTile(board_h)-6)), bg_color['3+'], color['else']]
        self.axesText[1].update({'text': nexttile_setting[0], 'color': nexttile_setting[2], 'size': 10})
        axes[1].set_facecolor(nexttile_setting[1])
        self.axesText[3].update({'text': str(currentScore)})
        return self.fig
    
    def anim_init(self):
        # figsize = (3,5) is a nice ratio
        ncols = 4
        nrows = 5 
        # create the plots
        # plt.suptitle('Best game')
        axes = [ self.fig.add_subplot(nrows, ncols, r * ncols + c) for r in range(0, nrows) for c in range(1, ncols+1) ]
        for ax in axes:
            self.axesText.append(ax.text(0.5, 0.5, "", horizontalalignment='center', verticalalignment='center'))
        
        self.axesText[0].update({'text':"Next: "})
        self.axesText[2].update({'text':"Score: "})
        #axes[2].text(0.5, 0.5, "Score: ", horizontalalignment='center', verticalalignment='center')
        for i in [0, 2, 3]:
            axes[i].set_frame_on(False)
    # remove the x and y ticks
        for ax in axes:
            ax.set_xticks([])
            ax.set_yticks([])
        return self.fig
    def anim_update(self, i):
        self.render_img(self.history[i])
        return self.fig

if __name__ == "__main__":
    with open ('outfile', 'rb') as fp:
        history = pickle.load(fp)
    #history_row = [(0x3012230011000120,2), 3, 99999, None, None]
    recorder = RecordThrees(history)
    anim = FuncAnimation(recorder.fig, func = recorder.anim_update, frames=range(len(history)), interval=1000)
    writergif = PillowWriter(fps=1) 
    anim.save('output.gif', writer=writergif)
    # anim.save('animation.mp4')
    plt.show()
