from .choice_state import ChoiceState
from .states_conf import change_state
from .state import State

from hangouts.models import User
from hangouts.views import generate_signin_card, generate_choices, text_format
from vsts.views import token_expired_or_refresh


class InitialState(State):
    STATE_LABEL = "initial"

    @staticmethod
    def is_waiting_text():
        return True

    @staticmethod
    def action(message, event):
        if message.lower() == 'support':
            user_object = User.objects.get(name=event['space']['name'])
            if user_object.jwt_token is None:
                return generate_signin_card(user_object)
            else:
                token_expired_or_refresh(user_object)
                change_state(user_object, ChoiceState.STATE_LABEL)
                return generate_choices("Choose work item type",
                                                       ["Hardware Support", "Software Support"], "choose_type")
        else:
            message = "I'm not sure what you mean. Type /help to see available commands."
            return text_format(message)

    @staticmethod
    def where():
        return "You're nowhere. Type `support` to begin issuing new Work Item."
