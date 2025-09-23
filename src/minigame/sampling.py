import pygame as pg
import numpy as np
from .minigame_manager import MiniGame
from ..core.configs import WINDOW_WIDTH, WINDOW_HEIGHT, GFX
import matplotlib.pyplot as plt
import io


class SamplingEffectMiniGame(MiniGame):
    def __init__(self, size):
        super().__init__(size)
        self.base_amplitude = 75
        self.base_frequency = 2  # Hz
        self.phase = 0
        self.sampling_rate = 1  # Hz

        self.font = pg.font.Font(None, 24)
        self.large_font = pg.font.Font(None, 32)

        margin = 60
        top = 70
        bottom = self.height - 100
        plot_width = self.width - 2 * margin
        self.plot_rect = pg.Rect(margin, top, plot_width, bottom - top)

        self.max_time = 3  # tempo total
        self.scale_x = self.max_time / plot_width  # segundos por pixel

        button_widths = [50, 50, 60]
        spacing = 20
        total_width = sum(button_widths) + spacing * 2
        start_x = (self.width - total_width) // 2
        button_y = self.height - 40

        self.buttons = [
            ("+F", pg.Rect(start_x, button_y, 50, 30), "sr", 1),
            ("-F", pg.Rect(start_x + 50 + spacing, button_y, 50, 30), "sr", -1),
            ("OK", pg.Rect(start_x + 50 + spacing + 50 + spacing, button_y, 60, 30), "finish", None),
        ]

        self.mouse_click = False
        self.mouse_pos = (0, 0)

        # Surface do gráfico
        self.plot_surface = None
        self.last_sampling_rate = None

        self.feedback_timer = 0

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

    def update(self, dt):
        if self.feedback_timer > 0:
            self.feedback_timer -= dt * 1000
            if self.feedback_timer <= 0:
                self.feedback_timer = 0
                self.finished = True
            return

        if self.mouse_click:
            for text, rect, param, change in self.buttons:
                if rect.collidepoint(self.mouse_pos):
                    if param == "sr":
                        self.sampling_rate = max(1, self.sampling_rate + change)
                    elif param == "finish":
                        if self.sampling_rate >= 8:
                            self.finished = True
                        else:
                            self.failed = True
                            self.feedback_timer = 1000
            self.mouse_click = False

    def generate_plot_surface(self):
        # --- Cria sinal contínuo ---
        t = np.linspace(0, self.max_time, 500)
        y = self.base_amplitude * np.sin(2 * np.pi * self.base_frequency * t + self.phase)

        # --- Pontos de amostragem ---
        ts = 1.0 / self.sampling_rate
        t_samples = np.arange(0, self.max_time, ts)
        y_samples = self.base_amplitude * np.sin(2 * np.pi * self.base_frequency * t_samples + self.phase)

        # --- Matplotlib ---
        fig, ax = plt.subplots(figsize=(6, 3), constrained_layout=True)
        ax.plot(t, y, color='gray', label='Sinal contínuo')
        ax.scatter(t_samples, y_samples, color='red', s=40, label='Amostras')
        ax.set_xlabel('Tempo [s]')
        ax.set_ylabel('Amplitude')
        ax.set_xlim(0, self.max_time)
        ax.set_ylim(-100, 100)
        ax.grid(True)

        # Legenda menor e no canto inferior direito
        ax.legend(fontsize=10, loc='lower right')

        buf = io.BytesIO()
        fig.canvas.print_rgba(buf)
        buf.seek(0)
        w, h = fig.canvas.get_width_height()
        img = np.frombuffer(buf.getvalue(), dtype=np.uint8).reshape(h, w, 4)
        buf.close()
        plt.close(fig)

        img_rgb = img[:, :, :3]
        return pg.surfarray.make_surface(np.transpose(img_rgb, (1, 0, 2)))

    def draw(self, surface):
        minigame_surface = pg.transform.smoothscale(
            GFX["others"]["minigame_bg"],
            (surface.width, surface.height)
        ).convert_alpha()
        surface.blit(minigame_surface)

        # Atualiza gráfico se a taxa mudou
        if self.plot_surface is None or self.sampling_rate != self.last_sampling_rate:
            self.plot_surface = self.generate_plot_surface()
            self.last_sampling_rate = self.sampling_rate
            self.size_adjusted = (self.plot_surface.width * 0.9, self.plot_surface.height * 0.9)

            # Desenha gráfico
        self.plot_surface = pg.transform.smoothscale(self.plot_surface, self.size_adjusted)
        plot_rect = self.plot_surface.get_rect(center=(self.width // 2, self.height // 2 - 20))

        surface.blit(self.plot_surface, plot_rect)

        # Texto acima dos botões
        freq_label = self.large_font.render(
            f"Amostras por segundo: {self.sampling_rate} Hz", True, (0, 0, 0)
        )
        label_rect = freq_label.get_rect(center=(self.width // 2, self.height - 70))
        surface.blit(freq_label, label_rect)

        # Botões
        for text, rect, _, _ in self.buttons:
            pg.draw.rect(surface, (0, 200, 0), rect)
            label = self.font.render(text, True, (0, 0, 0))
            surface.blit(label, (rect.x + 12, rect.y + 7))
