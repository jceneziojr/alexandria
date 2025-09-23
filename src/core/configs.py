# Python 3.10
"""
constantes globais
"""

import os
from typing import List
import pygame as pg
from .tools import load_all_gfx
import pytmx

pg.init()  # preciso dar esse init aqui para conseguir setar a tela

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 640

MAP_WIDTH = 1120
MAP_HEIGHT = 640

FPS = 60
TIME_PER_UPDATE = 1 / FPS

# setando o rect da tela
SCREEN_RECT = pg.Rect((0, 0), (WINDOW_WIDTH, WINDOW_HEIGHT))

INVINCIBILITY_TIME = 1e3
GRAVITY = 1500
MAX_SPEED = 300
MOVE_FORCE = 300
JUMP_FORCE = 600

DEFAULT_CONTROLS = {
    pg.K_UP: (0, -JUMP_FORCE),  # pulo
    pg.K_DOWN: (0, JUMP_FORCE),
    pg.K_LEFT: (-MOVE_FORCE, 0),  # Move para a esquerda
    pg.K_RIGHT: (MOVE_FORCE, 0),  # Move para a direita,
    pg.K_w: (0, -JUMP_FORCE),  # pulo
    pg.K_s: (0, JUMP_FORCE),
    pg.K_a: (-MOVE_FORCE, 0),  # Move para a esquerda
    pg.K_d: (MOVE_FORCE, 0),  # Move para a direita
}

BG_COLOR = (104, 104, 104)
GAME_WINDOW_TITLE = "AlexandriA"

PLAYER_SIZE = (50, 50)

_screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))  # setando a tela

levels = ["phase_1", "phase_2", "phase_3", "phase_4", "phase_5", "intro_scene", "library_scene"]
tmxdata = {}

for level in levels:
    tmxdata[level] = pytmx.util_pygame.load_pygame(
        f"resources/tiled/{level}.tmx")

FONTS_DICT = {1: ["GB", 21]}
FONT_INDEX = 1
TEXT_FONT = pg.font.Font(
    f"resources/fonts/{FONTS_DICT[FONT_INDEX][0]}.TTF", FONTS_DICT[FONT_INDEX][1])
TEXT_FONT_2 = pg.font.Font(
    f"resources/fonts/{FONTS_DICT[FONT_INDEX][0]}.TTF", 20)
INFO_BOX_FONT = pg.font.Font(
    f"resources/fonts/{FONTS_DICT[FONT_INDEX][0]}.TTF", 15)


def graphics_from_directories(directories: List[str]) -> dict:
    """
    Calls the tools.load_all_graphics() function for all directories passed.
    """
    base_path = os.path.join("resources", "graphics")
    gfx = {}
    for directory in directories:
        path = os.path.join(base_path, directory)
        gfx[directory] = load_all_gfx(path)
    return gfx


_SUB_DIRECTORIES = ["others", "ui", "dialog_faces", "minigame_assets", "newton_gif", "dialogs", "circuit_gif", "ai_gif",
                    "filter_gif", "player", "npcs", "animation", "credits"]  # graphics subfolders to load from
GFX = graphics_from_directories(_SUB_DIRECTORIES)  # all images
