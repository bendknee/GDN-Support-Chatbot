from .description_state import DescriptionState
from .end_state import EndState
from .state import State
from .states_conf import change_state

from hangouts.models import User
from hangouts.views import generate_edit_work_item, text_format


class TitleState(State):
    STATE_LABEL = "title"

    @staticmethod
    def is_waiting_text():
        return True

    @staticmethod
    def action(message, event):
        user_object = User.objects.get(name=event['space']['name'])

        work_item = user_object.get_work_item()
        work_item.title = message
        work_item.save()

        next_state = change_state(user_object, DescriptionState.STATE_LABEL)

        if next_state == EndState.STATE_LABEL:
            return generate_edit_work_item(work_item)

        return text_format("Please describe your issue.")

    @staticmethod
    def where():
        return "You're on `Title`. Please enter issue Title."
