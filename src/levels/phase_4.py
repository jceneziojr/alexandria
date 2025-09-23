import pygame as pg
from enum import Enum, auto

from .base_level import Level
from ..minigame.quizz import QuizMiniGame, GraphQuizMiniGame
from ..minigame.sampling import SamplingEffectMiniGame
from ..minigame.chapter_quizz import QuizChapterMiniGame
from ..minigame.prbsrc import PRBSRCMiniGame
from ..core.configs import GFX


class Phase4(Level):
    class PhaseState(Enum):
        WAIT_FOR_INTERACT = auto()
        DIALOG_1 = auto()
        MINIGAME_1 = auto()
        DIALOG_2_DELAY = auto()
        DIALOG_2 = auto()
        MINIGAME_2 = auto()
        DIALOG_3_DELAY = auto()
        DIALOG_3 = auto()
        MINIGAME_3 = auto()
        DIALOG_4_DELAY = auto()
        DIALOG_4 = auto()
        MINIGAME_4 = auto()
        DIALOG_5_DELAY = auto()
        DIALOG_5 = auto()
        MINIGAME_5 = auto()
        DIALOG_6_DELAY = auto()
        DIALOG_6 = auto()
        COMPLETED = auto()

    def __init__(self):
        super().__init__()
        self.current_level_name = "phase_4"
        self.next_level_name = "phase_5"
        self.info_box.box_active = True
        self.pressed_keys = set()
        self.info_box_message = ["Fale com Euclide."]
        self.info_box.current_message = self.info_box_message[0]
        self.state = self.PhaseState.WAIT_FOR_INTERACT
        self.state_timestamp = None

    def handle_music(self):
        pg.mixer.music.load("resources/sound/sound_7.mp3")
        pg.mixer.music.set_volume(0.3)
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
        self.player.body.position = (300, 487)
        self.player.can_interact = True
        self.player.can_move = True
        self.euclide.current_anim = "idle_available"
        self.euclide.anim_index = 0

        self.assist_global_handler.set_current_phase_number(None, override=9)


    def advance_state(self, now):
        """gerencia a transição de estados da fase."""
        if self.state == self.PhaseState.WAIT_FOR_INTERACT:
            if {pg.K_e}.issubset(self.pressed_keys) and self.player.used_E:
                self.euclide.current_anim = "idle"
                self.player.current_anim = "idle"
                self.player.anim_index = 0
                self.euclide.anim_index = 0
                self.info_box.box_active = False
                self.pressed_keys.clear()
                self.state = self.PhaseState.DIALOG_1

        elif self.state == self.PhaseState.DIALOG_1:
            if self.euclide.talked_current_phase:
                self.minigame_manager.start(GraphQuizMiniGame,
                                            question="Qual a temperatura do sistema?",
                                            options=[
                                                {"text": "30.0°C",
                                                 "correct": False},
                                                {"text": "35.0°C",
                                                 "correct": True},
                                                {"text": "40.0°C",
                                                 "correct": False},
                                                {"text": "45.0°C",
                                                 "correct": False},
                                            ],
                                            image=GFX["minigame_assets"]["temp_planta"],
                                            scale=0.45, protect=True)
                self.state = self.PhaseState.MINIGAME_1
                self.euclide.talked_current_phase = False

        elif self.state == self.PhaseState.MINIGAME_1:
            if not self.minigame_manager.active:
                self.assist_global_handler.set_current_phase_number(None)
                self.state = self.PhaseState.DIALOG_2_DELAY
                self.state_timestamp = now

        elif self.state == self.PhaseState.DIALOG_2_DELAY:
            if now - self.state_timestamp > 750:
                self.euclide.on_interaction()
                self.state = self.PhaseState.DIALOG_2
                self.euclide.talked_current_phase = False

        elif self.state == self.PhaseState.DIALOG_2:
            if self.euclide.talked_current_phase:
                self.minigame_manager.start(SamplingEffectMiniGame)
                self.state = self.PhaseState.MINIGAME_2
                self.euclide.talked_current_phase = False

        elif self.state == self.PhaseState.MINIGAME_2:
            if not self.minigame_manager.active:
                self.assist_global_handler.set_current_phase_number(None)
                self.state = self.PhaseState.DIALOG_3_DELAY
                self.state_timestamp = now

        elif self.state == self.PhaseState.DIALOG_3_DELAY:
            if now - self.state_timestamp > 750:
                self.euclide.on_interaction()
                self.state = self.PhaseState.DIALOG_3
                self.euclide.talked_current_phase = False

        elif self.state == self.PhaseState.DIALOG_3:
            if self.euclide.talked_current_phase:
                self.minigame_manager.start(QuizMiniGame,
                                            question="Quais as componentes de frequências de\num bom sinal de excitação?",
                                            options=[
                                                {"text": "Baixas frequências",
                                                 "correct": False},
                                                {"text": "Todo o espectro\nde frequência",
                                                 "correct": True},
                                                {"text": "Médias frequências",
                                                 "correct": False},
                                                {"text": "Altas frequências",
                                                 "correct": False},
                                            ])
                self.state = self.PhaseState.MINIGAME_3
                self.euclide.talked_current_phase = False

        elif self.state == self.PhaseState.MINIGAME_3:
            if not self.minigame_manager.active:
                self.assist_global_handler.set_current_phase_number(None)
                self.state = self.PhaseState.DIALOG_4_DELAY
                self.state_timestamp = now

        elif self.state == self.PhaseState.DIALOG_4_DELAY:
            if now - self.state_timestamp > 750:
                self.euclide.on_interaction()
                self.state = self.PhaseState.DIALOG_4
                self.euclide.talked_current_phase = False

        elif self.state == self.PhaseState.DIALOG_4:
            if self.euclide.talked_current_phase:
                self.minigame_manager.start(PRBSRCMiniGame)
                self.state = self.PhaseState.MINIGAME_4
                self.euclide.talked_current_phase = False

        elif self.state == self.PhaseState.MINIGAME_4:
            if not self.minigame_manager.active:
                self.assist_global_handler.set_current_phase_number(None)
                self.state = self.PhaseState.DIALOG_5_DELAY
                self.state_timestamp = now

        elif self.state == self.PhaseState.DIALOG_5_DELAY:
            if now - self.state_timestamp > 750:
                self.euclide.on_interaction()
                self.state = self.PhaseState.DIALOG_5
                self.euclide.talked_current_phase = False

        elif self.state == self.PhaseState.DIALOG_5:
            if self.euclide.talked_current_phase:
                pg.mixer.music.load("resources/sound/sound_4.mp3")
                pg.mixer.music.set_volume(0.2)
                pg.mixer.music.play(-1)
                self.minigame_manager.start(
                    QuizChapterMiniGame,
                    quiz_data=[
                        {
                            "type": QuizMiniGame,  # opcional, pois já é o padrão
                            "question": "Qual a característica de\num bom sinal de excitação?",
                            "options": [
                                {"text": "Ter um valor de\namplitude constante",
                                 "correct": False},
                                {"text": "Ter uma frequência de\ncomutação alta",
                                 "correct": False},
                                {"text": "Não existe uma\ncaracterística para se\nconsiderar",
                                 "correct": False},
                                {"text": "Ser capaz de excitar\nas diversas dinâmicas\ndo sistema",
                                 "correct": True},
                            ],
                        },
                        {
                            "type": GraphQuizMiniGame,
                            "question": "Qual o problema que observamos\nna resposta ao PRBS acima?",
                            "options": [
                                {"text": "O tempo entre bits\né muito alto",
                                 "correct": True},
                                {"text": "O PRBS não excitou\no regime permanente",
                                 "correct": False},
                                {"text": "Não podemos observar\nnenhum problema",
                                 "correct": False},
                                {"text": "O tempo entre bits\né muito baixo",
                                 "correct": False},
                            ],
                            "image": GFX["minigame_assets"]["quizz_graph_1"],
                            "scale": 0.65
                        },
                        {  # \n
                            "question": "Determine qual a afirmação\nestá correta:",
                            "options": [
                                {"text": "A coleta de dados não\ninfluencia no modelo\nfinal",
                                 "correct": False},
                                {"text": "Dados ruins podem sempre\nser facilmente corrigidos\ndepois",
                                 "correct": False},
                                {"text": "Modelos são construídos\ncom dados, e dados ruins\ngeram modelos ruins",
                                 "correct": True},
                                {
                                    "text": "A coleta de dados é a\netapa menos importante no\nprocesso de identificação",
                                    "correct": False},
                            ],
                        },
                        {
                            "question": "Quais são exemplos de causas\nde ruído em medições?",
                            "options": [
                                {
                                    "text": "Interferências\neletromagnéticas,\nsensores de alta qualidade\ne algoritmos de filtragem",
                                    "correct": False},
                                {
                                    "text": "Interferência humana,\ncircuitos de baixa\nqualidade e interferências\neletromagnéticas",
                                    "correct": True},
                                {"text": "Apenas o ambiente em que\no sistema está",
                                 "correct": False},
                                {"text": "Exclusivamente erros\nhumanos",
                                 "correct": False},
                            ],
                        },
                        {
                            "question": "O que é um filtro no contexto da\naquisição de dados?",
                            "options": [
                                {"text": "Um dispositivo que\naumenta a quantidade\nde dados coletados",
                                 "correct": False},
                                {"text": "Uma técnica ou\ndispositivo que remove\numa parte indesejada\ndo sinal",
                                 "correct": True},
                                {"text": "Um sensor de alta\nprecisão",
                                 "correct": False},
                                {"text": "Um sinal de excitação\naplicado ao sistema",
                                 "correct": False},
                            ],
                        },
                    ]
                )
                self.state = self.PhaseState.MINIGAME_5
                self.euclide.talked_current_phase = False

        elif self.state == self.PhaseState.MINIGAME_5:
            if not self.minigame_manager.active:
                self.assist_global_handler.set_current_phase_number(None)
                self.state = self.PhaseState.DIALOG_6_DELAY
                self.state_timestamp = now

        elif self.state == self.PhaseState.DIALOG_6_DELAY:
            if now - self.state_timestamp > 750:
                self.euclide.on_interaction()
                self.state = self.PhaseState.DIALOG_6
                self.euclide.talked_current_phase = False

        elif self.state == self.PhaseState.DIALOG_6:
            if self.euclide.talked_current_phase:
                self.state = self.PhaseState.COMPLETED

    def update(self, now):
        self.euclide.update()
        self.advance_state(now)
        super().update(now)
        if self.state == self.PhaseState.COMPLETED:
            self.done = True
