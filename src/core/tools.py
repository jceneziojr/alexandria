import os
from typing import Tuple, Dict, Literal, Union
import pygame as pg
import pymunk as pm
import pymunk.pygame_util
from . import configs
from .state_machine import StateMachine
from ..core.sound_controller import SoundController


class Controller:
    """
    Roda o jogo e comanda o loop de eventos
    """

    def __init__(self, game_window_title: Union[str, Literal["AlexandriA"]]):
        self.screen = pg.display.set_mode(
            (configs.WINDOW_WIDTH, configs.WINDOW_HEIGHT)
        )  # configura o tamanho do display, adicionar a flag pg.RESIZABLE permite modificar o tamanho dinamicamente
        self.title = game_window_title  # nome da janela do jogo
        self.done = False  # checa se o jogo acabou de rodar
        self.clock = pg.time.Clock()  # controla a passagem de tempo da simulação
        self.fps = configs.FPS  # fps da simulação
        self.fps_visible = True  # mostrar o fps
        self.now = 0.0  # variável para guardar o tempo total da simulação
        self.keys = pg.key.get_pressed()  # teclas pressionadas

        self.space = pm.Space()  # Criando o espaço do pymunk
        self.space.gravity = (
            0,
            configs.GRAVITY,
        )  # constante de gravidade em y do espaço do pymunk

        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        self.state_machine = StateMachine(
            self.space, self.draw_options
        )  # maquina de estados, preciso passar espaço e esse draw_opt para rodar o game de forma correta

    def update(self):
        """
        método de atualização
        """
        self.now = pg.time.get_ticks()  # pega o tempo total da simulação
        self.state_machine.update(
            self.keys, self.now
        )  # chama o método de update da máquina de estados
        self.done = (
            self.state_machine.done
        )  # o jogo acaba se a máquina de estados finalizar a execução

    def draw(self):
        if not self.state_machine.state.done:  # se o estado não tiver sido concluído
            self.state_machine.draw(
                self.screen
            )  # chama o método de draw da máquina de estados
            pg.display.update()  # atualiza o conteúdo da tela
            self.show_fps()

    def event_loop(self):
        """
        processador de eventos
        """

        for event in pg.event.get():  # pega os eventos capturados pelo pygame
            if event.type == pg.QUIT:  # checa se clicou o botão de fechar
                self.done = True
                self.state_machine.get_event(event)

            elif event.type == pg.KEYDOWN:  # checa se pressionou uma tecla
                self.toggle_show_fps(event.key)
                self.state_machine.get_event(
                    event
                )  # passa o evento para máquina de estados
            #
            elif event.type == pg.KEYUP:  # checa se soltou alguma tecla
                self.state_machine.get_event(
                    event
                )  # passa o evento para máquina de estados

            elif event.type in [pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP, pg.MOUSEMOTION]:
                self.state_machine.get_event(event)

    def toggle_show_fps(self, key: int):
        """F5 mostra o fps"""
        if key == pg.K_F5:
            self.fps_visible = not self.fps_visible
            if not self.fps_visible:
                pg.display.set_caption(self.title)

    def show_fps(self):
        """
        mostra o fps
        """
        if self.fps_visible:
            fps = self.clock.get_fps()
            with_fps = "{} - {:.2f} FPS".format(self.title, fps)
            pg.display.set_caption(with_fps)

    def main(self):
        # loop principal

        sound_controller = SoundController()
        self.state_machine.state.startup(self.clock.tick(self.fps),
                                         {"sound_controller": sound_controller, "draw_opt": self.draw_options,
                                          "space": self.space})
        while not self.done:
            self.event_loop()
            self.clock.tick(self.fps)
            self.space.step(1 / configs.FPS)
            self.update()
            self.draw()


class BaseEntity(pg.sprite.Sprite):

    def __init__(
            self,
            groups: pg.sprite.Group,
            pos: Tuple[int, int],
            size: Union[Tuple[int, int], Tuple[float, float]] = None,
            image: pg.Surface = None,
    ):
        super().__init__(groups)

        size = size or configs.PLAYER_SIZE
        self.image = (
            image if image is not None else pg.Surface(size)
        )  # para lidar com as imgs da Sprite
        self.rect = self.image.get_rect(topleft=pos)

    def collision_change(self, collide):
        """
        essa função é para ter override nas classes herdeiras, quando houver colisão com o player
        """
        pass


def load_all_gfx(
        directory: str,
        colorkey: Tuple[int] = (255, 0, 255),
        accept: Tuple[str] = (".png", ".jpg", ".bmp", ".jpeg"),
) -> Dict[str, pg.Surface]:
    """
    Load all graphics with extensions in the accept argument.  If alpha
    transparency is found in the image, it will be converted using
    convert_alpha().  If no alpha transparency is detected image will be
    converted using convert() and colorkey will be set to colorkey.
    """
    graphics = {}
    for pic in os.listdir(directory):
        name, ext = os.path.splitext(pic)
        if ext.lower() in accept:
            img = pg.image.load(os.path.join(directory, pic))
            if img.get_alpha():
                img = img.convert_alpha()
            else:
                img = img.convert()
                img.set_colorkey(colorkey)
            graphics[name] = img
    return graphics
