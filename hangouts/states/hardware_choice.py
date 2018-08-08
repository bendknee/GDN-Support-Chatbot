from hangouts import views
from hangouts.models import User
from hangouts.states import EndState, change_state, ChoiceState, SeverityChoice, severities_list


class HardwareChoice(ChoiceState):
    STATE_LABEL = "hardware_type"

    @staticmethod
    def action(message, event):
        views.delete_message(event['message']['name'])

        user_object = User.objects.get(name=event['space']['name'])
        work_item = user_object.get_work_item()
        work_item.hardware_type = message
        work_item.save()

        next_state = change_state(user_object, SeverityChoice.STATE_LABEL)

        if next_state == EndState.STATE_LABEL:
            return views.generate_edit_work_item(work_item)

        return views.generate_choices("How severe is this issue?", severities_list, "severity")

    @staticmethod
    def where():
        return "You're on `Choose Hardware`. Please select one Hardware Type that is being issued from the card above."
