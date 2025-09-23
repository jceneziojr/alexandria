from ..core.tools import BaseEntity
import pygame as pg
import pymunk as pm
from typing import Tuple, Union
from ..entities.player import Player
from ..core.configs import GFX


class LifeBar(pg.sprite.Sprite):
    def __init__(
            self,
            player: Player,
            group: pg.sprite.Group,
            pos: Tuple[int, int],
            heart_size: int = 15,
    ):
        super().__init__(group)

        self.player = player
        self.num_hearts = self.player.life_number
        self.heart_size = heart_size
        self.spacing = 10

        self.sprite = pg.transform.smoothscale(GFX["others"]["heart"],
                                         (self.heart_size, self.heart_size)).copy().convert_alpha()

        width = self.num_hearts * (self.heart_size + self.spacing) - self.spacing
        height = self.heart_size
        self.image = pg.Surface((width, height), pg.SRCALPHA)
        self.rect = self.image.get_rect(topleft=pos)

    def update(self):
        if self.num_hearts != self.player.life_number:
            self.num_hearts = self.player.life_number

        self.image.fill((0, 0, 0, 0))
        for i in range(self.num_hearts):
            x = i * (self.heart_size + self.spacing)
            self.image.blit(self.sprite, (x, 0))
