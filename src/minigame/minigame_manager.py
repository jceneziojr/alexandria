import pygame as pg

from ..core.configs import WINDOW_WIDTH, WINDOW_HEIGHT
from typing import Union
from ..core.configs import GFX


class MinigameManager:
    def __init__(self, player):
        self.active = False
        self.minigame: Union[MiniGame, None] = None
        self.rect = pg.Rect(0, 0, int(WINDOW_WIDTH * 0.75), int(WINDOW_HEIGHT * 0.75))
        self.rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)  # centralizando o rect do minigame
        self.player = player
        self.life_down_timer = 0
        self.sound_controller = None
        self.success_sound_control = 0

    def start(self, minigame_class, **kwargs):
        self.minigame = minigame_class(self.rect.size, **kwargs)
        self.minigame.failed = False
        self.active = True
        self.sound_controller.sounds["success"][0] = False
        self.minigame.sound_controller = self.sound_controller

    def handle_event(self, event, keys):
        if self.active and self.minigame:
            self.minigame.handle_event(event, keys)

    def update(self, dt):
        if self.active and self.minigame:
            self.minigame.update(dt)
            if self.minigame.finished:
                self.active = False
                if not self.sound_controller.sounds["success"][
                    0] and not self.minigame.failed and not self.minigame.minigame_name == "Animation":
                    self.success_sound_control = pg.time.get_ticks()
                    self.sound_controller.sounds["success"][1].play()
                    self.sound_controller.sounds["success"][1].set_volume(0.75)
                    self.sound_controller.sounds["success"][0] = True
                    self.player.play_animation_once("success", after="idle")

            if self.life_down_timer > 0:
                self.life_down_timer -= dt * 1000

            if self.minigame.failed:
                if self.life_down_timer > 0:
                    pass
                else:
                    if self.minigame.minigame_name == "graph_quizz" and self.minigame.protect:
                        self.sound_controller.sounds['loose_life'][1].play()
                    else:

                        self.player.loose_life()
                        self.player.play_animation_once("fail", after="idle")
                    self.life_down_timer = 1500  # esse tempo tem que ser maior que o tempo pro minigame fechar

    def draw(self, surface):
        if self.active and self.minigame:
            # Cria uma superfície temporária para o minigame
            minigame_surface = pg.transform.smoothscale(
                GFX["others"]["background_display"],
                (self.rect.width, self.rect.height)
            ).convert_alpha()

            self.minigame.draw(minigame_surface)
            surface.blit(minigame_surface, self.rect.topleft)


class MiniGame:
    def __init__(self, size, **kwargs):
        self.width, self.height = size
        self.active_keys = set()
        self.finished = False
        self.failed = False
        self.minigame_name = "None"
        self.sound_controller = None
        self.protect = False

    def handle_event(self, event, keys):
        self.active_keys = keys

    def update(self, dt):
        pass

    def draw(self, surface):
        pass
