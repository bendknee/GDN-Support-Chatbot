from hangouts import views
from hangouts.models import User
from hangouts.states import end_state, severity_choice, states_conf, state


class OtherSoftwareType(state.State):
    STATE_LABEL = "other_software_type"

    @staticmethod
    def is_waiting_text():
        return True

    @staticmethod
    def action(message, event):
        user_object = User.objects.get(name=event['space']['name'])

        work_item = user_object.get_work_item()
        work_item.third_party = message
        work_item.save()

        next_state = states_conf.change_state(user_object, severity_choice.SeverityChoice.STATE_LABEL)

        if next_state == end_state.EndState.STATE_LABEL:
            return views.generate_edit_work_item(work_item)

        severities = ["1 - Critical", "2 - High", "3 - Medium", "4 - Low"]
        return views.generate_choices("How severe is this issue?", severities, severity_choice.SeverityChoice.STATE_LABEL)

    @staticmethod
    def where():
        return "You're on `Custom Software Type`. Please enter your own desired 3rd party software."
