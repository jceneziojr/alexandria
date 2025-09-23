from __future__ import annotations

import pygame as pg
from pymunk import Space
from typing import Union, Dict


class StateMachine:
    def __init__(self, space, draw_opt):
        self.done: bool = False
        self.state_dict: Dict[str, State] = {}  # dict com os estados do jogo
        self.state_name: Union[str, None] = None  # nome do estado atual
        self.state: Union[State, None] = None  # objeto do estado atual
        self.now = None  # guarda o tempo total da simulação
        self.space: Space = space
        self.draw_opt = draw_opt

    def setup_states(self, state_dict: Dict[str, State], start_state: str):
        """
        Initialize the state_dict and sets a start_state
        """
        self.state_dict = state_dict
        self.state_name = start_state  # str com o primeiro estado do jogo
        self.state = self.state_dict[
            self.state_name
        ]  # iniciando o primeiro estado do jogo

    def update(self, keys, now):
        """
        Checks if a state is done or has called for a game quit.
        State is flipped if necessary and State.update is called.
        """
        self.now = now  # pega o tempo total da simulação obtido pela controladora
        if self.state.quit:  # checa se algum comando para sair foi dado
            self.done = True
        elif self.state.done:  # se o estado tiver concluído
            self.flip_state()  # avança para o proximo estado
        self.state.update(keys, now)

    def draw(self, surface: pg.Surface):
        self.state.draw(surface)  # chama o método de draw do estado atual

    def flip_state(self):
        """
        When a State changes to done necessary startup and cleanup functions
        are called and the current State is changed.
        """
        previous, self.state_name = (
            self.state_name,
            self.state.next,
        )  # muda o estado para o proximo
        persist = (
            self.state.cleanup()
        )  # roda o cleanup do estado e pega variáveis persistentes

        """NÃO ESQUECER DE CHECAR ESSA SEÇÃO APÓS MUDAR O MENU INICIAL"""
        # if self.state_name == "GAME":
        # persist["space"] = self.space
        # persist["draw_opt"] = self.draw_opt  # quando terminar o menu, tem que mudar essa estrutura
        if self.state_name == "GAME":
            self.state_dict[self.state_name].__init__()

        self.state = self.state_dict[self.state_name]  # chamando o estado
        self.state.previous = previous
        self.state.startup(self.now, persist)  # roda o startup do estado


    def get_event(self, event):
        """
        Pass events down to current State.
        """
        self.state.get_event(
            event
        )  # manda o evento que a controladora capturou para o estado


class State(object):
    """
    All states should inherit from this class.
    Both get_event and update must be overloaded in the child-class.
    The startup and cleanup methods need to be overloaded when there
    is src that must persist between States.
    """

    def __init__(self):
        self.start_time: float = 0.0
        self.now: float = 0.0
        self.done: bool = False
        self.quit: bool = False
        self.next = None
        self.previous = None
        self.persist: dict = {}

    def get_event(self, event):
        """
        Processes events that were passed from the main event loop.
        Must be overloaded in children.
        """
        pass

    def startup(self, now, persistant: dict):
        """
        Add variables passed in persistant to the proper attributes and
        set the start time of the State to the current time.
        """
        self.persist = persistant
        self.start_time = now

    def cleanup(self):
        """
        Add variables that should persist to the self.persist dictionary.
        Then reset State.done to False.
        """
        self.done = False
        return self.persist

    def update(self, keys, now):
        """
        Update function for state.
        Must be overloaded in children.
        """
        pass

    def draw(self, surface):
        """
        Draw function for state.
        Must be overloaded in children.
        """
        pass
