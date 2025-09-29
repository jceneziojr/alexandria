import pygame as pg
import pymunk as pm
import pymunk.pygame_util
from typing import Union

from ..core.configs import (
    WINDOW_WIDTH,
    MAP_HEIGHT,
    MAP_WIDTH,
)

from ..core.state_machine import State
from ..core.dialog_handler import DialogSystem
from ..core.global_controller import GlobalController
from ..entities.player import Player

from ..entities.life_bar import LifeBar

from ..levels.base_level import LevelSystem
from ..levels.phase_1 import Phase1
from ..levels.phase_2 import Phase2
from ..levels.phase_3 import Phase3
from ..levels.phase_4 import Phase4
from ..levels.phase_5 import Phase5
from ..levels.intro_scene import IntroScene
from ..levels.library_scene import LibraryScene
from ..levels.ending_scene import EndingScene


class Tile(pg.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf

        self.rect = self.image.get_rect(topleft=pos)


class Game(State):
    """
    Actual gameplay
    """

    def __init__(self):
        super().__init__()
        self.dialog_system: Union[DialogSystem, None] = None
        self.pymunk_surface = None
        self.camera = None
        self.npc = None
        self.life_bar = None
        self.block_2 = None
        self.block = None
        self.player: Union[Player, None] = None
        self.background_color = (255, 255, 255)

        self.active_keys = set()

        # criando grupo de sprites e agrupando para facilitar draw e update
        self.all_moving_sprites = (
            pg.sprite.Group()
        )  # todas as sprites que tem que se mexer com a câmera

        self.sprites_g = pg.sprite.Group()
        self.bad_sprites_g = pg.sprite.Group()
        self.static_sprites_g = pg.sprite.Group()
        self.npc_sprites_g = pg.sprite.Group()
        self.floor_sprites_g = pg.sprite.Group()
        self.background_sprites_g = pg.sprite.Group()

        self.space = None
        self.draw_opt: Union[pm.pygame_util.DrawOptions, None] = None

        self.sprites_groups = {
            "all_moving_sprites": self.all_moving_sprites,
            "sprites_g": self.sprites_g,
            "bad_sprites_g": self.bad_sprites_g,
            "static_sprites_g": self.static_sprites_g,
            "npc_sprites_g": self.npc_sprites_g,
            "floor_sprites_g": self.floor_sprites_g,
            "background_sprites_g": self.background_sprites_g,
        }

        self.level_controller = LevelSystem(self)

        self.next = "CREDITS"

    def startup(self, now, persistant):
        super().startup(now, persistant)
        self.space: pymunk.Space = persistant[
            "space"
        ]  # pegando o espaço do pymunk definido na controladora
        self.draw_opt = persistant[
            "draw_opt"
        ]  # serve pra debugar o pymunk, TIRAR AO FINAL

        # VER QUAL FUNCIONA MELHOR
        self.pymunk_surface = pg.Surface(
            (MAP_WIDTH, MAP_HEIGHT)
        )  # preciso ter uma surface apenas pra desenhar os objetos do pymunk alinhados com os do pygame
        self.draw_opt = pymunk.pygame_util.DrawOptions(self.pymunk_surface)

        self.player = Player(
            self.space,
            (self.sprites_g, self.all_moving_sprites),
            (600, 500),
            (50, 50),
            name=persistant["player_name"]
        )  # adicionando o player

        self.dialog_system = DialogSystem(self.player)

        self.life_bar = LifeBar(
            self.player, self.static_sprites_g, (20, 20), heart_size=32
        )

        self.camera = GameCamera(MAP_WIDTH, MAP_HEIGHT)
        self.sound_controller = persistant["sound_controller"]
        self.global_controller = GlobalController()
        self.player.sound_controller = self.sound_controller
        self.dialog_system.global_controller = self.global_controller
        self.dialog_system.sound_controller = self.sound_controller

        all_levels = {"phase_1": Phase1(), "phase_2": Phase2(), "phase_3": Phase3(), "phase_4": Phase4(),
                      "phase_5": Phase5(), "intro_scene": IntroScene(), "library_scene": LibraryScene(),
                      "ending_scene": EndingScene()}

        self.level_controller.setup_levels(all_levels, "intro_scene")
        pg.mixer.init()

    def get_event(self, event):
        """
        The logic implemented below allows for a movement to be continuous
        when the player holds the key
        """
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYDOWN:
            self.active_keys.add(event.key)  # Adds the pressed key to the set
        elif event.type == pg.KEYUP:
            # Removes the released key to the set
            self.active_keys.discard(event.key)
        self.player.input_handler(
            self.active_keys
        )  # pega as teclas pressionadas e passa para o jogador lidar com movimentação
        self.level_controller.get_event(event, self.active_keys)
        self.dialog_system.check_player_input(self.active_keys)

    def update(self, keys, now):
        self.level_controller.update(now)
        if not self.player.jump_pressed and self.sound_controller.sounds["jump"][0]:
            self.sound_controller.sounds["jump"][0] = False
        if self.player.jump_pressed and not self.sound_controller.sounds["jump"][0]:
            self.sound_controller.sounds["jump"][0] = True
            self.sound_controller.sounds["jump"][1].play()
            self.sound_controller.sounds["jump"][1].set_volume(0.3)

        if self.player.life_number <= 0:
            self.next = "GAME_OVER"
            self.done = True

    def draw(self, surface: pg.Surface):
        self.level_controller.draw(surface, self.pymunk_surface)
        self.dialog_system.update()

    def cleanup(self):
        self.done = False  # important, otherwise it will persist
        return super().cleanup()

    def create_bound(self):
        """
        Cria os limites da tela na esquerda, direita e teto
        """
        left_wall_body = pm.Body(body_type=pm.Body.STATIC)
        left_wall_shape = pm.Segment(
            left_wall_body, (0, 0), (0, MAP_HEIGHT), 0)
        left_wall_shape.friction = 0.0
        left_wall_shape.elasticity = 0.0
        self.space.add(left_wall_body, left_wall_shape)

        right_wall_body = pm.Body(body_type=pm.Body.STATIC)
        right_wall_shape = pm.Segment(
            right_wall_body, (MAP_WIDTH, 0), (MAP_WIDTH, MAP_HEIGHT), 1
        )
        right_wall_shape.friction = 0.0
        right_wall_shape.elasticity = 1.0
        self.space.add(right_wall_body, right_wall_shape)

        top_body = pm.Body(body_type=pm.Body.STATIC)
        top_shape = pm.Segment(top_body, (0, 0), (MAP_WIDTH, 0), 10)
        top_shape.friction = 1.0
        self.space.add(top_body, top_shape)


class GameCamera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.camera = pg.Rect(0, 0, self.width, height)
        self.x = 0
        self.y = 0

    def update(self, target):
        self.x = max(
            WINDOW_WIDTH - self.width,
            min(0, int(WINDOW_WIDTH / 2) - target.rect.centerx),
        )

        self.y = 0  # a camera não mexe em y
        self.camera = pg.Rect(self.x, self.y, self.width, self.height)

    def apply(self, entity, adjust=None):
        if adjust:
            return entity.rect.move(
                (self.camera.topleft[0], self.camera.topleft[1] + adjust)
            )
        return entity.rect.move(self.camera.topleft)

    def draw(self, surface, group, pymunk_surface, floor_sprites, background_sprites, npc_sprites):
        surface.blit(
            pymunk_surface,
            (
                self.x,
                self.y,
            ),
        )  # preciso ter uma surface só pra os elementos do pymunk alinharem

        for sprite in background_sprites.sprites():
            surface.blit(sprite.image, self.apply(sprite))
        # o pymunk vem antes para as coisas ficarem atras das sprites do pygame
        for sprite in npc_sprites.sprites():
            surface.blit(sprite.image, self.apply(sprite))
        for sprite in group.sprites():
            surface.blit(sprite.image, self.apply(sprite))
        for sprite in floor_sprites.sprites():
            surface.blit(sprite.image, self.apply(sprite))
