import pygame as pg
from ..core import configs
from ..core.state_machine import State


class GameOver(State):
    """
    State for the Game Over screen with fade-in
    """

    def __init__(self):
        super().__init__()
        self.next = "MENU"  # estado para onde ir após o Game Over
        self.fade_time = 3  # duração total da animação
        self.fade_percentage = 0.6  # porcentagem do tempo dedicada ao fade-in
        self.fade_in_time = self.fade_time * self.fade_percentage
        self.alpha = 0

        self.image = configs.GFX["others"]["game_over"].copy().convert()
        self.rect = self.image.get_rect(center=configs.SCREEN_RECT.center)

        self.total_time = 0
        self.fade_speed = 255 / self.fade_in_time  # velocidade do alpha

    def startup(self, now, persistant):
        super().startup(now, persistant)
        self.alpha = 0
        self.total_time = 0.0
        self.image.set_alpha(self.alpha)
        pg.mixer.music.load("resources/sound/game_over.mp3")
        pg.mixer.music.set_volume(0.3)
        pg.mixer.music.play(1)

    def cleanup(self):
        self.done = False  # important, otherwise it will persist
        return super().cleanup()

    def update(self, keys, now):
        """
        Faz o fade-in da imagem, mas não troca de estado automaticamente.
        Só sai se o jogador apertar uma tecla.
        """
        delta_time = (now - self.start_time) / 1000.0
        self.total_time += delta_time
        self.start_time = now

        if self.total_time <= self.fade_in_time:
            self.alpha = min(self.alpha + self.fade_speed * delta_time, 255)
        else:
            self.alpha = 255

        self.image.set_alpha(self.alpha)

    def draw(self, surface):
        surface.fill(configs.BG_COLOR)
        surface.blit(self.image, self.rect)

    def get_event(self, event):
        """
        Só sai do Game Over em qualquer tecla pressionada ou quit.
        """
        if event.type == pg.QUIT:
            self.quit = True
            pg.mixer.music.stop()
        elif event.type == pg.KEYDOWN:
            self.done = True
            pg.mixer.music.stop()
