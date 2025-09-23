from .core import configs
from .core.tools import Controller
from .states import intro, game, main_menu, new_player, game_over, credits, quitgame


def main():
    game_app = Controller(
        configs.GAME_WINDOW_TITLE
    )  # cria a controladora e passa o título da janela

    state_dict = {  # dicionario com os estados do jogo
        "INTRO": intro.Intro(),  # animação de intro do jogo
        "GAME": game.Game(),  # estado base do jogo
        "MENU": main_menu.Menu(),  # menu principal do jogo,
        "NEW_PLAYER": new_player.NewPlayer(),
        "GAME_OVER": game_over.GameOver(),  # estado de game over
        "CREDITS": credits.Credits(),  # estado do crédito final
        "QUIT": quitgame.QuitGame()  # estado para sair do jogo
    }

    game_app.state_machine.setup_states(
        state_dict, "INTRO"
    )  # passando os estados para a máquina de estados da controladora, e setando INTRO como o primeiro estado
    game_app.main()  # chamando o main loop da controladora
