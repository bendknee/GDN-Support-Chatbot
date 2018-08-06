from .choice_state import ChoiceState
from .description_state import DescriptionState
from .hardware_choice import HardwareChoice
from .initial_state import InitialState
from .severity_choice import SeverityChoice
from .software_choice import SoftwareChoice
from .states_conf import change_state
from .title_state import TitleState

from hangouts.models import User
from hangouts.views import generate_choices, generate_fields_dict, text_format

from vsts.views import create_work_item


class EndState(ChoiceState):
    STATE_LABEL = "end"

    @staticmethod
    def action(message, event):
        user_object = User.objects.get(name=event['space']['name'])
        work_item = user_object.get_work_item()

        user_object.is_finished = True
        user_object.save()

        if message == "save":
            user_object.is_finished = False
            user_object.save()

            path_dict = work_item.path_dict
            fields_dict = generate_fields_dict(work_item)

            work_item_dict = {}

            for key, value in path_dict.items():
                work_item_dict[value] = fields_dict[key]

            create_work_item(work_item_dict, work_item.url, user_object)
            print(work_item_dict)

            change_state(user_object, InitialState.STATE_LABEL)
            work_item.delete()

            return text_format("Your work item has been saved.")

        elif message == "Title":
            user_object.state = TitleState.STATE_LABEL
            user_object.save()

            return text_format("Please enter your issue Title.")

        elif message == "Description":
            user_object.state = DescriptionState.STATE_LABEL
            user_object.save()

            return text_format("Please describe your issue.")

        elif message == "Hardware Type":
            user_object.state = HardwareChoice.STATE_LABEL
            user_object.save()

            hardware_type = ["Internet/Wifi", "Laptop/Computer", "Mobile Device", "Other", "Printer"]
            return generate_choices("Choose Hardware Type", hardware_type, "hardware_type")

        elif message == "Severity":
            user_object.state = SeverityChoice.STATE_LABEL
            user_object.save()

            severities = ["1 - Critical", "2 - High", "3 - Medium", "4 - Low"]
            return generate_choices("How severe is this issue?", severities, "severity")

        elif message == "Third Party":
            user_object.state = SoftwareChoice.STATE_LABEL
            user_object.save()

            third_party = ["GSuite", "Power BI", "VSTS", "Fill your own.."]
            return generate_choices("Choose 3rd Party Software", third_party, "software_type")

    @staticmethod
    def where():
        return "You're near the finish line. Please evaluate your issue at the card above and click" \
               " `save` when you're done."
