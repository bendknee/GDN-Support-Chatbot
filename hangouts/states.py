import abc
from .views import *


class Context:
    def __init__(self, state):
        self._state = state

    def request(self):
        self._state.handle()


class State(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def is_waiting_text(self):
        pass

    @abc.abstractmethod
    def next_state(self):
        pass

    @abc.abstractmethod
    def previous_state(self):
        pass


class InitialState(State):
    def is_waiting_text(self):
        return True

    def next_state(self):
        return ChoiceState

    def previous_state(self):
        return InitialState


class ChoiceState(State):
    def is_waiting_text(self):
        return False

    def next_state(self):
        return

    def previous_state(self):
        return InitialState


class TitleState(State):
    def is_waiting_text(self):
        return True

    def next_state(self):
        return
