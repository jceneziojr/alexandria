import pygame as pg
from .minigame_manager import MiniGame
from ..core.configs import WINDOW_WIDTH, WINDOW_HEIGHT, GFX


class IndustrialTankMiniGame(MiniGame):
    def __init__(self, size):
        super().__init__(size)
        self.font = pg.font.Font(None, 24)
        self.big_font = pg.font.Font(None, 36)

        self.temperature = 35  # temperatura inicial (°C)
        self.volume = 40.0  # volume inicial (%)
        self.exploded = False
        self.passou_80 = False  # trava quando passa de 80°C

        self.button_up = pg.Rect(40, self.height // 2 - 50, 200, 40)
        self.button_down = pg.Rect(40, self.height // 2 + 10, 200, 40)
        self.mouse_click = False
        self.mouse_pos = (0, 0)

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
        if self.exploded:
            # espera 2 segundos após explosão para finalizar o minigame
            if pg.time.get_ticks() - self.explosion_time >= 2000:
                self.finished = True
            return

        # registra se já passou de 80°C alguma vez
        if self.temperature > 80:
            self.passou_80 = True

        # lógica do volume
        if self.temperature >= 80 or self.passou_80:
            self.volume += 5 * dt
        elif self.temperature >= 60:
            self.volume += 2 * dt

        # explosão
        if self.volume > 100 and not self.exploded:
            self.exploded = True
            self.sound_controller.sounds["explosion"][1].play()
            self.sound_controller.sounds["explosion"][1].set_volume(0.5)
            self.explosion_time = pg.time.get_ticks()

        # controle de temperatura
        if self.mouse_click:
            if self.button_up.collidepoint(self.mouse_pos):
                self.temperature += 5
            elif self.button_down.collidepoint(self.mouse_pos):
                self.temperature = max(0, self.temperature - 5)
            self.mouse_click = False

    def draw(self, surface):
        minigame_surface = pg.transform.smoothscale(
            GFX["others"]["minigame_bg"],
            (surface.width, surface.height)
        ).convert_alpha()
        surface.blit(minigame_surface)

        # retângulo envolvendo os botões
        rect_x = 20
        rect_y = self.height // 2 - 90
        rect_w = 240
        rect_h = 150
        pg.draw.rect(surface, (180, 180, 180), (rect_x, rect_y, rect_w, rect_h), border_radius=8)
        pg.draw.rect(surface, (0, 0, 0), (rect_x, rect_y, rect_w, rect_h), 2, border_radius=8)

        # título dentro do retângulo
        title_text = self.font.render("Controle de Temperatura", True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(rect_x + rect_w // 2, rect_y + 20))
        surface.blit(title_text, title_rect)

        # botões dentro do retângulo
        pg.draw.rect(surface, (0, 128, 255), self.button_up)
        label_up = self.font.render("Aumenta Temperatura", True, (255, 255, 255))
        surface.blit(label_up, (self.button_up.x + 15, self.button_up.y + 10))

        pg.draw.rect(surface, (0, 128, 255), self.button_down)
        label_down = self.font.render("Diminui Temperatura", True, (255, 255, 255))
        surface.blit(label_down, (self.button_down.x + 15, self.button_down.y + 10))

        # texto temperatura
        temp_text = self.big_font.render(f"Temperatura do tanque: {self.temperature}°C", True, (0, 0, 0))
        temp_rect = temp_text.get_rect(center=(self.width // 2, 40))  # 40 px do topo
        surface.blit(temp_text, temp_rect)

        # tanque
        tank_width = 100
        tank_height = 200
        tank_x = self.width - 160
        tank_y = self.height // 2 - tank_height // 2

        pg.draw.rect(surface, (0, 0, 0), (tank_x, tank_y, tank_width, tank_height), 3)

        volume_clamped = min(self.volume, 100.0)
        fill_height = int(volume_clamped / 100 * tank_height)
        fill_y = tank_y + tank_height - fill_height

        if self.exploded:
            color = (100, 100, 100)
        elif self.volume >= 80:
            color = (255, 0, 0)
        else:
            color = (0, 200, 0)

        pg.draw.rect(surface, color, (tank_x + 3, fill_y, tank_width - 6, fill_height))

        level_text = self.font.render(f"{int(self.volume)}%", True, (0, 0, 0))
        surface.blit(level_text, (tank_x + 20, tank_y + tank_height + 10))

        # avisos
        if self.exploded:
            warning = self.big_font.render("EXPLOSÃO!", True, (255, 0, 0))
            surface.blit(warning, (tank_x - 30, tank_y - 50))
        elif self.volume >= 80:
            warning = self.big_font.render("PERIGO!", True, (255, 0, 0))
            surface.blit(warning, (tank_x - 10, tank_y - 40))
