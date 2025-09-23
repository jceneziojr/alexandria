from ..core.state_machine import State


class QuitGame(State):
    """
    Estado que encerra o jogo imediatamente.
    Ao entrar neste estado, define self.quit = True.
    """

    def __init__(self):
        super().__init__()
        self.next = None  # não há próximo estado, pois o jogo será encerrado

    def startup(self, now, persistant):
        super().startup(now, persistant)
        self.quit = True  # força o encerramento do jogo assim que entra neste estado

    def cleanup(self):
        return super().cleanup()

    def update(self, keys, now):
        pass  # nada a atualizar

    def draw(self, surface):
        pass  # nada a desenhar

    def get_event(self, event):
        pass  # nenhum evento precisa ser tratado
