from hangouts import views
from hangouts.models import User
from hangouts.states import states_conf, item_type_state, state

from vsts.views import token_expired_or_refresh


class InitialState(state.State):
    STATE_LABEL = "initial"

    @staticmethod
    def is_waiting_text():
        return True

    @staticmethod
    def action(message, event):
        if message.lower() == 'support':
            user_object = User.objects.get(name=event['space']['name'])
            if user_object.jwt_token is None:
                return views.generate_signin_card(user_object)
            else:
                token_expired_or_refresh(user_object)
                states_conf.change_state(user_object, item_type_state.ItemTypeState.STATE_LABEL)
                return views.generate_choices("Choose work item type",
                                                       ["Hardware Support", "Software Support"], "choose_type")
        else:
            message = "I'm not sure what you mean. Type /help to see available commands."
            return views.text_format(message)

    @staticmethod
    def where():
        return "You're nowhere. Type `support` to begin issuing new Work Item."
