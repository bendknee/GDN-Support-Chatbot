from hangouts import views
from hangouts.models import HardwareSupport, SoftwareSupport
from hangouts.states import change_state, ChoiceState, TitleState


class ItemTypeState(ChoiceState):
    STATE_LABEL = "item_type"

    @staticmethod
    def is_waiting_text():
        return False

    @staticmethod
    def action(user_object, message, event):
        # views.delete_message(event['message']['name'])

        if message == 'Hardware Support':
            work_item_object = HardwareSupport.objects.create()
        elif message == 'Software Support':
            work_item_object = SoftwareSupport.objects.create()

        user_object.work_item = work_item_object
        user_object.save()

        change_state(user_object, TitleState.STATE_LABEL)

        return views.text_format("You've chosen `%s`\n\nPlease enter your issue Title." % message)

    @staticmethod
    def where():
        return "You're on `Choose Type`. Please pick desired work item Type from the card above."
