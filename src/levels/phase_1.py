import pygame as pg

from .base_level import Level


# https://www.gameart2d.com/license.html sprites daqui
# https://liberatedpixelcup.github.io/Universal-LPC-Spritesheet-Character-Generator/#?body=Body_color_light&head=Human_male_elderly_light&shadow=none_Shadow&sex=male&expression=Neutral_light&eyebrows=Thick_Eyebrows_white&nose=Elderly_nose_light&wrinkes=Wrinkles_light&beard=Winter_Beard_platinum&mustache=Mustache_white&hair=Balding_white&hairtie=none_Hair_Tie&headcover=none_Tied_Headband&headcover_rune=none_Thick_Headband_Rune&hat=none_Tricorne&shoulders=Mantal_brown&bauldron=none_Bauldron&vest=none_Vest&armour=none_Leather&clothes=Sleeveless_slate&legs=Legion_skirt_brown&shoes=Sandals_brown&weapon=Wand_wand
# https://kingbell.itch.io/pixel-sprite-mixer
# relação de velocidade npc/player = 2/120


class Phase1(Level):
    def __init__(self):
        super().__init__()
        self.current_level_name = "phase_1"

        self.next_level_name = "phase_2"
        self.map_id = 1
        self.info_box.box_active = True
        self.pressed_keys = set()
        self.info_box_message = ["Use as setas (← ↑ →) ou 'W A D' para se movimentar.",
                                 "Use a tecla 'E' para interagir com o NPC."]
        self.info_box_controller = [False, False]
        self.info_box.current_message = self.info_box_message[0]

    def handle_music(self):
        pg.mixer.music.load("resources/sound/sound_2.mp3")
        pg.mixer.music.set_volume(0.3)
        pg.mixer.music.play(-1)

    def get_npcs_current_level(self):
        for i in self.npc_sprites_g.sprites():
            if i.name == "Euclide":
                self.euclide = i

    def setup_level(self, game, persist):
        super().setup_level(game, persist)
        self.player.body.position = (30, 487)
        self.player.can_interact = True
        self.euclide.current_anim = "idle_available"
        self.euclide.anim_index = 0

        self.assist_global_handler.set_current_phase_number(None, override=1)

    def get_event(self, event: pg.event.Event, keys):
        if self.minigame_manager.active:
            self.minigame_manager.handle_event(event, keys)
        for key in keys:
            self.pressed_keys.add(key)

    def draw(self, surface, pymunk_surface):
        super().draw(surface, pymunk_surface)

    def update(self, now):
        # estrutura pra checar se o objetivo foi cumprido pra atualizar o info_box
        # basicamente, checo se a condição foi cumprida e se, o objetivo atual já chegou a ser concluido
        # e se o anterior ja foi cumprido

        # PARA PULAR A PRIMEIRA FASE
        # self.done = True
        self.euclide.update()

        if ({pg.K_UP, pg.K_RIGHT}.issubset(self.pressed_keys) or {pg.K_w, pg.K_d}.issubset(
                self.pressed_keys)) and not self.info_box_controller[0]:
            # self.info_box.box_active = False
            self.info_box_controller[0] = True
            self.info_box.current_message = self.info_box_message[1]
            self.pressed_keys.clear()

        if {pg.K_e}.issubset(self.pressed_keys) and not self.info_box_controller[1] and self.info_box_controller[0]:
            if self.player.used_E:
                self.euclide.current_anim = "idle"
                self.euclide.anim_index = 0
                self.info_box_controller[1] = True
                self.pressed_keys.clear()
                self.info_box.box_active = False

        if self.euclide.talked_current_phase:
            self.player.can_move = False
            self.euclide.rect.x += 2
            self.player.body.velocity = (120, 0)
            self.player.current_anim = "right"
            self.euclide.current_anim = "right"
            self.euclide.anim_index = 0
            self.player.can_interact = False

            if self.euclide.rect.x == 1000:
                self.done = True

        super().update(now)
