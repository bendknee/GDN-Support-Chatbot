from hangouts import views
from hangouts.models import User
from hangouts.states import end_state, states_conf, choice_state


class SeverityChoice(choice_state.ChoiceState):
    STATE_LABEL = "severity"

    @staticmethod
    def action(message, event):
        views.delete_message(event['message']['name'])

        user_object = User.objects.get(name=event['space']['name'])
        work_item = user_object.get_work_item()
        work_item.severity = message
        work_item.save()

        states_conf.change_state(user_object, end_state.EndState.STATE_LABEL)
        return views.generate_edit_work_item(work_item)

    @staticmethod
    def where():
        return "You're on `Choose Severity`. Please select this issue's severity level from the card above."
