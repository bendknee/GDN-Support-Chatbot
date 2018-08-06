from .end_state import EndState
from .hardware_choice import HardwareChoice
from .software_choice import SoftwareChoice
from .state import State
from .states_conf import change_state

from hangouts.models import User, HardwareSupport, SoftwareSupport
from hangouts.views import generate_edit_work_item, generate_choices


class DescriptionState(State):
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
            next_state = change_state(user_object, HardwareChoice.STATE_LABEL)
        elif isinstance(work_item, SoftwareSupport):
            next_state = change_state(user_object, SoftwareChoice.STATE_LABEL)

        if next_state == EndState.STATE_LABEL:
            return generate_edit_work_item(work_item)
        elif next_state == HardwareChoice.STATE_LABEL:
            hardware_type = ["Internet/Wifi", "Laptop/Computer", "Mobile Device", "Other", "Printer"]
            return generate_choices("Choose Hardware Type", hardware_type, "hardware_type")
        elif next_state == SoftwareChoice.STATE_LABEL:
            third_party = ["GSuite", "Power BI", "VSTS", "Fill your own.."]
            return generate_choices("Choose 3rd Party Software", third_party, "software_type")

    @staticmethod
    def where():
        return "You're on `Description`. Please describe your issue."
