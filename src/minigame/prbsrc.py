import pygame as pg
import numpy as np
from scipy import signal
from random import randint
from .minigame_manager import MiniGame
from ..core.configs import WINDOW_WIDTH, WINDOW_HEIGHT, GFX
import matplotlib.pyplot as plt
import io


class PRBSRCMiniGame(MiniGame):
    def __init__(self, size):
        super().__init__(size)
        # --- Configurações iniciais ---
        self.prbs_bits = 7
        self.rng_seed = 10001
        self.tau = 0.5  # constante RC
        self.Tbit = 0.5  # tempo entre bits (segundos)
        self.Tbit_step = self.tau / 20  # incremento/decremento
        self.oversampling = 50

        # --- Fonte ---
        self.font = pg.font.Font(None, 24)
        self.large_font = pg.font.Font(None, 28)

        # --- Botões ---
        button_widths = [50, 50, 60]
        spacing = 20
        total_width = sum(button_widths) + spacing * 2
        start_x = (self.width - total_width) // 2
        button_y = self.height - 40
        self.buttons = [
            ("+T", pg.Rect(start_x, button_y, 50, 30), "Tbit", 1),
            ("-T", pg.Rect(start_x + 50 + spacing, button_y, 50, 30), "Tbit", -1),
            ("OK", pg.Rect(start_x + 50 + spacing + 50 + spacing, button_y, 60, 30), "finish", None),
        ]

        self.mouse_click = False
        self.mouse_pos = (0, 0)

        # Surface do gráfico
        self.plot_surface = None
        self.last_Tbit = None

    # --- Função PRBS ---
    def prbs_sequence(self, prbs_bits: int, rng_seed: int) -> list[int]:
        prbs_types = {
            3: {'bit_1': 2, 'bit_2': 1},
            4: {'bit_1': 3, 'bit_2': 2},
            5: {'bit_1': 4, 'bit_2': 2},
            6: {'bit_1': 5, 'bit_2': 4},
            7: {'bit_1': 6, 'bit_2': 5},
        }
        prbs_bits = min(b for b in prbs_types.keys() if b >= prbs_bits)
        size = (2 ** prbs_bits) - 1
        bit_1 = prbs_types[prbs_bits]['bit_1']
        bit_2 = prbs_types[prbs_bits]['bit_2']
        start_value = randint(0, size - 1) if rng_seed is None else rng_seed
        start_value = int(min(max(start_value, 0), size - 1))

        bit_sequence = [start_value & 0x1]
        new_value = start_value
        for _ in range(size - 1):
            new_bit = ~((new_value >> bit_1) ^ (new_value >> bit_2)) & 0x1
            new_value = ((new_value << 1) + new_bit) & size
            if new_value == start_value or new_value == size:
                return bit_sequence
            bit_sequence.append(int(new_bit))
        return bit_sequence

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
            for text, rect, param, change in self.buttons:
                if rect.collidepoint(self.mouse_pos):
                    if param == "Tbit":
                        self.Tbit = min(2.0, max(self.Tbit_step, self.Tbit + change * self.Tbit_step))
                    elif param == "finish":
                        self.finished = True
            self.mouse_click = False

    # --- Gera gráfico Matplotlib e converte para Pygame Surface ---
    def generate_plot_surface(self):
        prbs = self.prbs_sequence(self.prbs_bits, self.rng_seed)
        t = np.linspace(0, (len(prbs) - 1) * self.Tbit, len(prbs) * self.oversampling)
        u = np.repeat(prbs, self.oversampling).astype(float)

        num = [1]
        den = [self.tau, 1]
        system = signal.TransferFunction(num, den)
        t_out, y_out, _ = signal.lsim(system, U=u, T=t)

        fig, axes = plt.subplots(2, 1, figsize=(6, 4), constrained_layout=True)
        axes[0].step(t, u, where="post", color='red')
        axes[0].set_title(f"Entrada PRBS (Tbit={self.Tbit:.2f}s)")
        axes[0].set_ylabel("u")
        axes[0].grid(True)

        axes[1].plot(t_out, y_out, color='blue')
        axes[1].set_title(f"Saída RC (τ={self.tau:.2f}s)")
        axes[1].set_xlabel("Tempo [s]")
        axes[1].set_ylabel("y")
        axes[1].grid(True)

        buf = io.BytesIO()
        # substitui print_rgb por print_rgba
        fig.canvas.print_rgba(buf)
        buf.seek(0)
        w, h = fig.canvas.get_width_height()
        img = np.frombuffer(buf.getvalue(), dtype=np.uint8).reshape(h, w, 4)  # 4 canais RGBA
        buf.close()
        plt.close(fig)

        # Converte RGBA para RGB (descarta alpha)
        img_rgb = img[:, :, :3]

        return pg.surfarray.make_surface(np.transpose(img_rgb, (1, 0, 2)))

    # --- Desenho ---
    def draw(self, surface):
        # surface.fill((255, 255, 255))
        minigame_surface = pg.transform.smoothscale(
            GFX["others"]["minigame_bg"],
            (surface.width, surface.height)
        ).convert_alpha()
        surface.blit(minigame_surface)

        # Mostra Tbit
        # Posição acima dos botões
        text_y = self.buttons[0][1].top - 30
        label = self.large_font.render(f"Tempo entre bits: {self.Tbit:.2f} s", True, (0, 0, 0))
        surface.blit(label, (self.width // 2 - label.get_width() // 2, text_y))

        # Gera Surface do gráfico se Tbit mudou
        if self.plot_surface is None or self.Tbit != self.last_Tbit:
            self.plot_surface = self.generate_plot_surface()
            self.last_Tbit = self.Tbit
            self.size_adjusted = (self.plot_surface.width * 0.9, self.plot_surface.height * 0.9)

        # Desenha gráfico no centro
        self.plot_surface = pg.transform.smoothscale(self.plot_surface, self.size_adjusted)
        plot_rect = self.plot_surface.get_rect(center=(self.width // 2, self.height // 2 - 30))
        surface.blit(self.plot_surface, plot_rect)

        # Desenha botões
        for text, rect, _, _ in self.buttons:
            pg.draw.rect(surface, (0, 200, 0), rect)
            label = self.font.render(text, True, (0, 0, 0))
            surface.blit(label, (rect.x + 12, rect.y + 7))
