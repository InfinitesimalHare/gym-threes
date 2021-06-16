from tkinter import *
from tkinter import messagebox

class BoardGUI:
    
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

    def __init__(self):
        self.window=Tk()
        self.window.title('Gym for Threes')
        self.gameArea=Frame(self.window,bg= 'azure3')
        self.nextTileArea = Frame(self.window,bg= 'azure3')

        self.boardGUI=[] # the 4*4 tiles
        self.nextTileGUI = [] # 1*3 tiles where the middle tile indicate the next tile, the first tile shows text "Next: "
        
        self.boardBinary= None # instance of Board(        

        for i in range(4):
            rows=[]
            for j in range(4):
                l=Label(self.gameArea,text='',bg='azure4',
                font=('arial',22,'bold'),width=4,height=2)
                l.grid(row=i,column=j,padx=7,pady=7)
                
                rows.append(l)
            self.boardGUI.append(rows)
        for i in range(3):
            l = Label(self.nextTileArea, text = '',bg='azure3',
                font=('arial',16, 'bold'),width=5,height=2)
            l.grid(column=i,padx=2,pady=2)
            self.nextTileGUI.append(l)
        self.nextTileGUI[0].config(text='Next: ')

        self.nextTileArea.grid()
        self.gameArea.grid()
    def bindBoard(self, boardBinary):
        self.boardBinary=boardBinary # game board in the form of 16-digit hex string
    def paintGrid(self):
        # paint tileArea -> if the game ends with the current tile, show messagebox -> else show next tile area
        for i in range(4):
            for j in range(4):
                digit = self.boardBinary.board_h >> 4*(3-j+4*(3-i)) & 0xf
                if digit==0:
                    self.boardGUI[i][j].config(text='',bg='azure4')
                elif digit == 1:
                    self.boardGUI[i][j].config(text=str(digit),
                    bg=self.bg_color['1'],
                    fg=self.color['1/2'])
                elif digit == 2:
                    self.boardGUI[i][j].config(text=str(digit),
                    bg=self.bg_color['2'],
                    fg=self.color['1/2'])    
                elif digit == self.boardBinary.max:
                    self.boardGUI[i][j].config(text=str(3*2**(digit-3)),
                    bg=self.bg_color['3+'],
                    fg=self.color['largest'])
                else:
                    self.boardGUI[i][j].config(text=str(3*2**(digit-3)),
                    bg=self.bg_color['3+'],
                    fg=self.color['else'])
        
        if not self.boardBinary.nextTile: 
            self.nextTileGUI[1].config(text='',
            bg='azure3')
        # paint nextTile Area
        elif self.boardBinary.nextTile <3:
            self.nextTileGUI[1].config(text='',
                    bg=self.bg_color[str(self.boardBinary.nextTile)],)
        elif self.boardBinary.nextTile == 3:
            self.nextTileGUI[1].config(text='3',
                    bg=self.bg_color['3+'],
                    fg=self.color['else'])
        else:
             self.nextTileGUI[1].config(text='{}-{}'.format(6,3*2**(self.boardBinary.max-6)),
                    bg=self.bg_color['3+'],
                    fg=self.color['else'] )
