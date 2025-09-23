import pygame as pg
from ..core import configs
from ..core.state_machine import State


class Credits(State):
    """
    Mostra os créditos como uma sequência de frames.
    Ao terminar, fica parado no último frame até o jogador apertar uma tecla.
    """

    def __init__(self):
        super().__init__()
        self.next = "MENU"

        # Carrega e redimensiona os 50 frames da animação
        self.frames = [
            pg.transform.smoothscale(
                configs.GFX["credits"][f"frame_{i}"].copy().convert(),
                (configs.WINDOW_WIDTH, configs.WINDOW_HEIGHT)
            )
            for i in range(1, 51)
        ]

        self.frame_index = 0
        self.frame_time = 0.04  # duração de cada frame (~25 FPS)
        self.total_time = 0.0
        self.animation_finished = False  # controle para saber quando parar no último frame

    def startup(self, now, persistant):
        super().startup(now, persistant)
        self.frame_index = 0
        self.total_time = 0.0
        self.animation_finished = False

        pg.mixer.music.load("resources/sound/sound_2.mp3")
        pg.mixer.music.set_volume(0.3)
        pg.mixer.music.play(-1)

    def cleanup(self):
        return super().cleanup()

    def update(self, keys, now):
        if self.animation_finished:
            return  # já terminou, fica parado no último frame

        delta_time = (now - self.start_time) / 1000.0
        self.start_time = now
        self.total_time += delta_time

        if self.total_time >= self.frame_time:
            self.total_time -= self.frame_time
            self.frame_index += 1

            if self.frame_index >= len(self.frames):
                self.frame_index = len(self.frames) - 1  # mantém no último frame
                self.animation_finished = True  # agora só sai se apertar tecla

    def draw(self, surface):
        surface.blit(self.frames[self.frame_index], (0, 0))

    def get_event(self, event):
        if event.type == pg.QUIT:
            self.quit = True
        # Só sai quando o player apertar tecla depois do fim da animação
        if event.type == pg.KEYDOWN and self.animation_finished:
            self.done = True
