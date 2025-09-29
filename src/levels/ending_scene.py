import pygame as pg
from enum import Enum, auto
from .base_level import Level


# https://www.gameart2d.com/license.html sprites daqui
# https://liberatedpixelcup.github.io/Universal-LPC-Spritesheet-Character-Generator/#?body=Body_color_light&head=Human_male_elderly_light&shadow=none_Shadow&sex=male&expression=Neutral_light&eyebrows=Thick_Eyebrows_white&nose=Elderly_nose_light&wrinkes=Wrinkles_light&beard=Winter_Beard_platinum&mustache=Mustache_white&hair=Balding_white&hairtie=none_Hair_Tie&headcover=none_Tied_Headband&headcover_rune=none_Thick_Headband_Rune&hat=none_Tricorne&shoulders=Mantal_brown&bauldron=none_Bauldron&vest=none_Vest&armour=none_Leather&clothes=Sleeveless_slate&legs=Legion_skirt_brown&shoes=Sandals_brown&weapon=Wand_wand
# https://kingbell.itch.io/pixel-sprite-mixer
# relação de velocidade npc/player = 2/120


class EndingScene(Level):
    class PhaseState(Enum):
        WAIT_INITIAL = auto()
        PAUSE_INITIAL = auto()
        MOVE_TO_ARCHIE = auto()
        TALK_ARCHIE = auto()
        WALK_OUT = auto()
        COMPLETED = auto()

    def __init__(self):
        super().__init__()
        self.current_level_name = "ending_scene"

        self.info_box.box_active = True
        self.pressed_keys = set()
        self.info_box_message = [""]
        self.info_box_controller = [False, False]
        self.info_box.current_message = self.info_box_message[0]

        self.state = self.PhaseState.WAIT_INITIAL
        self.state_timestamp = None

    def handle_music(self):
        pg.mixer.music.load("resources/sound/sound_5.mp3")
        pg.mixer.music.set_volume(0.3)
        pg.mixer.music.play(-1)

    def get_npcs_current_level(self):
        for i in self.npc_sprites_g.sprites():
            if i.name == "Archie":
                self.archie = i

    def setup_level(self, game, persist):
        super().setup_level(game, persist)
        self.player.body.position = (250, 487)
        self.player.can_interact = True
        self.archie.current_anim = "archie_idle"
        self.archie.anim_index = 0
        self.player.current_anim = "p_idle"
        self.player.anim_index = 0
        self.info_box.box_active = False

        self.dialog_started = False

        self.assist_global_handler.set_current_phase_number(None, override=22)

    def get_event(self, event: pg.event.Event, keys):
        if self.minigame_manager.active:
            self.minigame_manager.handle_event(event, keys)
        for key in keys:
            self.pressed_keys.add(key)

            if key == pg.K_r:
                self.done = True

    def draw(self, surface, pymunk_surface):
        super().draw(surface, pymunk_surface)

    def advance_state(self, now):
        if self.state == self.PhaseState.WAIT_INITIAL:
            self.player.can_interact = False
            self.player.anim_index = 0
            self.state = self.PhaseState.PAUSE_INITIAL
            self.state_timestamp = now

        elif self.state == self.PhaseState.PAUSE_INITIAL:
            self.player.can_interact = False
            if now - self.state_timestamp > 1000:
                self.state = self.PhaseState.MOVE_TO_ARCHIE
                self.player.current_anim = "p_right"
                self.player.anim_index = 0

        elif self.state == self.PhaseState.MOVE_TO_ARCHIE:
            self.player.body.velocity = (120, 0)
            if self.player.rect.x >= 715:
                self.player.body.velocity = (0, 0)
                self.state = self.PhaseState.TALK_ARCHIE
                self.player.current_anim = "p_idle"
                self.player.anim_index = 0

        elif self.state == self.PhaseState.TALK_ARCHIE:
            if not self.archie.talked_current_phase:
                if not self.dialog_started:
                    self.archie.on_interaction()
                    self.dialog_started = True
                else:
                    pass
            else:
                self.state = self.PhaseState.WALK_OUT
                self.player.current_anim = "p_left"
                self.player.anim_index = 0

        elif self.state == self.PhaseState.WALK_OUT:
            self.player.body.velocity = (-120, 0)
            if self.player.rect.x <= 400:
                self.done = True

    def update(self, now):
        # estrutura pra checar se o objetivo foi cumprido pra atualizar o info_box
        # basicamente, checo se a condição foi cumprida e se, o objetivo atual já chegou a ser concluido
        # e se o anterior ja foi cumprido

        self.player.can_move = False
        self.archie.update()
        self.advance_state(now)
        super().update(now)
