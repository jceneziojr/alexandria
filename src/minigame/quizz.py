import pygame as pg
from .minigame_manager import MiniGame
from ..core.configs import GFX


class QuizMiniGame(MiniGame):
    def __init__(self, size, **kwargs):
        super().__init__(size, **kwargs)

        self.font = pg.font.SysFont(None, 28)
        self.big_font = pg.font.SysFont(None, 36)

        self.question = kwargs.get("question")
        self.options = kwargs.get("options")

        # grid 2x2
        self.buttons = []
        padding = 20
        button_width = self.width // 2 - 1.5 * padding
        button_height = 90
        start_y = self.height // 2 - button_height - padding // 2

        for i, option in enumerate(self.options):
            row = i // 2
            col = i % 2
            x = padding + col * (button_width + padding)
            y = start_y + row * (button_height + padding)
            rect = pg.Rect(x, y, button_width, button_height)
            self.buttons.append({"rect": rect, "option": option})

        self.selected = None
        self.feedback_timer = 0
        self.failed = False

    def handle_event(self, event, keys):
        super().handle_event(event, keys)

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pg.mouse.get_pos()
            rel_x = mx - \
                    (pg.display.get_surface().get_width() - self.width) // 2
            rel_y = my - \
                    (pg.display.get_surface().get_height() - self.height) // 2

            for button in self.buttons:
                if button["rect"].collidepoint((rel_x, rel_y)) and self.selected is None:
                    self.selected = button
                    if button["option"]["correct"]:
                        self.feedback_timer = 1000
                    else:
                        self.failed = True
                        self.feedback_timer = 1000  # espera 1 segundo antes de fechar

    def update(self, dt):
        if self.feedback_timer > 0:
            self.feedback_timer -= dt * 1000
            if self.feedback_timer <= 0:
                self.feedback_timer = 0
                if self.failed:
                    self.finished = True  # só termina agora, depois do tempo
                else:
                    self.finished = True

    def draw(self, surface):
        minigame_surface = pg.transform.smoothscale(
            GFX["others"]["minigame_bg"],
            (surface.width, surface.height)
        ).convert_alpha()
        surface.blit(minigame_surface)

        lines = self.question.split('\n')
        for i, line in enumerate(lines):
            text_surf = self.big_font.render(line, True, (255, 255, 255))
            if i != 0:
                text_rect = text_surf.get_rect(
                    center=(self.width // 2, 25 + i * 30))
            else:
                text_rect = text_surf.get_rect(
                    center=(self.width // 2, 25 + i * 40))
            surface.blit(text_surf, text_rect)

        # botões de opção
        for button in self.buttons:
            rect = button["rect"]
            text = button["option"]["text"]

            # cores
            if self.selected is None:
                color = (70, 70, 100)
            elif button == self.selected:
                color = (0, 180, 0) if button["option"]["correct"] else (
                    180, 0, 0)
            else:
                color = (50, 50, 70)

            pg.draw.rect(surface, color, rect, border_radius=8)
            pg.draw.rect(surface, (200, 200, 200), rect, 2, border_radius=8)

            lines = text.split('\n')
            for i, line in enumerate(lines):
                text_surf = self.font.render(line, True, (255, 255, 255))
                text_rect = text_surf.get_rect(
                    center=(rect.centerx, rect.centery - (len(lines) - 1) * 10 + i * 20))
                surface.blit(text_surf, text_rect)


class GraphQuizMiniGame(MiniGame):
    def __init__(self, size, **kwargs):
        super().__init__(size, **kwargs)

        self.font = pg.font.SysFont(None, 28)
        self.big_font = pg.font.SysFont(None, 36)

        self.minigame_name = "graph_quizz"

        # dados recebidos
        self.question = kwargs.get("question", "")
        self.options = kwargs.get("options", [])
        self.image = kwargs.get("image", None)
        self.scale = kwargs.get("scale", True)  # novo argumento

        # redimensiona imagem de acordo com scale
        if self.image is not None:
            img_w, img_h = self.image.get_size()

            if self.scale is True:
                max_width = self.width - 80
                max_height = self.height // 3
                factor = min(max_width / img_w, max_height / img_h)
                new_size = (int(img_w * factor), int(img_h * factor))
                self.image = pg.transform.smoothscale(self.image, new_size)

            elif isinstance(self.scale, (int, float)):
                new_size = (int(img_w * self.scale), int(img_h * self.scale))
                self.image = pg.transform.smoothscale(self.image, new_size)

            # se for False → mantém tamanho original

        # grid 2x2 para opções
        self.buttons = []
        padding = 10
        button_width = self.width // 2 - 1.5 * padding
        button_height = 60
        start_y = self.height // 2 - button_height - padding // 2 + 165

        for i, option in enumerate(self.options):
            row = i // 2
            col = i % 2
            x = padding + col * (button_width + padding)
            y = start_y + row * (button_height + padding)
            rect = pg.Rect(x, y, button_width, button_height)
            self.buttons.append({"rect": rect, "option": option})

        self.selected = None
        self.feedback_timer = 0
        self.failed = False

        self.protect = kwargs.get("protect", False)

    def handle_event(self, event, keys):
        super().handle_event(event, keys)

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pg.mouse.get_pos()
            rel_x = mx - \
                    (pg.display.get_surface().get_width() - self.width) // 2
            rel_y = my - \
                    (pg.display.get_surface().get_height() - self.height) // 2

            for button in self.buttons:
                if button["rect"].collidepoint((rel_x, rel_y)) and self.selected is None:
                    self.selected = button
                    if button["option"]["correct"]:
                        self.feedback_timer = 1000
                    else:
                        self.failed = True
                        self.feedback_timer = 1000

    def update(self, dt):
        if self.feedback_timer > 0:
            self.feedback_timer -= dt * 1000
            if self.feedback_timer <= 0:
                self.feedback_timer = 0
                self.finished = True

    def draw(self, surface):
        minigame_surface = pg.transform.smoothscale(
            GFX["others"]["minigame_bg"],
            (surface.width, surface.height)
        ).convert_alpha()
        surface.blit(minigame_surface)

        y_offset = 20

        # desenha a imagem
        if self.image is not None:
            img_rect = self.image.get_rect(
                center=(self.width // 2, y_offset + self.image.get_height() // 2))
            surface.blit(self.image, img_rect)
            y_offset = img_rect.bottom + 20

        # pergunta
        lines = self.question.split("\n")
        for i, line in enumerate(lines):
            text_surf = self.big_font.render(line, True, (255, 255, 255))
            if i != 0:
                text_rect = text_surf.get_rect(
                    center=(self.width // 2, y_offset + i * 40 - 10))
            else:
                text_rect = text_surf.get_rect(
                    center=(self.width // 2, y_offset + i * 40 + 0))  # o valor somando ajusta a altura
            surface.blit(text_surf, text_rect)
        y_offset += len(lines) * 40 + 20

        # opções
        for button in self.buttons:
            rect = button["rect"]
            text = button["option"]["text"]

            if self.selected is None:
                color = (70, 70, 100)
            elif button == self.selected:
                color = (0, 180, 0) if button["option"]["correct"] else (
                    180, 0, 0)
            else:
                color = (50, 50, 70)

            pg.draw.rect(surface, color, rect, border_radius=8)
            pg.draw.rect(surface, (200, 200, 200), rect, 2, border_radius=8)

            lines = text.split("\n")
            for i, line in enumerate(lines):
                text_surf = self.font.render(line, True, (255, 255, 255))
                text_rect = text_surf.get_rect(
                    center=(rect.centerx, rect.centery -
                            (len(lines) - 1) * 10 + i * 20)
                )
                surface.blit(text_surf, text_rect)
