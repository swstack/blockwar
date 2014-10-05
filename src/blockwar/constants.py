#----------------------------------------------------------------------------------------
# General
#----------------------------------------------------------------------------------------
BOARDWIDTH = 4  # number of columns in the board
BOARDHEIGHT = 4  # number of rows in the board
TILESIZE = 80
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
FPS = 30
BLANK = None

#----------------------------------------------------------------------------------------
# Style
#----------------------------------------------------------------------------------------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BRIGHTBLUE = (0, 50, 255)
DARKTURQUOISE = (3, 54, 73)
GREEN = (0, 204, 0)

BGCOLOR = DARKTURQUOISE
TILECOLOR = GREEN
TEXTCOLOR = WHITE
BORDERCOLOR = BRIGHTBLUE

BUTTONCOLOR = WHITE
BUTTONTEXTCOLOR = BLACK
MESSAGECOLOR = WHITE

BASICFONTSIZE = 20

XMARGIN = int((WINDOWWIDTH - (TILESIZE * BOARDWIDTH + (BOARDWIDTH - 1))) / 2)
YMARGIN = int((WINDOWHEIGHT - (TILESIZE * BOARDHEIGHT + (BOARDHEIGHT - 1))) / 2)

#----------------------------------------------------------------------------------------
# Directional
#----------------------------------------------------------------------------------------
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'
