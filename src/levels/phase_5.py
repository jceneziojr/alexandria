import pygame as pg
from enum import Enum, auto

from .base_level import Level
from ..minigame.quizz import QuizMiniGame, GraphQuizMiniGame
from ..minigame.chapter_quizz import QuizChapterMiniGame
from ..core.configs import GFX
from ..minigame.aic import AICMiniGame
from ..minigame.parameter_estimation import ParameterEstimationMiniGame
from ..minigame.validation import OverfittingMiniGame


class Phase5(Level):
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
        MINIGAME_6 = auto()
        DIALOG_7_DELAY = auto()
        DIALOG_7 = auto()
        MINIGAME_7 = auto()
        DIALOG_8_DELAY = auto()
        DIALOG_8 = auto()
        COMPLETED = auto()

    def __init__(self):
        super().__init__()
        self.current_level_name = "phase_5"
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

        self.assist_global_handler.set_current_phase_number(None, override=15)

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
                                            question="Qual tipo de função é mais adequada para\nrepresentar o sinal acima",
                                            options=[
                                                {"text": "Logarítmica",
                                                 "correct": False},
                                                {"text": "Equação de\nsegundo grau",
                                                 "correct": False},
                                                {"text": "Senoide",
                                                 "correct": True},
                                                {"text": "Nenhuma das\nalternativas",
                                                 "correct": False},
                                            ],
                                            image=GFX["minigame_assets"]["senoide"],
                                            scale=1)
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
                self.minigame_manager.start(GraphQuizMiniGame,
                                            question="Qual o valor de y(k)?",
                                            options=[
                                                {"text": "5497.6",
                                                 "correct": False},
                                                {"text": "12641.7",
                                                 "correct": False},
                                                {"text": "2547.3",
                                                 "correct": False},
                                                {"text": "2550.7",
                                                 "correct": True},
                                            ],
                                            image=GFX["minigame_assets"]["quizz_regressor_v3"],
                                            scale=0.5)
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
                self.minigame_manager.start(AICMiniGame)
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
                self.minigame_manager.start(ParameterEstimationMiniGame)
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
                self.minigame_manager.start(OverfittingMiniGame)
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
                pg.mixer.music.load("resources/sound/sound_4.mp3")
                pg.mixer.music.set_volume(0.2)
                pg.mixer.music.play(-1)
                self.minigame_manager.start(
                    QuizChapterMiniGame,
                    quiz_data=[
                        {
                            "question": "Qual o fator mais importante na escolha\nda representação de um sistema?",
                            "options": [
                                {"text": "Sempre utilizar\nequações diferenciais", "correct": False},
                                {"text": "A complexidade\nmáxima possível", "correct": False},
                                {"text": "Utilizar inteligência\nartificial em\ntodos os casos", "correct": False},
                                {"text": "O objetivo da\nmodelagem e o\ntipo de sistema", "correct": True},
                            ],
                        },

                        {
                            "question": "Qual é a ideia central do Critério de\nInformação de Akaike (AIC)?",
                            "options": [
                                {"text": "Equilibrar perda\nde informação e\ncomplexidade do modelo", "correct": True},
                                {"text": "Eliminar resíduos\ncompletamente", "correct": False},
                                {"text": "Calcular os parâmetros\nvia mínimos quadrados", "correct": False},
                                {"text": "Estimar atrasos\ntemporais dos regressores", "correct": False},
                            ],
                        },
                        {
                            "type": GraphQuizMiniGame,
                            "question": "O que você você consegue supor\ndo ajuste acima?",
                            "options": [
                                {"text": "Os resíduos entre ajuste\ne dados são altos", "correct": False},
                                {"text": "Ocorreu overfitting\ndurante o ajuste",
                                 "correct": True},
                                {"text": "Ocorreu underfitting\ndurante o ajuste", "correct": False},
                                {"text": "O ajuste está\nadequado", "correct": False},
                            ],
                            "image": GFX["minigame_assets"]["quizz_over"],
                            "scale": 0.45
                        },

                        {
                            "question": "O que acontece se os parâmetros de um modelo\nnão forem ajustados corretamente?",
                            "options": [
                                {"text": "O modelo se torna\nlinear automaticamente", "correct": False},
                                {"text": "Os resíduos se tornam\nsempre nulos", "correct": False},
                                {"text": "O modelo pode\nperder sua precisão", "correct": True},
                                {"text": "Nada, pois os parâmetros\nnão influenciam no modelo", "correct": False},
                            ],
                        },
                        {
                            "type": QuizMiniGame,
                            "question": "O método dos mínimos quadrados é\nutilizado para:",
                            "options": [
                                {"text": "Ajustar os parâmetros\ndo modelo minimizando\nos resíduos", "correct": True},
                                {"text": "Escolher a representação\nmatemática do modelo", "correct": False},
                                {"text": "Determinar o grau de não\nlinearidade do modelo", "correct": False},
                                {"text": "Validar o modelo\ncomparando dados\nreais e preditos", "correct": False},
                            ],
                        },
                        {
                            "type": QuizMiniGame,
                            "question": "O que é um resíduo em um\nmodelo NARMAX?",
                            "options": [
                                {"text": "O valor real da\nsaída do sistema", "correct": False},
                                {"text": "A diferença entre o\nvalor real e o valor\npredito pelo modelo",
                                 "correct": True},
                                {"text": "O coeficiente que\nmultiplica um regressor", "correct": False},
                                {"text": "O atraso máximo\nconsiderado no modelo", "correct": False},
                            ],
                        },
                        {
                            "type": QuizMiniGame,
                            "question": "Qual é o objetivo de validar um\nmodelo matemático?",
                            "options": [
                                {"text": "Garantir que o modelo\nresolve o problema\ne representa o sistema",
                                 "correct": True},
                                {"text": "Aumentar o número de\nregressores usados", "correct": False},
                                {"text": "Minimizar o número\nde parâmetros", "correct": False},
                                {"text": "Evitar o uso de\nresíduos", "correct": False},
                            ],
                        },

                    ]
                )
                self.state = self.PhaseState.MINIGAME_6
                self.euclide.talked_current_phase = False

        elif self.state == self.PhaseState.MINIGAME_6:
            if not self.minigame_manager.active:
                self.assist_global_handler.set_current_phase_number(None)
                self.state = self.PhaseState.DIALOG_7_DELAY
                self.state_timestamp = now

        elif self.state == self.PhaseState.DIALOG_7_DELAY:
            if now - self.state_timestamp > 750:
                self.euclide.on_interaction()
                self.state = self.PhaseState.DIALOG_8
                self.euclide.talked_current_phase = False

        elif self.state == self.PhaseState.DIALOG_8:
            if self.euclide.talked_current_phase:
                self.state = self.PhaseState.COMPLETED

    def update(self, now):
        self.euclide.update()
        self.advance_state(now)
        super().update(now)
        if self.state == self.PhaseState.COMPLETED:
            self.done = True
