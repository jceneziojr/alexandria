from ..core.tools import BaseEntity
from ..core.configs import DEFAULT_CONTROLS, MAX_SPEED, GFX
import pygame as pg
import pymunk as pm
from typing import Tuple, Union


class Player(BaseEntity):

    def __init__(
            self,
            space: pm.Space,
            groups: Union[pg.sprite.Group, Tuple[pg.sprite.Group, pg.sprite.Group]],
            pos: Tuple[int, int],
            size: Union[Tuple[int, int], Tuple[float, float]] = None,
            image=None,
            name="Jogador"
    ):
        super().__init__(groups, pos, size, image)
        self.player_name = name
        self.controls = DEFAULT_CONTROLS  # controles padrão
        self.can_move = True

        self.animations = {
            "right": [GFX["player"][f"right_{i}"] for i in range(9)],
            "left": [GFX["player"][f"left_{i + 1}"] for i in range(9)],
            "idle": [GFX["player"]["idle"]],
            "right_jump": [GFX["player"][f"right_jump_{i + 1}"] for i in range(5)],
            "left_jump": [GFX["player"][f"left_jump_{i + 1}"] for i in range(5)],
            "jump": [GFX["player"][f"jump_{i + 1}"] for i in range(5)],
            "success": [GFX["player"][f"success_{i + 1}"] for i in range(5)],
            "fail": [GFX["player"][f"fail_{i + 1}"] for i in range(11)],
            "p_idle": [GFX["player"]["p_idle"]],
            "p_right": [GFX["player"][f"p_right_{i + 1}"] for i in range(9)],
            "p_left": [GFX["player"][f"p_left_{i + 1}"] for i in range(9)]
        }

        self.current_anim = "idle"
        self.anim_index = 0
        self.anim_speed = 0.3  # velocidade da animação (quanto maior, mais devagar)
        self.anim_timer = 0.0

        self.play_once = False  # controla animações que só rodam uma vez
        self.next_anim_after_once = "idle"

        self.play_once_speed = 10  # frames que cada quadro vai durar
        self.play_once_counter = 0

        self.space = space  # Guardamos referência ao espaço de física
        mass = 1  # massa do plaYer
        moment = pm.moment_for_box(mass, size)
        self.body = pm.Body(mass, moment, pm.Body.DYNAMIC)  # corpo dinâmico
        self.body.position = pos
        self.shape = pm.Poly.create_box(
            self.body, size
        )  # shape do player (pra colisões e afins)
        self.shape.friction = 0.0  # fricção do shape
        self.shape.elasticity = 0.0  # elasticidade do shape

        self.space.add(self.body, self.shape)  # Adicionamos ao espaço de física

        self.on_ground = False
        self.ground_shape = None
        self.jump_pressed = False

        self.life_number = 5
        self.last_contact = 0.0

        self.keys_pressed = set()
        self.interactable = (
            set()  # set que armazena os objetos que pode interagir com a tecla "E"
        )  # (provavelmente não é o melhor jeito de se fazer isso)
        self.used_E = False

        self.sound_controller = None
        self.can_interact = True

    def check_if_on_ground(self):
        """Verifica se o Player está tocando o chão"""
        self.on_ground = False

        for i in self.ground_shape:
            if i.bb.intersects(self.shape.bb):
                self.on_ground = True

        if self.on_ground and not ({pg.K_UP, pg.K_SPACE, pg.K_w} & self.keys_pressed):
            self.jump_pressed = False

    def animate(self):
        frames = self.animations[self.current_anim]

        if self.play_once:  # animações de fail e success controladas aqui
            self.play_once_counter += 1

            if self.play_once_counter >= self.play_once_speed:
                self.play_once_counter = 0
                self.anim_index += 1

                # se terminou a sequência
                if self.anim_index >= len(frames):
                    self.play_once = False
                    self.current_anim = self.next_anim_after_once
                    frames = self.animations[self.current_anim]
                    self.anim_index = 0

        else:
            # animações normais (usam anim_speed)
            self.anim_timer += self.anim_speed
            if self.anim_timer >= 1:
                self.anim_timer = 0
                self.anim_index += 1

                # trava último frame do pulo
                if self.current_anim in ["right_jump", "left_jump", "jump"] and self.anim_index >= len(frames):
                    self.anim_index = len(frames) - 1
                else:
                    self.anim_index %= len(frames)

        # define a imagem atual (garante índice válido)
        self.image = frames[min(self.anim_index, len(frames) - 1)]

    def play_animation_once(self, anim_name: str, after="idle"):
        """Dispara uma animação que roda uma única vez"""
        if anim_name in self.animations and not self.play_once:
            self.current_anim = anim_name
            self.anim_index = 0
            self.anim_timer = 0
            self.play_once = True
            self.next_anim_after_once = after
            self.play_once_counter = 0

    def loose_life(self):
        self.life_number -= 1
        self.sound_controller.sounds['loose_life'][1].play()
        self.sound_controller.sounds["loose_life"][1].set_volume(0.3)

    def update(self):
        self.check_if_on_ground()

        self.handle_movement()
        self.rect.center = self.body.position.x, self.body.position.y - 12

        self.animate()

    def input_handler(self, keys):
        self.keys_pressed = keys

        for key in self.keys_pressed:
            # if key == pg.K_r:
            #     self.revive()

            if key == pg.K_e:  # interação com objetos pela tecla
                for _sprite in self.interactable:
                    if (
                            pg.math.Vector2(self.rect.center).distance_to(
                                _sprite.rect.center
                            )
                            <= ((self.rect.size[0] + _sprite.rect.size[0]) / 2) + 25
                    ):
                        self.body.velocity = (0.0, 0.0)
                        self.used_E = True
                        if self.can_interact:
                            _sprite.on_interaction()
                            self.current_anim = "idle"

            # if key == pg.K_t:
            #     self.loose_life()

    def handle_movement(self):
        if self.can_move:
            fx = 0  # força no eixo X

            # percorre as teclas pressionadas
            for key in self.keys_pressed:
                if key in DEFAULT_CONTROLS:
                    dx, dy = DEFAULT_CONTROLS[key]
                    fx += dx * self.body.mass  # Aplica força proporcional à massa
                    # verifica salto
                    if (
                            key in {pg.K_UP, pg.K_w}
                            and self.on_ground
                            and not self.jump_pressed
                    ):
                        self.body.apply_impulse_at_local_point((0, dy), (0, 0))
                        self.jump_pressed = True

            # Aplica a força apenas enquanto há teclas pressionadas
            if not self.on_ground:
                if not self.anim_jump:
                    self.anim_index = 0
                    self.anim_jump = True

                if self.body.velocity[0] > 0:
                    self.current_anim = "right_jump"
                elif self.body.velocity[0] < 0:
                    self.current_anim = "left_jump"
                else:
                    self.current_anim = "jump"

            else:
                self.anim_jump = False
                if fx:
                    self.body.force = (fx, 0)
                    if fx > 0:
                        self.current_anim = "right"

                    else:
                        self.current_anim = "left"

                    # limitação de velocidade horizontal
                    if self.body.velocity[0] > MAX_SPEED:
                        self.body.velocity = (MAX_SPEED, self.body.velocity[1])
                    if self.body.velocity[0] < -MAX_SPEED:
                        self.body.velocity = (-MAX_SPEED, self.body.velocity[1])
                else:
                    self.body.velocity = (0, self.body.velocity.y)
                    if not self.play_once:
                        self.current_anim = "idle"
                        self.anim_index = 0

        # evita rotação do corpo
        self.body.angular_velocity = 0
        self.body.angle = 0

    def revive(self):
        self.life_number = 5
