from .views import *
import abc
from .models import *


def change_state(space_name):
    user_object = User.objects.get(name=space_name)
    current_state = states_list[user_object.state]
    next_state = states_list[current_state.next_state()]
    user_object.state = next_state
    user_object.save()


class State(metaclass=abc.ABCMeta):
    @staticmethod
    @abc.abstractmethod
    def label():
        pass
    
    @staticmethod
    @abc.abstractmethod
    def is_waiting_text():
        pass

    @staticmethod
    @abc.abstractmethod
    def next_state():
        pass


class InitialState(State):
    @staticmethod
    def label():
        return "initial_state"

    @staticmethod
    def is_waiting_text():
        return True

    @staticmethod
    def next_state():
        return "choice"


class ChoiceState(State):
    @staticmethod
    def label():
        return "choice"

    @staticmethod
    def is_waiting_text():
        return False

    @staticmethod
    def next_state():
        return "title"


class TitleState(State):
    @staticmethod
    def label():
        return "set_title"

    @staticmethod
    def is_waiting_text():
        return True

    @staticmethod
    def next_state():
        return "description"


class DescriptionState(State):
    @staticmethod
    def label():
        return "set_description"

    @staticmethod
    def is_waiting_text():
        return True

    @staticmethod
    def next_state():
        return "initial"


states_list = {"initial": InitialState, "choice": ChoiceState, "title": TitleState,
               "description": DescriptionState}
