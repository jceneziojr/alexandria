import pygame as pg
import numpy as np
from .minigame_manager import MiniGame
from ..core.configs import GFX


class NoisySignalQuizMiniGame(MiniGame):
    def __init__(self, size, **kwargs):
        super().__init__(size, **kwargs)
        self.minigame_name = "graph_quizz"
        self.font = pg.font.SysFont(None, 24)
        self.big_font = pg.font.SysFont(None, 32)

        # pega a imagem do gráfico que vai aparecer no jogo
        self.graph_image = GFX["minigame_assets"]["temp_planta"]

        # valor real da temperatura (a resposta certa)
        self.true_temperature = 35

        # ajusta o tamanho da imagem pra caber certinho na tela
        img_width = self.width - 80
        img_height = int(img_width * 3 / 4) - 150
        self.graph_image = pg.transform.smoothscale(
            self.graph_image, (img_width, img_height))

        # define as opções do quiz e inicializa os botões
        self.options = self.generate_options()
        self.buttons = []
        self.selected = None
        self.feedback_timer = 0
        self.failed = False

        # define onde e como os botões vão aparecer
        padding = 20
        button_width = self.width // 2 - 1.5 * padding
        button_height = 50
        start_y = self.height - (button_height * 2 + padding * 2)

        # cria os botões (dois por linha)
        for i, option in enumerate(self.options):
            row = i // 2
            col = i % 2
            x = padding + col * (button_width + padding)
            y = start_y + row * (button_height + padding)
            rect = pg.Rect(x, y, button_width, button_height)
            self.buttons.append({"rect": rect, "option": option})

    def generate_options(self):
        # opções que podem aparecer pro jogador escolher
        fixed_choices = np.array([30.0, 35.0, 40.0, 45.0])
        correct = round(self.true_temperature)

        # monta a lista com as opções, marcando a correta
        options = []
        for val in fixed_choices:
            options.append({
                "text": f"{val:.0f}",
                "correct": (val == correct)
            })

        return options

    def handle_event(self, event, keys):
        super().handle_event(event, keys)

        # vê se o jogador clicou em alguma opção
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
        # espera um pouco antes de passar pra próxima tela
        if self.feedback_timer > 0:
            self.feedback_timer -= dt * 1000
            if self.feedback_timer <= 0:
                self.finished = True

    def draw(self, surface):
        minigame_surface = pg.transform.smoothscale(
            GFX["others"]["minigame_bg"],
            (surface.width, surface.height)
        ).convert_alpha()
        surface.blit(minigame_surface)

        # título lá em cima
        title = self.big_font.render("Leitura do sensor", True, (0, 0, 0))
        surface.blit(title, (10, 10))

        # desenha o gráfico na tela
        graph_pos = (40, 50)
        surface.blit(self.graph_image, graph_pos)
        graph_area = pg.Rect(graph_pos, self.graph_image.get_size())
        pg.draw.rect(surface, (200, 200, 200), graph_area, 2)

        # pergunta que aparece embaixo do gráfico
        question_text = self.big_font.render(
            "", True, (0, 0, 0))
        surface.blit(question_text, (40, graph_area.bottom + 10))

        # desenha os botões com as respostas
        for button in self.buttons:
            rect = button["rect"]
            text = button["option"]["text"]

            if self.selected is None:
                color = (100, 100, 160)
            elif button == self.selected:
                color = (0, 180, 0) if button["option"]["correct"] else (
                    180, 0, 0)
            else:
                color = (80, 80, 120)

            pg.draw.rect(surface, color, rect, border_radius=8)
            pg.draw.rect(surface, (220, 220, 220), rect, 2, border_radius=8)

            text_surf = self.font.render(text + " °C", True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=rect.center)
            surface.blit(text_surf, text_rect)
