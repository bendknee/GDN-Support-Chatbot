from hangouts import views
from hangouts.states import change_state, ItemTypeState, State

from vsts.views import token_expired_or_refresh

available_types = ["Hardware Support", "Software Support"]


class InitialState(State):
    STATE_LABEL = "initial"

    @staticmethod
    def is_waiting_text():
        return True

    @staticmethod
    def action(user_object, message, event):
        if message.lower() == 'support':
            if user_object.jwt_token is None:
                return views.generate_signin_card(user_object)
            else:
                token_expired_or_refresh(user_object)
                change_state(user_object, ItemTypeState.STATE_LABEL)
                return views.generate_choices("Choose work item type", available_types, ItemTypeState.STATE_LABEL)
        else:
            message = "I'm not sure what you mean. Type /help to see available commands."
            return views.text_format(message)

    @staticmethod
    def where():
        return "You're nowhere. Type `support` to begin issuing new Work Item."
