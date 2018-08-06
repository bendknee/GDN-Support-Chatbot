from hangouts import views
from hangouts.models import User
from hangouts.states import end_state, severity_choice, states_conf, choice_state, other_software_type


class SoftwareChoice(choice_state.ChoiceState):
    STATE_LABEL = "software_type"

    @staticmethod
    def action(message, event):
        # views.delete_message(event['message']['name'])

        user_object = User.objects.get(name=event['space']['name'])
        work_item = user_object.get_work_item()
        user_email = str(event['user']['email'])
        user_email = user_email.split("@")[0] + '@staff.gramedia.com'
        work_item.requested_by = user_email

        if message == "Fill your own..":
            work_item.save()
            user_object.state = other_software_type.OtherSoftwareType.STATE_LABEL
            user_object.save()
            return views.text_format("Please enter your own software type")

        work_item.third_party = message
        work_item.save()

        next_state = states_conf.change_state(user_object, severity_choice.SeverityChoice.STATE_LABEL)

        if next_state == end_state.EndState.STATE_LABEL:
            return views.generate_edit_work_item(work_item)

        severities = ["1 - Critical", "2 - High", "3 - Medium", "4 - Low"]
        return views.generate_choices("How severe is this issue?", severities, "severity")

    @staticmethod
    def where():
        return "You're on `Choose Software`. Please select 3rd Party App that is being issued from the card above."
