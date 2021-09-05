import gym
from gym import spaces
from gym.utils import seeding

from pathlib import Path
import json

from .Board_tkinter import BoardGUI
from .render_img import RecordThrees

from tkinter import messagebox
import pickle


def keystoint(x):
    return {int(k): v for k, v in x}
# import the dictionaries needed
with open(Path(__file__).parent/'RightTables.json') as json_file:
#with open('RightTables.json') as json_file:
    RIGHTTABLE = json.load(json_file, object_pairs_hook=keystoint)
with open(Path(__file__).parent/'LeftTables.json') as json_file:
    LEFTTABLE = json.load(json_file, object_pairs_hook=keystoint)
with open(Path(__file__).parent/'scoreTables.json') as json_file:
    SCORETABLE = json.load(json_file, object_pairs_hook=keystoint)  
ACTION = {'Left': 0, 'Right': 1, 'Up': 2, 'Down': 3}
class ThreesEnv(gym.Env):
  """Custom Environment for a game simulation of Threes 
  https://en.wikipedia.org/wiki/Threes
  """
  metadata = {'render.modes': ['human_interact', 'human', 'uint64']}
  # 'human_interact': render a tkinter for a human game
  # 'human': render a gif of a play through up to the current step
  # 'uint64': print the current observation in stdout

  def __init__(self): 
    
    # Define action and observation space
    # They must be gym.spaces objects
    # Example when using discrete actions:
    self.action_space = spaces.Discrete(4)
    """ action_space mapping:
    0  -  "Left"
    1  -  "Right"
    2  -  "Up"
    3  -  "Down"
     """
    # Example for using image as input:
    self.observation_space =spaces.Tuple((spaces.Discrete(16**16), spaces.Discrete(4)))
    """ (board, nextTile):
    board: uint64 without 0 (as it is not possible to have an empty board). From top-left to bottom-right, every 4 digit (int i) represent the value of a tile.
    i = 0  -  empty
    i in [1,2] -  i
    i >= 3   - 3**(i-2)
    nextTile:
    0 - next tile is 1
    1 - next tile is 2
    2 - next tile is 3
    3 - next tile is bonus tile, i.e., between 6 and maxTile/8 (containing both ends)
      """    
    self.history = [] 
    # history should be a list where each entry is \
    # `[observation, nextTile, score, action, reward]` 
    # currently `history` is only recorded beyond the initial state\
    # when rendering in human_interact mode. One has to manually record the history in other cases. 
    # One can use self.history to recall the initial state of the game.
    self.currentSeed = self.seed()

    self.reset()
  def step(self, action):
    # done = self._noMoreMoves(moveTable_L= LEFTTABLE, moveTable_R= RIGHTTABLE)
    # Execute one time step within the environment
    prev_score = self.score
    if action==2:   # Up
      self._transpose()
      self._updateRows(direction='Left', moveTable=LEFTTABLE, scoreTable= SCORETABLE)
      self._transpose()

    elif action==3:  # Down
      self._transpose()
      self._updateRows(direction='Right', moveTable=RIGHTTABLE, scoreTable= SCORETABLE)
      self._transpose()

    elif action==0:  # Left
      self._updateRows(direction='Left', moveTable=LEFTTABLE, scoreTable= SCORETABLE)
    elif action==1:   # Right
      self._updateRows(direction='Right', moveTable=RIGHTTABLE, scoreTable= SCORETABLE)
    next = self.nextTile -1 if self.nextTile<=3 else 3
    reward = self.score-prev_score + 3  
    """ reward: 
    +3 for each turn played;
    +3 when merging 1 and 2
    +a when merging a and a
      """ 
    self.legalMoves(moveTable_L= LEFTTABLE, moveTable_R= RIGHTTABLE)
    done = not self.legalNextMoves
    if done:
      next = None
      reward = 0
      # self.history.append([(self.board_h, next), self.nextTile, self.score, action, reward])
    return (self.board_h, next), reward, done, {}
  def reset(self):
    # Reset the state of the environment to an initial state
    # seed is used to generate all the random new tiles of the game
    self.newTiles = [1]*4+[2]*4+[3]*4
    self.np_random.shuffle(self.newTiles)
    initialboard = self.newTiles[0:9]+[0]*7
    self.newTiles = self.newTiles[9:]
    self.np_random.shuffle(initialboard)
    self.board_h = int( ''.join(map(str, initialboard)), 16)
    self.max = 0
    self.score = 0
    self._genNextTile()
    self.servedTiles = [self.nextTile] # we should consider past served tile in the future
    next = self.nextTile -1 if self.nextTile<=3 else 3
    self.legalNextMoves=self.legalMoves()
    self.history = [[(self.board_h, next), self.nextTile, 0, None, None]]
    return (self.board_h, next)
  def seed(self, seed=None):
    self.np_random, seed = seeding.np_random(seed)
    return seed
  def _transpose(self) -> int:
    a1 = self.board_h & 0xF0F00F0FF0F00F0F
    a2 = self.board_h & 0x0000F0F00000F0F0
    a3 = self.board_h & 0x0F0F00000F0F0000
    a = a1 | (a2 << 12) | (a3 >> 12)
    b1 = a & 0xFF00FF0000FF00FF
    b2 = a & 0x00FF00FF00000000
    b3 = a & 0x00000000FF00FF00
    self.board_h =  b1 | (b2 >> 24) | (b3 << 24)
  def _updateRows(self, direction = 'Left', moveTable = None, scoreTable = None) -> int: # update .board_h according to leftTable/rightTable
    # return newTile that is already inserted to the board
    temp_row = 0
    self.score = 0
    availableRows = []
    for i in range(4):
      current_row = self.board_h >> 16*(3-i) & 0xffff
      current_row = moveTable[current_row]
      #print("{}->{}".format(hex(self.board_h >> 16*(3-i) & 0xffff), hex(current_row)))
      if current_row  != -1:
        availableRows.append(i)
        self.score += scoreTable[current_row]  # the score is calcualted for the board after moving but before new tile is inserted
        temp_row |= current_row << 16*(3-i)
      else: 
        temp_row |= (self.board_h >> 16*(3-i)& 0xffff) << 16*(3-i)
        self.score += scoreTable[self.board_h >> 16*(3-i)& 0xffff]
    #print('available rows: {}'.format(availableRows))
    if availableRows:
        chosenRow = self.np_random.choice(availableRows).item()  #change np type to python native type
        if direction == 'Left':
            temp_row |= self.nextTile << 16*(3-chosenRow)
        else:
            temp_row |= self.nextTile<< 16*(3-chosenRow)+12
            self.servedTiles.append(self.nextTile)
        self._genNextTile()
    self.board_h = temp_row
    #print("final: {}".format(hex(self.board_h)))
  def _genNextTile(self) -> int:
      # return the next tile in hex number
      if self.max >= 7 and self.np_random.random() < 1/21:
          self.nextTile = self.np_random.choice(range(4, self.max-2)).item() #change np type to python native type
      else:
          if not self.newTiles:
              self.newTiles = [1]*4+[2]*4+[3]*4
              self.np_random.shuffle(self.newTiles)
          self.nextTile = self.newTiles.pop(0)  
  def maxTile(self) -> None:
      maxTile = 0
      for i in range(16):
          temp = self.board_h >> 4*i & 0xf
          maxTile = temp if temp>maxTile else maxTile
      self.max = maxTile
  def _noMoreMoves(self, moveTable_L = None, moveTable_R = None)->bool:
      flag = True
      for i in range(4):
          current_row = self.board_h >> 16*(3-i) & 0xffff
          #temp_rows.append(moveTable[current_row])            
          if moveTable_L[current_row]  != -1 or moveTable_R[current_row] !=-1:
              flag = False
              return flag
      self._transpose()
      for i in range(4):
          current_row = self.board_h >> 16*(3-i) & 0xffff
          #temp_rows.append(moveTable[current_row])            
          if moveTable_L[current_row]  != -1 or moveTable_R[current_row] !=-1:
              flag = False
              break
      self._transpose()
      return flag
  def legalMoves(self, moveTable_L = LEFTTABLE, moveTable_R = RIGHTTABLE)->list:
      #return boolean "if possible" fror [left, right, up, down]
      flag = [0]*4
      for i in range(4):
        current_row = self.board_h >> 16*(3-i) & 0xffff
        #temp_rows.append(moveTable[current_row])            
        if moveTable_L[current_row]  != -1:
            flag[0] |= 1 
        if moveTable_R[current_row] !=-1:
            flag[1] |= 1
        if flag[0] & flag[1]:
          break
      self._transpose()
      for i in range(4):
        current_row = self.board_h >> 16*(3-i) & 0xffff
        #temp_rows.append(moveTable[current_row])            
        if moveTable_L[current_row]  != -1:
            flag[2] |= 1
        if moveTable_R[current_row] !=-1:
            flag[3] |= 1
        if flag[2] & flag[3]:
          break
      self._transpose()
      self.legalNextMoves = [i for i in range(4) if flag[i]]
      return self.legalNextMoves
  def render(self, mode='uint64', close=False):
    # Render the environment to the screen
    if mode == 'uint64':
      print("Game Threes:")
      output = self._uint64toMatrix()
      print("{}\n{}\n{}\n{}".format(output[0],output[1],output[2],output[3]))
      print("Next: {}\n Score: {}".format(self._nextTileMap(), self.score))
      print("Possible next moves: {}\n".format(self.legalNextMoves))
    elif mode == 'human_interact':
      gamepanel = BoardGUI()
      game = Game_tkinter(gamepanel, self)
      game.start()
    elif mode == 'human':
      next = self.nextTile -1 if self.nextTile<=3 else 3
      figObj = RecordThrees([[(self.board_h,next), self.nextTile, self.score, None, None]])
      figObj.render_img(figObj.history[0])
      return figObj.fig 
      # return the figure object. Save by figObj.fig.savefig('plot.png')
  def _nextTileMap(self) -> str:
    if self.nextTile<= 3:
      output = str(self.nextTile)
    else:
      output = '6-{}'.format(3*2**(self.boardBinary.max-6))
    return output
  def _uint64toMatrix(self) -> list:
    board_matrix = []# can not do [[0]*4]*4, because this makes all the rows refer to the same row
    for i in range(4):
      board_row = []
      for j in range(4):
        digit = self.board_h >> 4*(3-j+4*(3-i)) & 0xf
        if digit<=3:
          board_row.append(digit)
        else:
          board_row.append(3*2**(digit-3))
      board_matrix.append(board_row)
    return board_matrix

class Game_tkinter:
    def __init__(self,gamepanel: BoardGUI, boardBinary: ThreesEnv ):
        self.gameGUI=gamepanel
        self.boardBinary = boardBinary 
        self.gameGUI.bindBoard(self.boardBinary)
        self.end = False # game ending criteria: self.minmax[0]>0 or self.minmax[1]==15
        self.gameGUI.paintGrid()
        self.outfile = 0 # The output history pickle file name as integer
    def start(self):
        self.gameGUI.window.bind('<Key>', self.link_keys)
        self.gameGUI.window.mainloop()
    def link_keys(self,event):
        pressed_key=event.keysym
        if self.end:
          output_dir = Path(__file__).parent.parent / 'records'
          self.outfile = len(list(output_dir.glob('*'))) + 1
          with open(output_dir/"{}".format(self.outfile), 'wb') as fp:
            pickle.dump(self.boardBinary.history, fp)
          messagebox.showinfo('Game Over!!!', 'Your score is: {}.'.format(self.boardBinary.score))
        if pressed_key not in ['Up', 'Down', 'Left', 'Right']:
          return
        else:
          action  = ACTION[pressed_key]
          obs, reward, self.end, _ =  self.boardBinary.step(action)
        self.boardBinary.maxTile()
        self.boardBinary.history.append([obs, self.boardBinary.nextTile, self.boardBinary.score, action, reward])
        #print(hex(self.boardBinary.board_h))
        #print(self.boardBinary.max)
        #print("{} chosen out of {}".format(self.boardBinary.nextTile, self.boardBinary.newTiles))
        self.gameGUI.paintGrid()

        