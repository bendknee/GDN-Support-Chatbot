from hangouts import views
from hangouts.models import User
from hangouts.states import EndState, change_state, ChoiceState


class SeverityChoice(ChoiceState):
    STATE_LABEL = "severity"

    @staticmethod
    def action(message, event):
        # views.delete_message(event['message']['name'])

        user_object = User.objects.get(name=event['space']['name'])
        work_item = user_object.get_work_item()
        work_item.severity = message
        work_item.save()

        change_state(user_object, EndState.STATE_LABEL)
        return views.generate_edit_work_item(work_item)

    @staticmethod
    def where():
        return "You're on `Choose Severity`. Please select this issue's severity level from the card above."
