from hangouts import views
from hangouts.models import User
from hangouts.states import DescriptionState, EndState, State, change_state


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
            return views.generate_edit_work_item(work_item)

        return views.text_format("Please describe your issue.")

    @staticmethod
    def where():
        return "You're on `Title`. Please enter issue Title."
