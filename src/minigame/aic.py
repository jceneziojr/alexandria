import pygame as pg
import numpy as np
import matplotlib.pyplot as plt
import io
from .minigame_manager import MiniGame
from ..core.configs import WINDOW_WIDTH, WINDOW_HEIGHT, GFX


class AICMiniGame(MiniGame):
    def __init__(self, size):
        super().__init__(size)

        self.font = pg.font.Font(None, 22)
        self.large_font = pg.font.Font(None, 28)

        # --- Termos candidatos (nome, ΔErro, Complexidade) ---
        self.terms = [
            {"name": "y(k-1)", "delta_error": 5.0, "complexity": 1.0},
            {"name": "u(k-1)", "delta_error": 4.0, "complexity": 1.0},
            {"name": "y(k-1)*u(k-1)", "delta_error": 3.5, "complexity": 1.5},
            {"name": "y(k-2)", "delta_error": 2.0, "complexity": 1.5},
            {"name": "u(k-2)", "delta_error": 0.2, "complexity": 3.0},
        ]

        self.selected_terms = []
        self.error = 20.0  # erro inicial
        self.complexity = 0.0
        self.aic = self.error + self.complexity

        # --- Calcula o menor AIC possível ---
        self.min_aic_target = 10.5

        # --- Botões horizontais (parte inferior) ---
        spacing = 40
        start_x = 20
        button_y = self.height - 100  # próximo da parte inferior
        self.buttons = []
        for i, term in enumerate(self.terms):
            rect = pg.Rect(start_x + i * (75 + spacing), button_y, 100, 40)
            self.buttons.append({"term": term, "rect": rect})

        # Botão OK para finalizar
        self.ok_button = pg.Rect(self.width - 120, self.height - 50, 100, 40)

        # Mouse
        self.mouse_click = False
        self.mouse_pos = (0, 0)

        # Surface do gráfico
        self.plot_surface = None
        self.last_selected_terms = []

        # Pré-gerar ruído fixo para o modelo
        t = np.linspace(0, 10, 100)
        self.noise_seed = np.random.randn(len(t))  # ruído fixo

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
            for button in self.buttons:
                if button["rect"].collidepoint(self.mouse_pos):
                    term = button["term"]
                    if term in self.selected_terms:
                        # desseleciona
                        self.selected_terms.remove(term)
                        self.error = min(20.0, self.error +
                                         term["delta_error"])
                        self.complexity -= term["complexity"]
                    else:
                        # seleciona
                        self.selected_terms.append(term)
                        self.error = max(0.0, self.error - term["delta_error"])
                        self.complexity += term["complexity"]

                    self.aic = self.error + self.complexity

            # Botão OK
            if self.ok_button.collidepoint(self.mouse_pos):
                if abs(self.aic - self.min_aic_target) < 0.01:
                    self.finished = True
                    self.success = True
                else:
                    self.finished = True
                    self.failed = True

            self.mouse_click = False

    # --- Gera gráfico simples de ajuste ---
    def generate_plot_surface(self):
        fig, ax = plt.subplots(figsize=(6, 3), constrained_layout=True)
        t = np.linspace(0, 10, 100)
        y_real = np.sin(t)
        # Ruído escalado pelo erro atual, mas com valores fixos
        noise_level = max(0.1, self.error / 20)
        y_model = np.sin(t) + self.noise_seed * noise_level  # usa ruído fixo
        ax.plot(t, y_real, color='blue', label="Sistema real")
        ax.plot(t, y_model, color='red', linestyle='--', label="Modelo")
        ax.set_ylim(-3.5, 3.5)

        ax.set_xlim(0, 10)

        ax.set_title(f"Ajuste do modelo - AIC: {self.aic:.2f}")
        ax.set_xlabel("Tempo")
        ax.set_ylabel("Saída")
        ax.grid(True)
        ax.legend(fontsize=8, loc='lower right', frameon=True)

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

        if self.plot_surface is None or self.selected_terms != self.last_selected_terms:
            self.plot_surface = self.generate_plot_surface()
            self.last_selected_terms = list(self.selected_terms)
            self.size_adjusted = (self.plot_surface.width * 0.9, self.plot_surface.height * 0.9)

        # Desenha gráfico no centro
        self.plot_surface = pg.transform.smoothscale(self.plot_surface, self.size_adjusted)
        plot_rect = self.plot_surface.get_rect(
            center=(self.width // 2, self.height // 2 - 50))
        surface.blit(self.plot_surface, plot_rect)

        # Botões de termos centralizados
        for button in self.buttons:
            term = button["term"]
            rect = button["rect"]
            color = (0, 200, 0) if term in self.selected_terms else (
                200, 200, 200)
            pg.draw.rect(surface, color, rect)
            label = self.font.render(term["name"], True, (0, 0, 0))
            label_pos = (rect.x + rect.width // 2 - label.get_width() // 2,
                         rect.y + rect.height // 2 - label.get_height() // 2)
            surface.blit(label, label_pos)

        # Botão OK
        pg.draw.rect(surface, (0, 150, 0), self.ok_button)
        ok_label = self.font.render("OK", True, (255, 255, 255))
        surface.blit(ok_label, (self.ok_button.x + 35, self.ok_button.y + 10))
