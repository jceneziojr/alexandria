import pygame as pg
import numpy as np
import matplotlib.pyplot as plt
import io
from .minigame_manager import MiniGame
from ..core.configs import WINDOW_WIDTH, WINDOW_HEIGHT, GFX


class OverfittingMiniGame(MiniGame):
    def __init__(self, size):
        super().__init__(size)
        self.font = pg.font.Font(None, 24)

        # --- Dados amostrados ---
        np.random.seed(1)
        self.x = np.linspace(-3, 3, 40)
        self.y_sampled = np.sin(self.x) + 0.2 * np.random.randn(len(self.x))

        # --- Grau do polinômio (ajustável) ---
        self.degree = 1
        self.max_degree = 30

        # --- Botões ---
        self.ok_button = pg.Rect(self.width - 120, self.height - 60, 100, 40)
        self.plus_button = pg.Rect(20, self.height - 60, 40, 40)
        self.minus_button = pg.Rect(70, self.height - 60, 40, 40)

        self.mouse_click = False
        self.mouse_pos = (0, 0)
        self.plot_surface = None
        self.need_redraw = True

        self.update_fit()

    # --- Atualiza ajuste ---
    def update_fit(self):
        self.coeffs = np.polyfit(self.x, self.y_sampled, self.degree)
        # Para mostrar além do intervalo dos dados
        self.x_fit = np.linspace(self.x[0] - 1, self.x[-1] + 1, 200)
        self.y_fit = np.polyval(self.coeffs, self.x_fit)
        # EQM
        self.eqm = np.mean((np.polyval(self.coeffs, self.x) - self.y_sampled) ** 2)
        self.need_redraw = True

    # --- Eventos ---
    def handle_event(self, event, keys):
        super().handle_event(event, keys)
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            rel_mouse_pos = pg.mouse.get_pos()
            rel_mouse_pos = (
                rel_mouse_pos[0] - (WINDOW_WIDTH - self.width) // 2,
                rel_mouse_pos[1] - (WINDOW_HEIGHT - self.height) // 2,
            )
            self.mouse_click = True
            self.mouse_pos = rel_mouse_pos

    # --- Atualização ---
    def update(self, dt):
        if self.mouse_click:
            if self.plus_button.collidepoint(self.mouse_pos) and self.degree < self.max_degree:
                self.degree += 1
                self.update_fit()
            elif self.minus_button.collidepoint(self.mouse_pos) and self.degree > 1:
                self.degree -= 1
                self.update_fit()
            elif self.ok_button.collidepoint(self.mouse_pos):
                self.finished = True
                self.success = True
            self.mouse_click = False

    # --- Gera gráfico ---
    def generate_plot_surface(self):
        fig, ax = plt.subplots(figsize=(6, 3), constrained_layout=True)
        ax.scatter(self.x, self.y_sampled, color="black", s=20, label="Pontos amostrados")
        ax.plot(self.x_fit, self.y_fit, "r-", label=f"Ajuste grau {self.degree}")
        ax.set_title(f"Ajuste de polinômio (EQM={self.eqm:.3f})")
        ax.set_xlabel("x")
        ax.set_ylim(-3, 3)
        # ax.set_xlim(-3, 3)
        ax.set_ylabel("y")
        ax.grid(True)
        ax.legend(fontsize=8, loc="lower right")

        buf = io.BytesIO()
        fig.canvas.print_rgba(buf)
        buf.seek(0)
        w, h = fig.canvas.get_width_height()
        img = np.frombuffer(buf.getvalue(), dtype=np.uint8).reshape(h, w, 4)
        buf.close()
        plt.close(fig)
        img_rgb = img[:, :, :3]
        return pg.surfarray.make_surface(np.transpose(img_rgb, (1, 0, 2)))

    # --- Desenho ---
    def draw(self, surface):
        minigame_surface = pg.transform.smoothscale(
            GFX["others"]["minigame_bg"],
            (surface.width, surface.height)
        ).convert_alpha()
        surface.blit(minigame_surface)

        if self.plot_surface is None or self.need_redraw:
            self.plot_surface = self.generate_plot_surface()
            self.need_redraw = False
            self.size_adjusted = (self.plot_surface.width * 0.9, self.plot_surface.height * 0.9)

        self.plot_surface = pg.transform.smoothscale(self.plot_surface, self.size_adjusted)
        plot_rect = self.plot_surface.get_rect(center=(self.width // 2, self.height // 2 - 50))
        surface.blit(self.plot_surface, plot_rect)

        # --- Botões grau ---
        pg.draw.rect(surface, (200, 200, 200), self.plus_button)
        pg.draw.rect(surface, (200, 200, 200), self.minus_button)
        surface.blit(self.font.render("+", True, (0, 0, 0)), (self.plus_button.x + 15, self.plus_button.y + 10))
        surface.blit(self.font.render("-", True, (0, 0, 0)), (self.minus_button.x + 18, self.minus_button.y + 10))

        # --- Texto grau ---
        degree_label = self.font.render(f"Grau: {self.degree}", True, (0, 0, 0))
        surface.blit(degree_label, (120, self.height - 45))

        # --- Botão OK ---
        pg.draw.rect(surface, (0, 150, 0), self.ok_button)
        ok_label = self.font.render("OK", True, (255, 255, 255))
        surface.blit(ok_label, (self.ok_button.x + 35, self.ok_button.y + 10))
