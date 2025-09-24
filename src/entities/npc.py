from ..core.tools import BaseEntity
import pygame as pg
from typing import Tuple, Union
from ..core.configs import GFX


class NPC(BaseEntity):

    def __init__(
            self,
            groups: Union[pg.sprite.Group, Tuple[pg.sprite.Group, pg.sprite.Group]],
            pos: Tuple[int, int],
            size: Union[Tuple[int, int], Tuple[float, float]] = None,
            image=None,
            name=None,
            dialog_system=None,
            assist_global_handler=None,
    ):
        self.image = image
        self.name = name
        self.speaker_id = name
        self.dialog_system = dialog_system
        self.assist_global_handler = assist_global_handler
        self.talked_current_phase = False
        super().__init__(groups, pos, size, self.image)

        self.animations = {
            "right": [GFX["npcs"][f"right_{i + 1}"] for i in range(9)],
            "left": [GFX["npcs"][f"left_{i + 1}"] for i in range(9)],
            "idle_available": [GFX["npcs"][f"idle_available_{i + 1}"] for i in range(8)],
            "idle": [GFX["npcs"]["idle"]],
            "idle_back": [GFX["npcs"]["idle_back"]],
            "archie_idle": [GFX["npcs"]["archie"]],
        }

        self.current_anim = "idle"
        self.anim_index = 0
        self.anim_timer = 0.0
        self.anim_speed = 0.3  # controla velocidade da animação

    def animate(self):
        frames = self.animations[self.current_anim]

        self.anim_timer += self.anim_speed
        if self.anim_timer >= 1:
            self.anim_timer = 0
            self.anim_index = (self.anim_index + 1) % len(frames)

        # define a imagem atual
        self.image = frames[self.anim_index]

    def update(self):
        self.animate()
        print(self.current_anim)

    def on_interaction(self):
        self.dialog_system.start_dialog(self.speaker_id, self.assist_global_handler.current_phase_number)
