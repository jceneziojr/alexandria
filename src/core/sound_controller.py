import pygame as pg


class SoundController:
    def __init__(self):
        self.sounds = {
            "jump": [False, pg.mixer.Sound("resources/sound/Jump.wav")],
            "loose_life": [False, pg.mixer.Sound("resources/sound/Hit_Hurt.wav")],
            "dialogue": [False, pg.mixer.Sound("resources/sound/Dialogue.wav")],
            "success": [False, pg.mixer.Sound("resources/sound/Success.wav")],
            "write": [False, pg.mixer.Sound("resources/sound/Write.wav")],
            "explosion": [False, pg.mixer.Sound("resources/sound/Explosion.wav")],
        }
