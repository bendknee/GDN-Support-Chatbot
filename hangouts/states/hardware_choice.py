from hangouts import views
from hangouts.models import User
from hangouts.states import end_state, states_conf, choice_state, severity_choice


class HardwareChoice(choice_state.ChoiceState):
    STATE_LABEL = "hardware_type"

    @staticmethod
    def action(message, event):
        # views.delete_message(event['message']['name'])

        user_object = User.objects.get(name=event['space']['name'])
        work_item = user_object.get_work_item()
        work_item.hardware_type = message
        work_item.save()

        next_state = states_conf.change_state(user_object, severity_choice.SeverityChoice.STATE_LABEL)

        if next_state == end_state.EndState.STATE_LABEL:
            return views.generate_edit_work_item(work_item)

        severities = ["1 - Critical", "2 - High", "3 - Medium", "4 - Low"]
        return views.generate_choices("How severe is this issue?", severities, "severity")

    @staticmethod
    def where():
        return "You're on `Choose Hardware`. Please select one Hardware Type that is being issued from the card above."
