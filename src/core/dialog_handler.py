import pygame as pg
from .configs import WINDOW_WIDTH, WINDOW_HEIGHT, GFX, TEXT_FONT, FONTS_DICT, FONT_INDEX
from .dialogs import dialogues
from .content_display import ContentDisplayManager


class DialogSystem:
    def __init__(self, player):
        self.tick_time = None
        self.text_x_Pos = None
        self.text_y_Pos = None
        self.text_start_pos = None
        self.screen = pg.display.get_surface()
        self.counter = 0
        self.player = player

        self.height_adjust = 50

        self.player_name = self.player.player_name

        self.rendered_text = {}
        self.text_to_move = []

        self.speaker = None  # para lidar com qual fala colocar

        self.typing_speed = 2
        self.dialog_index = 1
        self.char_index = 0
        self.letter_spacing = 21
        self.phase = 1

        self.skip_key_pressed = False
        self.button_pressed_time = None

        self.line_cut = False
        self.dialog_active = False
        self.ticked = False
        self.line_finished = False
        self.skipped_dialog = False

        self.font = None
        self.font_color = None

        self.lines = []
        self.current_line = ""
        self.initialize_fonts()
        self.initialize_text_positions()
        self.initialize_text_box()

        self.speaker_name_text_pos = (70, 565 + self.height_adjust)
        self.sound_controller = None

        self.sound_count = 0

        self.content_display_manager = ContentDisplayManager(self.player)

    def update(self):
        current_time = pg.time.get_ticks()

        if self.skip_key_pressed:
            if current_time - self.button_pressed_time > 50:
                self.skip_key_pressed = False

        if self.ticked:
            if current_time - self.tick_time > self.typing_speed:
                self.ticked = False

        if self.content_display_manager:
            self.content_display_manager.update(60 / 1000)

        self.handle_rendering()

    def handle_rendering(self):
        if self.speaker is None or self.phase not in dialogues.get(self.speaker, {}):
            return

        if self.dialog_index <= len(dialogues[self.speaker][self.phase]):
            self.render_dialog_box()
            self.add_to_rendered_text(dialogues[self.speaker][self.phase][self.dialog_index][1])
        else:
            self.end_dialog()

    def add_to_rendered_text(self, txt):
        txt = txt.format(CTE_PLAYER_NAME=self.player_name)
        if self.counter < len(txt) * self.typing_speed:  # multiplico pela velocidade pra ajustar os indices abaixo
            self.counter += 1
        if self.skipped_dialog:  # se apertar pra pular, mostrar o texto completo
            visible_text = txt
        else:
            visible_text = txt[
                           0:int(self.counter // self.typing_speed)]  # esse tipo de slice permite ajustar a velocidade

            if self.sound_count % 4 == 0:
                self.sound_controller.sounds["dialogue"][1].play()
                self.sound_controller.sounds["dialogue"][1].set_volume(0.1)
                self.sound_count = 0
            self.sound_count += 1
        words = visible_text.split(' ')
        lines = []
        current_line = ''

        max_width = self.maximum_x_text_x_bounds - self.x_start_text

        for word in words:
            test_line = current_line + word + ' '
            text_width, _ = self.font.size(test_line)
            if text_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line.strip())
                current_line = word + ' '
        if current_line:
            lines.append(current_line.strip())

        # blitando cada linha
        for i, line in enumerate(lines):
            rendered = self.font.render(line, True, self.font_color)
            line_y = self.text_y_Pos + i * self.text_y_offset
            self.screen.blit(rendered, (self.text_x_Pos, line_y))

        # detectar se a última letra já foi renderizada
        if len(visible_text) >= len(txt):
            self.line_finished = True
            self.sound_controller.sounds["dialogue"][1].stop()

    def check_player_input(self, active_keys):
        for key in active_keys:
            if key == pg.K_SPACE:
                if not self.skip_key_pressed:
                    if self.line_finished:
                        self.next_dialog()
                    else:
                        self.skipped_dialog = True
                self.button_pressed_time = pg.time.get_ticks()
                self.skip_key_pressed = True

    def next_dialog(self):
        self.char_index = 0
        self.counter = 0
        self.dialog_index += 1
        self.text_x_Pos = self.x_start_text
        self.text_y_Pos = self.y_start_text
        self.rendered_text.clear()
        self.line_finished = False
        self.typing_speed = 3
        self.skipped_dialog = False

        if self.content_display_manager:
            self.content_display_manager.end()  # remove conteúdo atual
            self.content_display_manager.start_for_dialog(self.speaker, self.phase, self.dialog_index)

    def render_dialog_box(self):
        self.screen.blit(self.dialog_box_sprite, self.box_pos)
        face_sprite = pg.transform.smoothscale(GFX["dialog_faces"][f"{self.speaker}_Face"],
                                               (78, 75)).copy().convert_alpha()
        self.screen.blit(face_sprite, (70, WINDOW_HEIGHT - 164 + self.height_adjust))
        current_speaker_sprite = dialogues[self.speaker][self.phase][self.dialog_index][0]
        name_text = self.font.render(current_speaker_sprite, True, self.font_color)
        self.screen.blit(name_text, self.speaker_name_text_pos)

        if self.content_display_manager:
            self.content_display_manager.draw(self.screen)

    def start_dialog(self, speaker, phase):
        self.speaker = speaker
        self.dialog_active = True
        self.skipped_dialog = False
        self.phase = phase
        self.player.can_move = False
        self.sound_count = 0

        if self.content_display_manager:
            self.content_display_manager.start_for_dialog(self.speaker, self.phase, self.dialog_index)

    def end_dialog(self):
        self.dialog_index = 1
        if self.speaker == "NPC_1":
            pass
        for i in self.player.interactable:
            if i.name == self.speaker:
                i.talked_current_phase = True
        self.speaker = None
        self.dialog_active = False
        self.player.can_move = True

    def initialize_fonts(self):
        self.font = TEXT_FONT
        self.font_color = (0, 0, 100)

    def initialize_text_positions(self):
        self.text_start_pos = [200, 500 + self.height_adjust]

        self.x_start_text = 190
        self.text_x_Pos = self.x_start_text
        self.x_distance_between = 21
        self.maximum_x_text_x_bounds = 740

        self.y_start_text = 470 + self.height_adjust
        self.text_y_Pos = self.y_start_text
        self.text_y_offset = FONTS_DICT[FONT_INDEX][1] + 0

    def initialize_text_box(self):

        dialog_box_size = (WINDOW_WIDTH - 50, 150)
        self.dialog_box_sprite = pg.transform.smoothscale(GFX["ui"]["DialogBox"],
                                                          dialog_box_size).copy().convert_alpha()
        self.box_pos = (30, WINDOW_HEIGHT - 200 + self.height_adjust)
