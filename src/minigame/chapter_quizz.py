from .minigame_manager import MiniGame
from .quizz import QuizMiniGame
from math import ceil


class QuizChapterMiniGame(MiniGame):
    def __init__(self, size, **kwargs):
        super().__init__(size, **kwargs)

        # lista de perguntas
        self.quiz_data = kwargs.get("quiz_data", [])
        self.current_question = 0
        self.errors = 0

        # instância do minigame individual
        self.current_game = None
        self.load_question()

    def load_question(self):
        """Carrega o próximo QuizMiniGame ou GraphQuizMiniGame"""
        if self.current_question >= len(self.quiz_data):
            # acabou o quiz
            self.finished = True
            if len(self.quiz_data) <= 5:
                self.failed = self.errors > 2
            else:
                self.failed = self.errors > ceil(0.4 * len(self.quiz_data))
            return

        q = self.quiz_data[self.current_question]

        # --- integração aqui ---
        game_class = q.get("type", QuizMiniGame)  # padrão: QuizMiniGame
        game_kwargs = {
            "question": q["question"],
            "options": q["options"]
        }

        # argumentos extras (caso seja GraphQuizMiniGame)
        if "image" in q:
            game_kwargs["image"] = q["image"]
        if "scale" in q:
            game_kwargs["scale"] = q["scale"]

        self.current_game = game_class(
            (self.width, self.height),
            **game_kwargs
        )

    def handle_event(self, event, keys):
        if self.current_game and not self.finished:
            self.current_game.handle_event(event, keys)

    def update(self, dt):
        if self.current_game and not self.finished:
            self.current_game.update(dt)

            if self.current_game.finished:
                # verificar se errou
                if self.current_game.failed:
                    self.errors += 1

                if self.errors > 2:
                    self.finished = True
                    self.failed = True
                else:
                    self.current_question += 1
                    self.load_question()

    def draw(self, surface):
        if self.current_game and not self.finished:
            self.current_game.draw(surface)
