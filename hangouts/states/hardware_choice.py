from hangouts import views
from hangouts.states import EndState, change_state, ChoiceState, SeverityChoice


class HardwareChoice(ChoiceState):
    STATE_LABEL = "hardware_type"

    @staticmethod
    def action(user_object, message, event):
        # views.delete_message(event['message']['name'])

        work_item = user_object.get_work_item()
        work_item.hardware_type = message
        work_item.save()

        next_state = change_state(user_object, SeverityChoice.STATE_LABEL)

        if next_state == EndState.STATE_LABEL:
            return views.generate_edit_work_item(work_item)

        return views.generate_choices("How severe is this issue?", work_item.severities_list, SeverityChoice.STATE_LABEL)

    @staticmethod
    def where():
        return "You're on `Choose Hardware`. Please select one Hardware Type that is being issued from the card above."
