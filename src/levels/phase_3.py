import pygame as pg
from enum import Enum, auto

from .base_level import Level
from ..minigame.quizz import QuizMiniGame
from ..minigame.projectile import ProjectileMiniGame
from ..minigame.tank import IndustrialTankMiniGame
from ..minigame.chapter_quizz import QuizChapterMiniGame


class Phase3(Level):
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
        COMPLETED = auto()

    def __init__(self):
        super().__init__()
        self.current_level_name = "phase_3"
        self.next_level_name = "phase_4"

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

        self.assist_global_handler.set_current_phase_number(None, override=4)

    def advance_state(self, now):
        """Gerencia a transição de estados da fase."""

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
                self.minigame_manager.start(
                    QuizMiniGame,
                    question="Qual destes é um modelo?",
                    options=[
                        {"text": "Maquete de uma aeronave", "correct": True},
                        {"text": "Equação do projétil", "correct": True},
                        {"text": "Simulação de um circuito", "correct": True},
                        {"text": "Inteligência Artificial", "correct": True},
                    ]
                )
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
                self.minigame_manager.start(ProjectileMiniGame)
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
                self.minigame_manager.start(IndustrialTankMiniGame)
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
                pg.mixer.music.load("resources/sound/sound_4.mp3")
                pg.mixer.music.set_volume(0.2)
                pg.mixer.music.play(-1)
                self.minigame_manager.start(
                    QuizChapterMiniGame,
                    quiz_data=[
                        {
                            "question": "O que caracteriza um modelo matemático?",
                            "options": [
                                {"text": "Uma representação\nartística de um sistema", "correct": False},
                                {
                                    "text": "Uma representação de um\nsistema por hipóteses\nsobre sua estrutura\ne comportamento",
                                    "correct": True},
                                {"text": "A reprodução física\n em escala reduzida\nde um objeto", "correct": False},
                                {"text": "Um software de\nsimulação gráfica", "correct": False},
                            ],
                        },
                        {
                            "question": "Por que diferentes modelos podem\nrepresentar um mesmo sistema?",
                            "options": [
                                {"text": "Porque todos os\nmodelos são iguais", "correct": False},
                                {
                                    "text": "Porque podem existir\ndiferentes hipóteses ou\nparâmetros que levam\na resultados semelhantes",
                                    "correct": True},
                                {"text": "Porque apenas um tipo\nde modelo é válido em\ncada situação",
                                 "correct": False},
                                {"text": "Porque o sistema\nnunca se altera", "correct": False},
                            ],
                        },
                        {
                            "question": "Qual das opções NÃO pode ser\nconsiderada um modelo?",
                            "options": [
                                {"text": "Uma maquete de avião", "correct": False},
                                {"text": "A equação da trajetória\nde um projétil", "correct": False},
                                {"text": "O próprio avião\nreal em voo", "correct": True},
                                {"text": "Um simulador de\ncircuitos elétricos", "correct": False},
                            ],
                        },
                        {
                            "question": "No exemplo do fluido volátil,\nqual foi o problema de não\npossuir um modelo adequado?",
                            "options": [
                                {"text": "O tanque esvaziou\nrapidamente", "correct": False},
                                {"text": "O fluido não reagiu\nà temperatura", "correct": False},
                                {"text": "A expansão do fluido\nultrapassou o limite\nseguro e causou explosão",
                                 "correct": True},
                                {"text": "O fluido se manteve\nestável mesmo acima\nde 80°C", "correct": False},
                            ],
                        },
                        {
                            "question": "Qual das opções apresenta\num benefício do uso\nde modelos?",
                            "options": [
                                {"text": "Evitar acidentes ao\nprever comportamentos\ndo sistema", "correct": True},
                                {"text": "Garantir que todos os\nsistemas tenham sempre o\nmesmo resultado",
                                 "correct": False},
                                {"text": "Eliminar totalmente a\nnecessidade de medições\nreais", "correct": False},
                                {"text": "Tornar desnecessário o\nestudo do funcionamento\ninterno do sistema",
                                 "correct": False},
                            ],
                        },
                    ]
                )
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
                self.state = self.PhaseState.COMPLETED

    def update(self, now):
        self.euclide.update()
        self.advance_state(now)
        super().update(now)
        if self.state == self.PhaseState.COMPLETED:
            self.done = True
