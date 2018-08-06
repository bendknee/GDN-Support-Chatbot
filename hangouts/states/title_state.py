from hangouts import views
from hangouts.models import User
from hangouts.states import description_state, end_state, state, states_conf


class TitleState(state.State):
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

        next_state = states_conf.change_state(user_object, description_state.DescriptionState.STATE_LABEL)

        if next_state == end_state.EndState.STATE_LABEL:
            return views.generate_edit_work_item(work_item)

        return views.text_format("Please describe your issue.")

    @staticmethod
    def where():
        return "You're on `Title`. Please enter issue Title."
