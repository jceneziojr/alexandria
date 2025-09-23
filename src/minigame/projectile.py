import pygame as pg
import numpy as np
from .minigame_manager import MiniGame
from ..core.configs import WINDOW_WIDTH, WINDOW_HEIGHT, GFX

GRAVITY = 9.8  # m/s²
SCALE = 10  # Pixels por metro (ajuste para caber na tela)


class ProjectileMiniGame(MiniGame):
    def __init__(self, size):
        super().__init__(size)
        self.y0 = 0  # altura inicial em metros
        self.delta = 10  # ângulo em graus
        self.v0 = 20  # velocidade inicial (fixa para simplificação)
        self.font = pg.font.Font(None, 24)

        button_y = self.height - 60  # mesma altura para todos os botões

        self.buttons = [
            ("- y", pg.Rect(60, button_y, 40, 30), "y0", -1),
            ("+ y", pg.Rect(110, button_y, 40, 30), "y0", 1),
            ("- α", pg.Rect(275, button_y, 40, 30), "delta", -1),
            ("+ α", pg.Rect(325, button_y, 40, 30), "delta", 1),
            ("OK", pg.Rect(self.width - 100, button_y, 50, 30), "finish", None),
        ]

        self.mouse_click = False
        self.mouse_pos = (0, 0)
        self.ground_y = self.height - 150  # posição Y do chão (em pixels)

        # ponto alvo no chão
        self.target_x = self.width // 2 + 50  # ponto alvo
        self.target_y = self.ground_y
        self.tolerance = 10  # tolerância em pixels para considerar acerto

        # timer para feedback após falha
        self.feedback_timer = 0

    def handle_event(self, event, keys):
        super().handle_event(event, keys)
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            rel_mouse_pos = pg.mouse.get_pos()
            rel_mouse_pos = (rel_mouse_pos[0] - (WINDOW_WIDTH - self.width) // 2,
                             rel_mouse_pos[1] - (WINDOW_HEIGHT - self.height) // 2)
            self.mouse_click = True
            self.mouse_pos = rel_mouse_pos

    def update(self, dt):
        # Atualiza o timer de feedback se estiver ativo
        if self.feedback_timer > 0:
            self.feedback_timer -= dt * 1000  # dt em segundos, timer em ms
            if self.feedback_timer <= 0:
                self.feedback_timer = 0
                self.finished = True
            return

        if self.mouse_click:
            for text, rect, param, change in self.buttons:
                if rect.collidepoint(self.mouse_pos):
                    if param == "y0":
                        self.y0 = max(0, min(50, self.y0 + change))
                    elif param == "delta":
                        self.delta = max(10, min(89, self.delta + change))
                    elif param == "finish":
                        x_px, y_px = self.compute_trajectory()
                        final_x, final_y = x_px[-1], y_px[-1]
                        dist = ((final_x - self.target_x) ** 2 + (final_y - self.target_y) ** 2) ** 0.5

                        if dist <= self.tolerance:
                            self.finished = True
                        else:
                            self.failed = True
                            self.feedback_timer = 1000  # 1 segundo de espera antes de fechar
            self.mouse_click = False

    def compute_trajectory(self):
        v0 = self.v0
        g = GRAVITY
        theta = np.radians(self.delta)
        v0x = v0 * np.cos(theta)
        v0y = v0 * np.sin(theta)

        t_flight = (v0y + np.sqrt(v0y ** 2 + 2 * g * self.y0)) / g
        t_vals = np.linspace(0, t_flight, num=200)

        x_vals = v0x * t_vals
        y_vals = self.y0 + v0y * t_vals - 0.5 * g * t_vals ** 2

        max_display_y = max(self.y0 + 40, 50)
        scale_y = (self.ground_y - 20) / max_display_y

        max_range = 100  # escala fixa para mostrar variações reais no alcance
        scale_x = self.width / max_range

        offset_x = 40

        x_px = [int(x * scale_x) + offset_x for x in x_vals]
        y_px = [int(self.ground_y - y * scale_y) for y in y_vals]

        return x_px, y_px

    def draw(self, surface):
        # surface.fill((255, 255, 255))

        minigame_surface = pg.transform.smoothscale(
            GFX["others"]["minigame_bg"],
            (surface.width, surface.height)
        ).convert_alpha()
        surface.blit(minigame_surface)

        pg.draw.line(surface, (100, 100, 100), (100, self.ground_y), (self.width - 100, self.ground_y), 2)

        sprite = GFX["minigame_assets"]["flag"]
        sprite_rect = sprite.get_rect(center=(self.target_x, self.target_y - 20))
        surface.blit(sprite, sprite_rect)

        # Desenhar trajetória
        x_px, y_px = self.compute_trajectory()
        offset = 5  # número de pontos para pular no início
        for i in range(offset, len(x_px) - 1):
            if 0 <= x_px[i] < self.width and 0 <= y_px[i] < self.height:
                pg.draw.line(surface, (0, 0, 255), (x_px[i], y_px[i]), (x_px[i + 1], y_px[i + 1]), 2)

        if 0 <= x_px[-1] < self.width and 0 <= y_px[-1] < self.height:
            pg.draw.circle(surface, (255, 0, 0), (int(x_px[-1]), int(y_px[-1])), 5)

        # Sprite do canhão
        canon_sprite = GFX["minigame_assets"]["canon"]

        # Ângulo com compensação
        rotation_angle = (self.delta - 10)
        rotated_canon = pg.transform.rotozoom(canon_sprite, rotation_angle, 0.08)

        # Centralizar no ponto de lançamento
        canon_rect = rotated_canon.get_rect(center=(x_px[0], y_px[0] + 5))
        surface.blit(rotated_canon, canon_rect)

        # Desenhar botões
        for text, rect, _, _ in self.buttons:
            pg.draw.rect(surface, (0, 200, 0), rect)
            label = self.font.render(text, True, (0, 0, 0))
            surface.blit(label, (rect.x + 5, rect.y + 5))

        # Mostrar valores acima dos botões
        altura_text = self.font.render(f"{self.y0:.1f} m", True, (0, 0, 0))
        angulo_text = self.font.render(f"{self.delta:.1f}°", True, (0, 0, 0))

        # Títulos de controle
        altura_title = self.font.render("Controle da altura", True, (0, 0, 0))
        angulo_title = self.font.render("Controle de ângulo", True, (0, 0, 0))

        # Desenhar textos (títulos mais acima, valores logo abaixo deles)
        surface.blit(altura_title, (85 + 20 - altura_title.get_width() // 2, self.height - 120))
        surface.blit(altura_text, (85 + 20 - altura_text.get_width() // 2, self.height - 90))

        surface.blit(angulo_title, (305 + 20 - angulo_title.get_width() // 2, self.height - 120))
        surface.blit(angulo_text, (305 + 20 - angulo_text.get_width() // 2, self.height - 90))
