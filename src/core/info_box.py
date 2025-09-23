import pygame as pg

from .configs import GFX, INFO_BOX_FONT, WINDOW_WIDTH


class InfoBox:
    def __init__(self):
        self.text_start_pos = None
        self.text_x_Pos = None
        self.text_y_Pos = None
        self.screen = pg.display.get_surface()

        self.text_index = 1
        self.box_active = False

        self.font = None
        self.font_color = None

        self.lines = []
        self.current_line = ""
        self.initialize_fonts()
        self.initialize_text_box()
        self.initialize_text_positions()
        self.current_message = ""

    def initialize_fonts(self):
        self.font = INFO_BOX_FONT
        self.font_color = (0, 0, 100)

    def initialize_text_positions(self):
        self.text_start_pos = [200, 500]

        self.x_start_text = self.box_pos[0] + 10
        self.text_x_Pos = self.x_start_text
        self.x_distance_between = 21
        self.maximum_x_text_x_bounds = 190

        self.y_start_text = self.box_pos[1] + 15
        self.text_y_Pos = self.y_start_text
        self.text_y_offset = 15 + 0

    def initialize_text_box(self):
        info_box_size = (200, 75)
        self.info_box_sprite = pg.transform.smoothscale(GFX["ui"]["InfoBox"], info_box_size).copy().convert_alpha()
        self.box_pos = (WINDOW_WIDTH - 225, 25)

    def render_info_box(self, surface):
        if self.box_active:
            surface.blit(self.info_box_sprite, self.box_pos)

            lines = self.handle_text_lines(self.current_message, self.maximum_x_text_x_bounds)

            for i, line in enumerate(lines):
                text_surface = self.font.render(line, True, self.font_color)
                line_y = self.text_y_Pos + i * self.text_y_offset
                surface.blit(text_surface, (self.text_x_Pos, line_y))

    def handle_text_lines(self, text, max_width):
        words = text.split()
        wrapped_lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            text_width, _ = self.font.size(test_line)
            if text_width <= max_width:
                current_line = test_line
            else:
                wrapped_lines.append(current_line.strip())
                current_line = word + " "

        if current_line:
            wrapped_lines.append(current_line.strip())

        return wrapped_lines
