import pygame as pg
from ..core.state_machine import State
from ..core import configs

_circle_cache = {}


def _circlepoints(r):
    r = int(round(r))
    if r in _circle_cache:
        return _circle_cache[r]
    x, y, e = r, 0, 1 - r
    _circle_cache[r] = points = []
    while x >= y:
        points.append((x, y))
        y += 1
        if e < 0:
            e += 2 * y - 1
        else:
            x -= 1
            e += 2 * (y - x) - 1
    points += [(y, x) for x, y in points if x > y]
    points += [(-x, y) for x, y in points if x]
    points += [(x, -y) for x, y in points if y]
    points.sort()
    return points


def render_out(text, text_surf, text_font, out_color=(0, 0, 0, 0), opx=2):
    w = text_surf.get_width() + 2 * opx
    h = text_font.get_height()

    osurf = pg.Surface((w, h + 2 * opx)).convert_alpha()
    osurf.fill((0, 0, 0, 0))
    surf = osurf.copy()
    osurf.blit(text_font.render(text, True, out_color).convert_alpha()), (0, 0)

    for dx, dy in _circlepoints(opx):
        surf.blit(osurf, (dx + opx, dy + opx))
    surf.blit(text_surf, (opx, opx))

    return surf


class MenuManager:

    def __init__(self):
        self.done = None
        self.quit = None
        self.rendered = None
        self.selected_index = 0
        self.last_option = None
        self.selected_color = (246, 175, 58)
        self.deselected_color = (255, 255, 255)
        self.next = "NEW_PLAYER"
        self.options = ["Jogar", "Sair"]
        self.next_list = ["NEW_PLAYER", "QUIT"]
        self.pre_render_options()
        self.from_bottom = 200
        self.spacer = 75

    def draw_menu(self, screen):
        """handle drawing of the menu options"""
        for i, opt in enumerate(self.rendered["des"]):
            opt[1].center = (
                configs.WINDOW_WIDTH / 2,
                self.from_bottom + i * self.spacer,
            )
            if i == self.selected_index:
                rend_img, rend_rect = self.rendered["sel"][i]
                rend_rect.center = opt[1].center
                screen.blit(rend_img, rend_rect)
            else:
                screen.blit(opt[0], opt[1])

    def update_menu(self):
        self.change_selected_option()

    def get_event_menu(self, event: pg.event):
        if event.type == pg.KEYDOWN:
            """select new index"""
            if event.key in [pg.K_UP, pg.K_w]:
                self.change_selected_option(-1)
            elif event.key in [pg.K_DOWN, pg.K_s]:
                self.change_selected_option(1)

            elif event.key == pg.K_RETURN:
                self.select_option(self.selected_index)
        self.mouse_menu_click(event)

    def mouse_menu_click(self, event: pg.event):
        """select menu option"""
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            for i, opt in enumerate(self.rendered["des"]):
                if opt[1].collidepoint(pg.mouse.get_pos()):
                    self.selected_index = i
                    self.select_option(i)
                    break

    def pre_render_options(self):
        """setup render menu options based on selected or deselected"""

        font_deselect = pg.font.Font(
            f"resources/fonts/{configs.FONTS_DICT[1][0]}.TTF", 50)
        font_selected = pg.font.Font(
            f"resources/fonts/{configs.FONTS_DICT[1][0]}.TTF", 70)

        rendered_msg = {"des": [], "sel": []}
        for option in self.options:
            d_rend = font_deselect.render(option, 1, self.deselected_color)
            d_rend = render_out(option, d_rend, font_deselect, (154, 90, 25))
            d_rect = d_rend.get_rect()

            s_rend = font_selected.render(option, 1, self.selected_color)
            s_rend = render_out(option, s_rend, font_selected, (157, 72, 26))
            s_rect = s_rend.get_rect()

            rendered_msg["des"].append((d_rend, d_rect))
            rendered_msg["sel"].append((s_rend, s_rect))

        self.rendered = rendered_msg

    def select_option(self, i):
        """Select menu option via keys or mouse"""
        if i == len(self.next_list):
            self.quit = True
        else:
            self.next = self.next_list[i]
            self.done = True
            self.selected_index = 0

    def change_selected_option(self, op=0):
        """change highlighted menu option"""
        for i, opt in enumerate(self.rendered["des"]):
            if opt[1].collidepoint(pg.mouse.get_pos()):
                self.selected_index = i
        if op:
            self.selected_index += op
            max_ind = len(self.rendered["des"]) - 1
            if self.selected_index < 0:
                self.selected_index = max_ind
            elif self.selected_index > max_ind:
                self.selected_index = 0


class Menu(State, MenuManager):

    def __init__(self):
        State.__init__(self)
        MenuManager.__init__(self)
        self.next = "NEW_PLAYER"
        self.previous = None
        self.options = ["Jogar", "Sair"]
        self.next_list = ["NEW_PLAYER", "QUIT"]
        self.pre_render_options()
        self.from_bottom = 200
        self.spacer = 75
        self.image = configs.GFX["others"]["menu"].copy().convert()
        self.image = pg.transform.smoothscale(self.image, (configs.WINDOW_WIDTH, configs.WINDOW_HEIGHT))

        self.rect = self.image.get_rect(center=configs.SCREEN_RECT.center)

    def cleanup(self):
        self.done = False  # importante, para não persistir
        pg.mixer.music.stop()
        return super().cleanup()

    def startup(self, now, persistant):
        super().startup(now, persistant)

        if self.previous in ["GAME_OVER", "CREDITS"]:
            pg.mixer.music.load("resources/sound/sound_1.mp3")
            pg.mixer.music.set_volume(0.3)
            pg.mixer.music.play(-1)

    def get_event(self, event):
        if event.type == pg.QUIT:
            self.quit = True
        self.get_event_menu(event)

    def update(self, keys, now):
        self.update_menu()

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        self.draw_menu(surface)
