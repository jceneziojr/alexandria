import pygame as pg
import numpy as np
from .minigame_manager import MiniGame
from ..core.configs import WINDOW_WIDTH, WINDOW_HEIGHT, GFX


class SineWaveMiniGame(MiniGame):
    def __init__(self, size):
        super().__init__(size)
        self.amplitude = 100
        self.frequency = 2
        self.phase = 0
        self.font = pg.font.Font(None, 24)

        # Botões com retângulos já posicionados
        self.buttons = [
            ("A+", pg.Rect(10, 10, 40, 30), "amp", 10),
            ("A-", pg.Rect(60, 10, 40, 30), "amp", -10),
            ("F+", pg.Rect(110, 10, 40, 30), "freq", 0.5),
            ("F-", pg.Rect(160, 10, 40, 30), "freq", -0.5),
            ("P+", pg.Rect(210, 10, 40, 30), "fase", np.pi / 8),
            ("P-", pg.Rect(260, 10, 40, 30), "fase", -np.pi / 8),
            ("OK", pg.Rect(self.width - 60, self.height - 40, 50, 30), "finish", None),
        ]

        self.mouse_click = False
        self.mouse_pos = (0, 0)

    def handle_event(self, event, keys):
        super().handle_event(event, keys)
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            # Captura o clique relativo ao minigame_surface
            rel_mouse_pos = pg.mouse.get_pos()
            # Corrigir posição relativa ao rect do minigame
            rel_mouse_pos = (rel_mouse_pos[0] - (WINDOW_WIDTH - self.width) // 2,
                             rel_mouse_pos[1] - (WINDOW_HEIGHT - self.height) // 2)

            self.mouse_click = True
            self.mouse_pos = rel_mouse_pos

    def update(self, dt):
        if self.mouse_click:
            for text, rect, param, change in self.buttons:
                if rect.collidepoint(self.mouse_pos):
                    if param == "amp":
                        self.amplitude = max(10, self.amplitude + change)
                    elif param == "freq":
                        self.frequency = max(0.1, self.frequency + change)
                    elif param == "fase":
                        self.phase += change
                    elif param == "finish":
                        self.finished = True
            self.mouse_click = False  # resetar clique

    def draw(self, surface):
        minigame_surface = pg.transform.smoothscale(
            GFX["others"]["minigame_bg"],
            (surface.width, surface.height)
        ).convert_alpha()
        surface.blit(minigame_surface)

        # Desenhar senoide
        for x in range(self.width):
            y = int(self.height / 2 + self.amplitude * np.sin(self.frequency * (x * 0.05) + self.phase))
            if 0 <= y < self.height:
                pg.draw.circle(surface, (0, 0, 255), (x, y), 1)

        # Desenhar botões
        for text, rect, _, _ in self.buttons:
            pg.draw.rect(surface, (0, 200, 0), rect)
            label = self.font.render(text, True, (0, 0, 0))
            surface.blit(label, (rect.x + 5, rect.y + 5))

        # Mostrar valores
        surface.blit(self.font.render(f"Amp: {self.amplitude}", True, (0, 0, 0)), (10, 60))
        surface.blit(self.font.render(f"Freq: {self.frequency:.2f}", True, (0, 0, 0)), (10, 80))
        surface.blit(self.font.render(f"Phase: {self.phase:.2f}", True, (0, 0, 0)), (10, 100))
