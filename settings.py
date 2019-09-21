'''Configuration of the game settings'''

import pygame as pg


# Game colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
RED = (255, 0, 0)
LIGHTGREEN = (0, 255, 0)
DARKGREEN = (0, 128, 0)
BLUE = (0, 0, 255)
LIGHTBLUE = (80, 80, 255)
DARKBLUE = (0, 0, 128)
YELLOW = (128, 128, 0)
DARKYELLOW = (255, 255, 0)
BROWN = (106, 55, 5)
CYAN = (0, 255, 255)
COLORS = [DARKGREEN, BLUE, BROWN, YELLOW, LIGHTGREY]
EXPLORED_TILES_COLOR = (128, 128, 128, 128)

# Game Settings
WIDTH = 1024
HEIGHT = 768
TILESIZE = 64
BOARDWIDTH = 32
BOARDHEIGHT = 24
BOARD_TOPLEFT = (WIDTH // 2 - TILESIZE // 2, HEIGHT // 2 - TILESIZE // 2)
BOARD_CENTER = [-abs((BOARDWIDTH * 64 - WIDTH) // 2),
                -abs((BOARDHEIGHT * 64 - HEIGHT) // 2)]
FPS = 30
BGCOLOR = WHITE
BG_IMAGE = None
FONT_NAME = 'arial'
TITLE = 'Turn Based Game'

TOOLTIP_DELAY = 500

# Player settings
PLAYER_VEL = 200
DARK = 0

# Terrain Settings
FOREST_ENTERING_COST = 10
GRASS_ENTERING_COST = 0
WATER_ENTERING_COST = 50
MOUNTAIN_ENTERING_COST = 100

FOREST_FREQUENCY = 40
GRASS_FREQUENCY = 30
WATER_FREQUENCY = 10
MOUNTAIN_FREQUENCY = 5

FOREST_DEFENCE = 10
GRASS_DEFENCE = 0
WATER_DEFENCE = 0
MOUNTAIN_DEFENCE = 20
