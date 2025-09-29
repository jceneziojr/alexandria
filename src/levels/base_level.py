from __future__ import annotations

import pygame as pg
import pymunk as pm

from ..core.configs import tmxdata, MAP_WIDTH, MAP_HEIGHT, INVINCIBILITY_TIME, BG_COLOR
from ..core.shape_loader import ObjectShape

from typing import Union, Tuple, Dict
from ..entities.npc import NPC
from ..minigame.minigame_manager import MinigameManager
from ..core.info_box import InfoBox


class Tile(pg.sprite.Sprite):
    def __init__(
            self, pos, surf, groups: Union[pg.sprite.Group, Tuple[pg.sprite.Group]]
    ):
        # noinspection PyTypeChecker
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)


class LevelSystem:
    def __init__(self, game):
        self.done: bool = False
        self.level_dict: Dict[str, Level] = {}
        self.level_name: Union[str, None] = None
        self.level: Union[Level, None] = None
        self.game = game
        self.sprites_groups = game.sprites_groups

        self.first_level_loaded = False

    def setup_levels(self, level_dict: Dict[str, Level], start_state: str):
        self.level_dict = level_dict
        self.level_name = start_state
        self.level = self.level_dict[self.level_name]
        self.flip_level()

    def update(self, now):
        if self.level.done:
            self.flip_level()
        self.level.update(now)

    def draw(self, surface: pg.Surface, pymunk_surface: pg.Surface):
        self.level.draw(surface, pymunk_surface)

    def flip_level(self):
        if self.level_name == "ending_scene":
            self.game.done = True
        else:
            self.level.done = (
                False  # apenas pra testes, nas versões finais provavelmente deve sair
            )

            if self.first_level_loaded:
                previous, self.level_name = (self.level_name, self.level.next_level_name)
                persist = self.level.cleanup()

                if persist is not None:
                    persist = persist | self.sprites_groups
                else:
                    persist = self.sprites_groups
                self.level.previous_level = previous
                self.game.global_controller.set_current_phase_number(self.level_name)

            else:
                persist = self.sprites_groups
                self.first_level_loaded = True

            self.level = self.level_dict[self.level_name]

            self.level.setup_level(self.game, persist)
            self.level.handle_music()

    def get_event(self, event, keys):
        self.level.get_event(event, keys)


class Level:
    def __init__(self):
        self.game = None
        self.player = None
        self.draw_opt = None
        self.camera = None
        self.space: Union[pm.Space, None] = None
        self.minigame_manager: Union[MinigameManager, None] = None

        self.life_bar = None
        self.current_level_name = "map_1"
        self.next_level_name = "map_2"
        self.done = False

        self.background_color = (255, 255, 255)

        self.sprites_g = None
        self.all_moving_sprites = None
        self.bad_sprites_g = None
        self.static_sprites_g = None
        self.npc_sprites_g = None
        self.floor_sprites_g = None
        self.background_sprites_g = None

        self.assist_global_handler = None
        self.info_box = InfoBox()

    def update(self, now):
        for (
                _sprite
        ) in (
                self.bad_sprites_g.sprites()
        ):  # checando se o player colidiu com um inimigo
            if self.player.shape.shapes_collide(_sprite.body.shape).points:
                _sprite.collision_change(True)

                delta_time = now - self.player.last_contact

                if delta_time > INVINCIBILITY_TIME:  # se for maior que 1 segundo
                    self.player.loose_life()
                    self.player.last_contact = now
            else:
                _sprite.collision_change(False)

        self.static_sprites_g.update()
        self.all_moving_sprites.update()
        self.camera.update(self.player)

        if self.minigame_manager.active:
            self.minigame_manager.update(1 / 60)  # só chamar o update se o minigame estiver ativo
            self.player.can_move = False  # impedir o player de mover se o minigame estiver ativo
        elif self.game.dialog_system.dialog_active:
            self.player.can_move = False
        else:
            self.player.can_move = True  # player pode mover se o minigame não estiver ativo
            if (pg.time.get_ticks() - self.minigame_manager.success_sound_control) / 1000 > \
                    self.minigame_manager.sound_controller.sounds["success"][1].get_length() and \
                    self.minigame_manager.sound_controller.sounds["success"][0]:
                self.minigame_manager.sound_controller.sounds["success"][1].stop()
                self.minigame_manager.sound_controller.sounds["success"][0] = False

    def draw(self, surface, pymunk_surface):
        pymunk_surface.fill(BG_COLOR)
        surface.fill(self.background_color)
        self.space.debug_draw(self.draw_opt)

        self.camera.draw(
            surface,
            self.all_moving_sprites,
            pymunk_surface,
            self.floor_sprites_g,
            self.background_sprites_g,
            self.npc_sprites_g
        )
        self.static_sprites_g.draw(surface)
        self.info_box.render_info_box(surface)
        self.minigame_manager.draw(surface)

    def handle_music(self):
        # precisa de um override em todas as classes que herdam Level, no formato abaixo:
        # pg.mixer.music.load("resources/sound/placeholder_main.mp3")
        # pg.mixer.music.set_volume(0.5)
        # pg.mixer.music.play(-1)
        pass

    def cleanup(self):
        pg.mixer.music.stop()
        sprite_groups = [
            self.sprites_g,
            self.all_moving_sprites,
            self.bad_sprites_g,
            self.static_sprites_g,
            self.npc_sprites_g,
            self.floor_sprites_g,
            self.background_sprites_g,
        ]

        for group in sprite_groups:
            group.remove(
                [
                    sprite
                    for sprite in group
                    if sprite not in {self.game.life_bar, self.player}
                ]
            )

        # preciso limpar o set player.interactable pra não bugar o número de interações que acontecem
        self.player.interactable.clear()

        # Remover shapes, exceto a do player
        for shape in self.space.shapes[
                     :
                     ]:  # Criar uma cópia para evitar erro ao remover durante a iteração
            if shape != self.player.shape:
                self.space.remove(shape)

        # Remover bodies, exceto o do player
        for body in self.space.bodies[
                    :
                    ]:  # Criar uma cópia para evitar erro ao remover durante a iteração
            if body != self.player.body:
                self.space.remove(body)

        persist = {}

        return persist

    def get_event(self, event: pg.event.Event, keys):
        if self.minigame_manager.active:
            self.minigame_manager.handle_event(event, keys)

    def setup_level(self, game, persist):
        self.game = game
        self.player = game.player
        self.space = game.space
        self.draw_opt = game.draw_opt
        self.camera = game.camera

        self.sprites_g = persist["sprites_g"]
        self.all_moving_sprites = persist["all_moving_sprites"]
        self.bad_sprites_g = persist["bad_sprites_g"]
        self.static_sprites_g = persist["static_sprites_g"]
        self.npc_sprites_g = persist["npc_sprites_g"]
        self.floor_sprites_g = persist["floor_sprites_g"]
        self.background_sprites_g = persist["background_sprites_g"]

        self.life_bar = game.life_bar
        self.create_bound()

        self.assist_global_handler = game.global_controller

        # carregando o mapa dos arquivos do tiled
        for layer in tmxdata[self.current_level_name].visible_layers:
            if hasattr(layer, "data"):
                for x, y, surf in layer.tiles():
                    if layer.name == "Fundo":
                        pos = (0, 0)
                        Tile(pos=pos, surf=surf, groups=(self.background_sprites_g))
                    else:
                        pos = (x * 32, y * 32)
                        Tile(pos=pos, surf=surf, groups=(self.floor_sprites_g))

        # colisões do mapa (bounds/blocos/chão)
        jumpable = self.create_pymunk_from_tiled()

        self.player.ground_shape = tuple(jumpable)
        self.startup()

        self.get_npcs_current_level()

        # posicionar o player

    def get_npcs_current_level(self):
        pass

    def startup(self):
        self.minigame_manager = MinigameManager(self.player)
        self.minigame_manager.sound_controller = self.game.sound_controller

    def create_pymunk_from_tiled(self):
        all_grounds = []
        for g in tmxdata[self.current_level_name].objectgroups:
            for o in g:

                if (
                        o.type == "Plataforma"
                ):  # acho que faz sentido dar pra pular de qualquer objeto
                    assist = ObjectShape(
                        o, (self.sprites_g, self.all_moving_sprites), self.space
                    )
                    all_grounds.append(assist.body.shape)
                elif o.type == "NPC":
                    npc = NPC(
                        (self.npc_sprites_g),
                        (o.x, o.y),
                        (o.width, o.height),
                        o.image,
                        o.name,
                        dialog_system=self.game.dialog_system,
                        assist_global_handler=self.assist_global_handler
                    )
                    self.player.interactable.add(npc)
                elif o.type == "Enemy":
                    assist = ObjectShape(
                        o, (self.sprites_g, self.all_moving_sprites, self.bad_sprites_g), self.space
                    )

                else:
                    # quando não passo o shape pra lista, não da pra pular do objeto
                    ObjectShape(
                        o, (self.sprites_g, self.all_moving_sprites), self.space
                    )
        return all_grounds

    def create_bound(self):
        """
        Cria os limites da tela na esquerda, direita e teto

        """
        left_wall_body = pm.Body(body_type=pm.Body.STATIC)
        left_wall_shape = pm.Segment(left_wall_body, (0, 0), (0, MAP_HEIGHT), 0)
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
