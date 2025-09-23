import pygame as pg
from ..core.state_machine import State
from ..core.configs import WINDOW_WIDTH, TEXT_FONT, WINDOW_HEIGHT


class NewPlayer(State):
    def __init__(self):
        super().__init__()
        self.next = "GAME"
        self.player_name = ""
        self.font = TEXT_FONT
        self.prompt_text = "Digite seu nome:"
        self.confirmando = False  # controle do pop-up
        self.botao_sim = None
        self.botao_nao = None

    def startup(self, now, persistant):
        super().startup(now, persistant)
        self.sound_controller = self.persist["sound_controller"]

    def get_event(self, event):
        if event.type == pg.QUIT:
            self.quit = True

        elif event.type == pg.KEYDOWN:
            if self.confirmando:
                if event.key in (pg.K_y, pg.K_RETURN, pg.K_KP_ENTER):
                    self.done = True
                    self.next = "GAME"
                elif event.key == pg.K_n:
                    self.confirmando = False
            else:
                if event.key in (pg.K_RETURN, pg.K_KP_ENTER):
                    self.confirmando = True
                elif event.key == pg.K_BACKSPACE:
                    self.player_name = self.player_name[:-1]
                else:
                    if len(self.player_name) < 20 and event.unicode.isprintable() and event.key != pg.K_CAPSLOCK:

                        self.player_name += event.unicode

                        if "write" in self.sound_controller.sounds:
                            self.sound_controller.sounds["write"][1].play()
                            self.sound_controller.sounds["write"][1].set_volume(0.3)

        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.confirmando:
                if self.botao_sim and self.botao_sim.collidepoint(event.pos):
                    self.done = True
                    self.next = "GAME"
                elif self.botao_nao and self.botao_nao.collidepoint(event.pos):
                    self.confirmando = False

    def update(self, keys, now):
        self.now = now

    def draw(self, surface):
        surface.fill((0, 0, 0))

        prompt_surface = self.font.render(self.prompt_text, True, (255, 255, 255))
        prompt_rect = prompt_surface.get_rect(center=(surface.get_width() // 2, 100))
        surface.blit(prompt_surface, prompt_rect)

        name_surface = self.font.render(self.player_name, True, (255, 255, 255))
        name_rect = name_surface.get_rect(center=(surface.get_width() // 2, 200))
        surface.blit(name_surface, name_rect)

        # --- TEXTO NO CANTO INFERIOR ESQUERDO ---
        confirm_hint = self.font.render("Pressione Enter para confirmar", True, (200, 200, 200))
        hint_rect = confirm_hint.get_rect(bottomright=(WINDOW_WIDTH - 10, WINDOW_HEIGHT - 10))
        surface.blit(confirm_hint, hint_rect)

        if self.confirmando:
            popup_width, popup_height = 400, 200
            popup_x = (surface.get_width() - popup_width) // 2
            popup_y = (surface.get_height() - popup_height) // 2

            shadow_rect = pg.Rect(popup_x + 5, popup_y + 5, popup_width, popup_height)
            pg.draw.rect(surface, (50, 50, 50), shadow_rect, border_radius=10)

            popup_rect = pg.Rect(popup_x, popup_y, popup_width, popup_height)
            pg.draw.rect(surface, (30, 30, 30), popup_rect, border_radius=10)
            pg.draw.rect(surface, (255, 255, 255), popup_rect, 2, border_radius=10)

            confirm_text = self.font.render("Confirmar nome?", True, (255, 255, 0))
            confirm_rect = confirm_text.get_rect(center=(surface.get_width() // 2, popup_y + 50))
            surface.blit(confirm_text, confirm_rect)

            # Botões
            button_w, button_h = 100, 40
            spacing = 40
            center_x = surface.get_width() // 2

            self.botao_sim = pg.Rect(center_x - button_w - spacing // 2, popup_y + 120, button_w, button_h)
            self.botao_nao = pg.Rect(center_x + spacing // 2, popup_y + 120, button_w, button_h)

            for rect, text, color in [
                (self.botao_sim, "Sim", (0, 200, 0)),
                (self.botao_nao, "Não", (200, 0, 0)),
            ]:
                pg.draw.rect(surface, color, rect, border_radius=8)
                pg.draw.rect(surface, (255, 255, 255), rect, 2, border_radius=8)
                txt_surf = self.font.render(text, True, (255, 255, 255))
                txt_rect = txt_surf.get_rect(center=rect.center)
                surface.blit(txt_surf, txt_rect)

    def cleanup(self):
        if self.player_name:
            self.persist["player_name"] = self.player_name
        else:
            self.persist["player_name"] = "Jogador"
        return super().cleanup()
