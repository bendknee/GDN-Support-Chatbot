from hangouts import views
from hangouts.models import User, HardwareSupport, SoftwareSupport
from hangouts.states import end_state, hardware_choice, software_choice, state, states_conf


class DescriptionState(state.State):
    STATE_LABEL = "description"

    @staticmethod
    def is_waiting_text():
        return True

    @staticmethod
    def action(message, event):
        user_object = User.objects.get(name=event['space']['name'])

        work_item = user_object.get_work_item()
        work_item.description = message
        work_item.save()

        if isinstance(work_item, HardwareSupport):
            next_state = states_conf.change_state(user_object, hardware_choice.HardwareChoice.STATE_LABEL)
        elif isinstance(work_item, SoftwareSupport):
            next_state = states_conf.change_state(user_object, software_choice.SoftwareChoice.STATE_LABEL)

        if next_state == end_state.EndState.STATE_LABEL:
            return views.generate_edit_work_item(work_item)
        elif next_state == hardware_choice.HardwareChoice.STATE_LABEL:
            hardware_type = ["Internet/Wifi", "Laptop/Computer", "Mobile Device", "Other", "Printer"]
            return views.generate_choices("Choose Hardware Type", hardware_type, hardware_choice.HardwareChoice.STATE_LABEL)
        elif next_state == software_choice.SoftwareChoice.STATE_LABEL:
            third_party = ["GSuite", "Power BI", "VSTS", "Fill your own.."]
            return views.generate_choices("Choose 3rd Party Software", third_party, software_choice.SoftwareChoice.STATE_LABEL)

    @staticmethod
    def where():
        return "You're on `Description`. Please describe your issue."
