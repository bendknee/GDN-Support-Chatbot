from . import State
from abc import ABCMeta


class ChoiceState(State, metaclass=ABCMeta):
    @staticmethod
    def is_waiting_text():
        return False
