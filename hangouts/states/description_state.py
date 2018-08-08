from hangouts import views
from hangouts.models import HardwareSupport, SoftwareSupport
from hangouts.states import EndState, HardwareChoice, SoftwareChoice, State, change_state


class DescriptionState(State):
    STATE_LABEL = "description"

    @staticmethod
    def is_waiting_text():
        return True

    @staticmethod
    def action(user_object, message, event):
        work_item = user_object.get_work_item()
        work_item.description = message
        work_item.save()

        if isinstance(work_item, HardwareSupport):
            next_state = change_state(user_object, HardwareChoice.STATE_LABEL)
        elif isinstance(work_item, SoftwareSupport):
            next_state = change_state(user_object, SoftwareChoice.STATE_LABEL)

        if next_state == EndState.STATE_LABEL:
            return views.generate_edit_work_item(work_item)
        elif next_state == HardwareChoice.STATE_LABEL:
            return views.generate_choices("Choose Hardware Type", work_item.hardware_list, "hardware_type")
        elif next_state == SoftwareChoice.STATE_LABEL:
            return views.generate_choices("Choose 3rd Party Software", work_item.software_list, "software_type")

    @staticmethod
    def where():
        return "You're on `Description`. Please describe your issue."
