import pygame as pg
from ..core import configs
from ..core.state_machine import State


class Intro(State):
    """
    State for the opening intro of the game
    """

    def __init__(self):
        super().__init__()
        self.next = "MENU"
        self.fade_time = 3.5  # total animation time for intro
        self.fade_percentage = 0.75  # Percentage of time for fade-in
        self.fade_in_time = self.fade_time * self.fade_percentage  # total fade-in time
        self.delay_time = 10.0  # delay before starting fade-in (in seconds)

        self.alpha = 0  # start value for alpha
        self.image = configs.GFX["others"]["intro_img_1"].copy().convert()
        self.image = pg.transform.smoothscale(self.image, (configs.WINDOW_WIDTH, configs.WINDOW_HEIGHT))
        self.rect = self.image.get_rect(center=configs.SCREEN_RECT.center)

        self.total_time = 0
        self.fade_speed = 255 / self.fade_in_time  # increment for alpha in fade-in

        self.start_song = False

    def startup(self, now, persistant):
        super().startup(now, persistant)
        self.alpha = 0
        self.total_time = 0.0
        self.image.set_alpha(self.alpha)

    def cleanup(self):
        return super().cleanup()

    def update(self, keys, now):
        """Updates the intro screen"""
        delta_time = (now - self.start_time) / 1000.0
        self.total_time += delta_time
        self.start_time = now

        if self.total_time <= self.delay_time:
            # durante o delay, nada acontece
            self.alpha = 0
        elif self.total_time <= self.delay_time + self.fade_in_time:

            if not self.start_song:
                pg.mixer.music.load("resources/sound/sound_1.mp3")
                pg.mixer.music.set_volume(0.3)
                pg.mixer.music.play(-1)
                self.start_song = True
            # inicia o fade-in depois do delay
            self.alpha = min(
                self.alpha + self.fade_speed * delta_time, 255
            )
        else:
            # imagem totalmente visível
            self.alpha = 255

        self.image.set_alpha(self.alpha)

        # estado termina após delay + fade + restante do tempo
        if self.total_time >= self.delay_time + self.fade_time:
            self.done = True

    def draw(self, surface):
        # surface.fill(configs.BG_COLOR)
        surface.blit(self.image, self.rect)

    def get_event(self, event):
        """
        Get events from Control. Changes to next state on any key press.
        """
        if event.type == pg.QUIT:
            self.quit = True
        self.done = event.type == pg.KEYDOWN
