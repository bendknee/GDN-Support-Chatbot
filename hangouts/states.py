import abc
from .views import *


def change_state(space_name):
    user_object = User.objects.get(name=space_name)
    current_state = states_list[user_object.state]
    next_state = states_list[current_state.next_state()]
    User.objects.update(name=space_name, state=next_state)  # update state


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

    @staticmethod
    @abc.abstractmethod
    def previous_state():
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

    @staticmethod
    def previous_state():
        return "initial"


class ChoiceState(State):
    @staticmethod
    def label():
        return None

    @staticmethod
    def is_waiting_text():
        return False

    @staticmethod
    def next_state():
        return "title"

    @staticmethod
    def previous_state():
        return "initial"


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

    @staticmethod
    def previous_state():
        return "choice"


class DescriptionState(State):
    @staticmethod
    def label():
        return "set_description"

    @staticmethod
    def is_waiting_text():
        return True

    @staticmethod
    def next_state():
        return "work_item"

    @staticmethod
    def previous_state():
        return "title"


states_list = {"initial": InitialState, "choice": ChoiceState, "title": TitleState,
               "description": DescriptionState}
