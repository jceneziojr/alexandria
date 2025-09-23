from ..core.tools import BaseEntity
import pygame as pg
import pymunk as pm
from typing import Tuple, Union


class Block(BaseEntity):

    def __init__(
            self,
            space: pm.Space,
            groups: Union[pg.sprite.Group, Tuple[pg.sprite.Group, pg.sprite.Group]],
            pos: Tuple[int, int],
            size: Union[Tuple[int, int], Tuple[float, float]] = None,
            image=None,
            color=None,
    ):
        super().__init__(groups, pos, size, image)

        self.space = space
        mass = 1
        moment = pm.moment_for_box(mass, size)
        self.body = pm.Body(mass, moment, pm.Body.DYNAMIC)
        self.body.position = pos[0], pos[1] - size[1] / 2
        self.shape = pm.Poly.create_box(self.body, size)
        self.shape.friction = 0.1
        self.shape.elasticity = 0.0
        self.color = color
        self.space.add(self.body, self.shape)
        self.image.fill(self.color)

    def update(self):
        self.rect.center = self.body.position.x, self.body.position.y

    def collision_change(self, collide):
        """
        quando o player encosta no bloco, ele muda de cor
        Se não encosta, ele tem velocidade 0 no eixo x
        """
        if collide:
            self.image.fill((100, 10, 10))
        else:
            self.image.fill(self.color)
            self.body.velocity = 0, self.body.velocity.y

    def on_interaction(self):
        pass
