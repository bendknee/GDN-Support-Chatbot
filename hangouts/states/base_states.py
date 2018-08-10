from abc import abstractmethod, ABCMeta


class State(metaclass=ABCMeta):
    STATE_LABEL = None

    @staticmethod
    @abstractmethod
    def action(user_object, message, event):
        pass

    @staticmethod
    @abstractmethod
    def is_waiting_text():
        pass

    @staticmethod
    @abstractmethod
    def where():
        pass


class TextState(State, metaclass=ABCMeta):
    @staticmethod
    def is_waiting_text():
        return True


class ChoiceState(State, metaclass=ABCMeta):
    @staticmethod
    def is_waiting_text():
        return False
