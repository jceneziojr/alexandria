from ..core.tools import BaseEntity
import pygame as pg
import pymunk as pm
from typing import Tuple, Union
from pytmx import TiledObject


class ObjectShape(BaseEntity):
    def __init__(
            self,
            tmx_object: TiledObject,
            groups: Union[Tuple[pg.sprite.Group], pg.sprite.Group],
            space: pm.Space,
    ):
        self.tmx_object = tmx_object
        self.x = self.tmx_object.x
        self.y = self.tmx_object.y
        pos = self.x, self.y  # posição referente ao pygame (top left)
        size = self.tmx_object.width, self.tmx_object.height

        if tmx_object.type == "Enemy":
            # Basicamente, o pygame reutiliza as imagens. Então, se tiver um sprite sendo usada em mais de um objeto,
            # e tiver mudança em uma das imagens associadas a um objeto, vai mudar em todos os que usam a mesma imagem
            # (por exemplo, o valor alpha)
            self.image = self.tmx_object.image.convert()
        else:
            self.image = self.tmx_object.image

        super().__init__(groups, pos, size, self.image)
        bl = -self.tmx_object.width / 2, -self.tmx_object.height / 2
        br = self.tmx_object.width / 2, -self.tmx_object.height / 2
        tr = self.tmx_object.width / 2, self.tmx_object.height / 2
        tl = -self.tmx_object.width / 2, self.tmx_object.height / 2
        verts = [bl, br, tr, tl]

        if "body_type" in self.tmx_object.properties:
            if self.tmx_object.properties["body_type"] == "STATIC":
                body_type = pm.Body.STATIC
            elif self.tmx_object.properties["body_type"] == "DYNAMIC":
                body_type = pm.Body.DYNAMIC
            elif self.tmx_object.properties["body_type"] == "KINEMATIC":
                body_type = pm.Body.KINEMATIC
        else:
            body_type = pm.Body.STATIC

        if "static" in self.tmx_object.properties:
            body_type = (
                pm.Body.STATIC
                if self.tmx_object.properties["static"]
                else pm.Body.DYNAMIC
            )

        if "mass" in self.tmx_object.properties:
            mass = self.tmx_object.properties["mass"]
            moment = pm.moment_for_box(mass, size)
        else:
            mass = 1
            moment = pm.moment_for_box(mass, size)

        self.body = pm.Body(mass, moment, body_type)
        self.body.position = (
            self.x + self.tmx_object.width / 2,
            self.y + self.tmx_object.height / 2,
        )  # correção de coordenadas p/ pymunk

        self.body.shape = pm.Poly(self.body, verts)

        if "friction" in self.tmx_object.properties:
            self.body.shape.friction = self.tmx_object.properties["friction"]
        else:
            self.body.shape.friction = 0.5

        if "elasticity" in self.tmx_object.properties:
            self.body.shape.elasticity = self.tmx_object.properties["elasticity"]
        else:
            self.body.shape.elasticity = 0.0

        self.space = space
        self.space.add(self.body, self.body.shape)

    def update(self):
        if self.tmx_object.name == "EU":

            self.body.velocity = (30, 0)
            self.rect.center = self.body.position.x, self.body.position.y
        else:
            self.rect.center = self.body.position.x, self.body.position.y
            self.body.angular_velocity = 0

    def collision_change(self, collide):
        if collide:
            self.image.set_alpha(120)
        else:
            self.image.set_alpha(255)
