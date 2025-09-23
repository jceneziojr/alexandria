import pygame as pg
from .minigame_manager import MiniGame
from ..core.configs import GFX, TEXT_FONT_2


class Animation(MiniGame):
    def __init__(self, size, **kwargs):
        super().__init__(size)

        # --- Frames da animação (agora 14 frames) ---
        self.frames = [
            GFX["animation"][f"frame_{i}"] for i in range(1, 35)
        ]
        self.current_frame = 0
        self.frame_time = 0.15  # tempo entre frames (s)
        self.frame_timer = 0

        # --- Delay inicial no frame 1 ---
        self.initial_delay = 1.0
        self.delay_timer = 0
        self.delay_done = False

        # --- Controle de pausa no frame 4 ---
        self.pause_on_frame_4 = True
        self.pause_timer = 0
        self.pause_duration = 10.0  # fica 10s no frame 4
        self.text_visible = True  # controla se o texto deve ser mostrado

        # --- Textos ---
        self.main_text = "Modelagem e\nIdentificação de\nSistemas"
        self.player_name = kwargs.get("name", "")
        self.full_text = self.player_name + "\n" + self.main_text

        self.displayed_text = ""
        self.char_index = 0
        self.text_speed = 0.05  # tempo entre caracteres (s)
        self.text_timer = 0

        self.font = TEXT_FONT_2
        self.minigame_name = "Animation"

    def update(self, dt):
        # --- Primeiro, aguarda o delay do frame inicial ---
        if not self.delay_done:
            self.delay_timer += dt
            if self.delay_timer >= self.initial_delay:
                self.delay_done = True
            return  # sai aqui, não atualiza nada enquanto delay não acaba

        # --- Verifica se estamos no frame 4 e devemos pausar ---
        if self.pause_on_frame_4 and self.current_frame == 3:
            self.pause_timer += dt

            # Atualiza digitação do texto durante a pausa
            if self.char_index < len(self.full_text):
                self.text_timer += dt
                if self.text_timer >= self.text_speed:
                    self.text_timer -= self.text_speed
                    self.char_index += 1
                    self.displayed_text = self.full_text[:self.char_index]

            if self.pause_timer >= self.pause_duration:
                # Pausa acabou, libera para continuar animação e esconde o texto
                self.pause_on_frame_4 = False
                self.text_visible = False
                self.pause_timer = 0
            else:
                return  # fica travado no frame 4

        # --- Avança animação normalmente ---
        self.frame_timer += dt
        if self.frame_timer >= self.frame_time:
            self.frame_timer -= self.frame_time
            self.current_frame += 1

            if self.current_frame >= len(self.frames):
                self.finished = True
                self.current_frame = len(self.frames) - 1

    def draw(self, surface):
        # Fundo
        minigame_surface = pg.transform.smoothscale(
            GFX["others"]["minigame_bg"],
            (surface.width, surface.height)
        ).convert_alpha()
        surface.blit(minigame_surface)

        # --- Desenha frame da animação ---
        frame_img = self.frames[self.current_frame]
        width, height = frame_img.get_size()
        factor = 1.7
        frame_rect = frame_img.get_rect(center=(self.width // 2 - 120, self.height // 2 - 130))
        frame_img = pg.transform.smoothscale(frame_img, (int(width * factor), int(height * factor)))
        surface.blit(frame_img, frame_rect)

        # --- Desenha texto apenas durante pausa no frame 4 ---
        if self.text_visible and self.displayed_text:
            lines = self.displayed_text.split("\n")
            y_offset = self.height - 300
            for line in lines:
                text_surface = self.font.render(line, True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=(self.width // 2 + 120, y_offset))
                surface.blit(text_surface, text_rect)
                y_offset += text_surface.get_height() + 5
