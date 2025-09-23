import pygame as pg
from .minigame_manager import MiniGame


class MovingBoxMiniGame(MiniGame):
    def __init__(self, size):
        super().__init__(size)
        self.box = pg.Rect(10, 10, 20, 20)
        self.speed = 200
        self.target = pg.Rect(self.width - 30, self.height - 30, 20, 20)

    def update(self, dt):
        if pg.K_LEFT in self.active_keys:
            self.box.x -= self.speed * dt
        if pg.K_RIGHT in self.active_keys:
            self.box.x += self.speed * dt
        if pg.K_UP in self.active_keys:
            self.box.y -= self.speed * dt
        if pg.K_DOWN in self.active_keys:
            self.box.y += self.speed * dt

        self.box.clamp_ip(pg.Rect(0, 0, self.width, self.height))  # manter dentro do "bound"

        if self.box.colliderect(self.target):  # conclusão do minigame
            self.finished = True

    def draw(self, surface):
        # desenhando os dois retangulos (pode ser substituido por sprites)
        pg.draw.rect(surface, (255, 255, 0), self.box)
        pg.draw.rect(surface, (0, 255, 0), self.target)
