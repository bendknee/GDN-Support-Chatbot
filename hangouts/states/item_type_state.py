from .states_conf import change_state
from .choice_state import ChoiceState
from .title_state import TitleState

from hangouts.models import User, HardwareSupport, SoftwareSupport
from hangouts.views import delete_message, text_format


class ItemTypeState(ChoiceState):
    STATE_LABEL = "choice"

    @staticmethod
    def is_waiting_text():
        return False

    @staticmethod
    def action(message, event):
        delete_message(event['message']['name'])

        user_object = User.objects.get(name=event['space']['name'])
        if message == 'Hardware Support':
            work_item_object = HardwareSupport.objects.create()
        elif message == 'Software Support':
            work_item_object = SoftwareSupport.objects.create()

        user_object.work_item = work_item_object
        user_object.save()

        change_state(user_object, TitleState.STATE_LABEL)

        return text_format("You've chosen `%s`\n\nPlease enter your issue Title." % message)

    @staticmethod
    def where():
        return "You're on `Choose Type`. Please pick desired work item Type from the card above."
