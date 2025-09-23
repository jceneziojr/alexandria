import pygame as pg
import numpy as np
import matplotlib.pyplot as plt
import io
from .minigame_manager import MiniGame
from ..core.configs import WINDOW_WIDTH, WINDOW_HEIGHT, GFX


class ParameterEstimationMiniGame(MiniGame):
    def __init__(self, size):
        super().__init__(size)

        self.font = pg.font.Font(None, 24)

        # --- Dados reais ---
        np.random.seed(0)
        self.x = np.linspace(-3, 3, 50)
        self.y_real = 1.0 + 2.0 * self.x - 0.5 * self.x ** 2 + 0.5 * np.random.randn(len(self.x))

        # --- Ajuste por mínimos quadrados (LS) ---
        self.X = np.vstack([np.ones_like(self.x), self.x, self.x ** 2]).T
        self.ls_params, *_ = np.linalg.lstsq(self.X, self.y_real, rcond=None)
        self.y_ls = self.X @ self.ls_params

        # --- Ajuste alternativo (forçado ruim) ---
        alt_params = self.ls_params + np.array([0.5, -0.3, 0.2])
        self.y_alt = self.X @ alt_params

        # --- Ajuste manual do usuário ---
        self.manual_params = np.array([0.0, 0.0, 0.0])
        self.y_manual = self.X @ self.manual_params

        # --- Layout dos botões ---
        self.ok_button = pg.Rect(self.width - 120, self.height - 70, 100, 40)
        button_y = self.height - 70  # mesma altura do OK
        spacing = 120
        start_x = 20
        self.param_buttons = []
        names = ["p0", "p1", "p2"]
        for i, name in enumerate(names):
            base_x = start_x + i * spacing
            plus_rect = pg.Rect(base_x, button_y, 40, 40)
            minus_rect = pg.Rect(base_x + 50, button_y, 40, 40)
            self.param_buttons.append({"name": name, "plus": plus_rect, "minus": minus_rect})

        self.mouse_click = False
        self.mouse_pos = (0, 0)
        self.plot_surface = None
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
            for i, btn in enumerate(self.param_buttons):
                if btn["plus"].collidepoint(self.mouse_pos):
                    self.manual_params[i] += 0.1
                    self.need_redraw = True
                elif btn["minus"].collidepoint(self.mouse_pos):
                    self.manual_params[i] -= 0.1
                    self.need_redraw = True

            if self.ok_button.collidepoint(self.mouse_pos):
                self.finished = True
                self.success = True

            self.mouse_click = False

        self.y_manual = self.X @ self.manual_params

    # --- Gera gráfico ---
    def generate_plot_surface(self):
        fig, ax = plt.subplots(figsize=(6, 3), constrained_layout=True)

        ax.scatter(self.x, self.y_real, color="black", s=20, label="Dados reais")
        ax.plot(self.x, self.y_ls, "b-", label="Mínimos Quadrados")
        ax.plot(self.x, self.y_alt, "g--", label="Método alternativo")
        ax.plot(self.x, self.y_manual, "r:", linewidth=2, label="Manual")

        ax.set_title("Estimação de Parâmetros")
        ax.set_xlabel("x")
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

    # --- EQM ---
    def mse(self, y_hat):
        return np.mean((self.y_real - y_hat) ** 2)

    def draw(self, surface):
        minigame_surface = pg.transform.smoothscale(
            GFX["others"]["minigame_bg"],
            (surface.width, surface.height)
        ).convert_alpha()
        surface.blit(minigame_surface)

        # Atualiza ou redesenha o gráfico
        if self.plot_surface is None or self.need_redraw:
            self.plot_surface = self.generate_plot_surface()
            self.need_redraw = False
            self.size_adjusted = (self.plot_surface.width * 0.9, self.plot_surface.height * 0.9)

        # Desenha gráfico no centro
        self.plot_surface = pg.transform.smoothscale(self.plot_surface, self.size_adjusted)
        plot_rect = self.plot_surface.get_rect(center=(self.width // 2, self.height // 2 - 90))
        surface.blit(self.plot_surface, plot_rect)

        # --- Botões e labels dos parâmetros ---
        for i, btn in enumerate(self.param_buttons):
            name = btn["name"]
            # botões
            pg.draw.rect(surface, (200, 200, 200), btn["plus"])
            pg.draw.rect(surface, (200, 200, 200), btn["minus"])
            plus_label = self.font.render("+", True, (0, 0, 0))
            minus_label = self.font.render("-", True, (0, 0, 0))
            surface.blit(plus_label, (btn["plus"].x + 12, btn["plus"].y + 8))
            surface.blit(minus_label, (btn["minus"].x + 12, btn["minus"].y + 8))

            # texto acima centralizado no par
            center_x = (btn["plus"].x + btn["minus"].x + btn["minus"].width) // 2
            param_val = self.font.render(f"{name}", True, (0, 0, 0))
            text_x = center_x - param_val.get_width() // 2
            text_y = btn["plus"].y - 30
            surface.blit(param_val, (text_x, text_y))

        # --- EQMs em uma única linha ---
        eqm_ls = self.mse(self.y_ls)
        eqm_alt = self.mse(self.y_alt)
        eqm_manual = self.mse(self.y_manual)
        metrics_text = f"EQM (LS): {eqm_ls:.2f}   |   EQM (Alt): {eqm_alt:.2f}   |   EQM (Manual): {eqm_manual:.2f}"
        metrics_label = self.font.render(metrics_text, True, (0, 0, 0))
        metrics_rect = metrics_label.get_rect(center=(self.width // 2, plot_rect.bottom + 20))
        surface.blit(metrics_label, metrics_rect)

        # --- Equação do modelo manual ---
        p0, p1, p2 = self.manual_params
        eq_text = f"Modelo manual: y = {p0:.2f} + {p1:.2f}·x + {p2:.2f}·x²"
        eq_label = self.font.render(eq_text, True, (0, 0, 0))
        eq_rect = eq_label.get_rect(center=(self.width // 2, metrics_rect.bottom + 20))
        surface.blit(eq_label, eq_rect)

        # --- Botão OK ---
        pg.draw.rect(surface, (0, 150, 0), self.ok_button)
        ok_label = self.font.render("OK", True, (255, 255, 255))
        surface.blit(ok_label, (self.ok_button.x + 35, self.ok_button.y + 10))
