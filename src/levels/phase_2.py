import pygame as pg
from enum import Enum, auto

from .base_level import Level


# https://www.gameart2d.com/license.html sprites daqui
# https://liberatedpixelcup.github.io/Universal-LPC-Spritesheet-Character-Generator/#?body=Body_color_light&head=Human_male_elderly_light&shadow=none_Shadow&sex=male&expression=Neutral_light&eyebrows=Thick_Eyebrows_white&nose=Elderly_nose_light&wrinkes=Wrinkles_light&beard=Winter_Beard_platinum&mustache=Mustache_white&hair=Balding_white&hairtie=none_Hair_Tie&headcover=none_Tied_Headband&headcover_rune=none_Thick_Headband_Rune&hat=none_Tricorne&shoulders=Mantal_brown&bauldron=none_Bauldron&vest=none_Vest&armour=none_Leather&clothes=Sleeveless_slate&legs=Legion_skirt_brown&shoes=Sandals_brown&weapon=Wand_wand
# https://kingbell.itch.io/pixel-sprite-mixer
# relação de velocidade npc/player = 2/120

class Phase2(Level):
    class PhaseState(Enum):
        WAIT_FOR_INTERACT = auto()
        EUCLIDE_WALKING_RIGHT = auto()
        EUCLIDE_PAUSE = auto()
        EUCLIDE_RETURN = auto()
        EUCLIDE_EXIT = auto()
        COMPLETED = auto()
        WAIT_FOR_INTERACT_2 = auto()

    def __init__(self):
        super().__init__()
        self.current_level_name = "phase_2"
        self.next_level_name = "phase_3"

        self.map_id = 2
        self.info_box.box_active = True
        self.pressed_keys = set()
        self.info_box_message = ["Fale com Euclide."]
        self.info_box.current_message = self.info_box_message[0]

        self.state = self.PhaseState.WAIT_FOR_INTERACT
        self.state_timestamp = None

    def handle_music(self):
        pg.mixer.music.load("resources/sound/sound_3.mp3")
        pg.mixer.music.set_volume(0.05)
        pg.mixer.music.play(-1)

    def get_npcs_current_level(self):
        for i in self.npc_sprites_g.sprites():
            if i.name == "Euclide":
                self.euclide = i

    def get_event(self, event: pg.event.Event, keys):
        if self.minigame_manager.active:
            self.minigame_manager.handle_event(event, keys)
        for key in keys:
            self.pressed_keys.add(key)

    def draw(self, surface, pymunk_surface):
        super().draw(surface, pymunk_surface)

    def setup_level(self, game, persist):
        super().setup_level(game, persist)
        self.player.body.position = (100, 487)
        self.player.can_interact = True
        self.euclide.current_anim = "idle_available"

    def advance_state(self, now):
        """Gerencia transições de estado da fase."""

        if self.state == self.PhaseState.WAIT_FOR_INTERACT:
            if {pg.K_e}.issubset(self.pressed_keys) and self.player.used_E:
                self.euclide.current_anim = "idle"
                self.player.current_anim = "idle"
                self.player.anim_index = 0
                self.euclide.anim_index = 0
                self.info_box.box_active = False
                self.pressed_keys.clear()
                self.state = self.PhaseState.EUCLIDE_WALKING_RIGHT

        elif self.state == self.PhaseState.EUCLIDE_WALKING_RIGHT:
            if self.euclide.talked_current_phase:
                self.euclide.current_anim = "right"
                self.euclide.anim_index = 0
                self.player.can_move = False
                self.player.can_interact = False
                self.euclide.rect.x += 3
                if self.euclide.rect.x >= 500:
                    self.euclide.current_anim = "idle_back"
                    self.euclide.anim_index = 0
                    self.state = self.PhaseState.EUCLIDE_PAUSE
                    self.state_timestamp = now

        elif self.state == self.PhaseState.EUCLIDE_PAUSE:
            self.player.can_move = False
            if now - self.state_timestamp > 3000:
                self.state = self.PhaseState.EUCLIDE_RETURN
                self.euclide.current_anim = "left"
                self.euclide.anim_index = 0

        elif self.state == self.PhaseState.EUCLIDE_RETURN:
            self.euclide.rect.x -= 3
            if self.euclide.rect.x <= 195:
                self.euclide.talked_current_phase = False
                self.player.can_move = True
                self.player.can_interact = True
                self.assist_global_handler.set_current_phase_number(None)
                self.state = self.PhaseState.WAIT_FOR_INTERACT_2
                self.info_box.box_active = True
                self.euclide.current_anim = "idle_available"
                self.euclide.anim_index = 0
            else:
                self.player.can_move = False

        elif self.state == self.PhaseState.WAIT_FOR_INTERACT_2:
            if {pg.K_e}.issubset(self.pressed_keys) and self.player.used_E:
                self.euclide.current_anim = "idle"
                self.euclide.anim_index = 0
                self.info_box.box_active = False
                self.pressed_keys.clear()
                self.state = self.PhaseState.EUCLIDE_EXIT
                # nesse momento começa a saída

        elif self.state == self.PhaseState.EUCLIDE_EXIT:
            if self.euclide.talked_current_phase:
                self.player.can_move = False
                self.player.can_interact = False
                self.euclide.rect.x -= 2
                self.player.body.velocity = (-120, 0)
                self.player.current_anim = "left"
                self.player.anim_index = 0
                self.euclide.current_anim = "left"
                self.euclide.anim_index = 0

                if self.euclide.rect.x <= 10 or self.player.rect.x <= 10:
                    self.state = self.PhaseState.COMPLETED

        elif self.state == self.PhaseState.COMPLETED:
            self.done = True

    def update(self, now):
        self.euclide.update()
        self.advance_state(now)
        super().update(now)
