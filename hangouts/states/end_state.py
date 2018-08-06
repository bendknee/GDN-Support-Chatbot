from . import choice_state, description_state, hardware_choice, initial_state, severity_choice,\
    states_conf, software_choice, title_state

from hangouts import views
from hangouts.models import User

from vsts.views import create_work_item


class EndState(choice_state.ChoiceState):
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
            fields_dict = views.generate_fields_dict(work_item)

            work_item_dict = {}

            for key, value in path_dict.items():
                work_item_dict[value] = fields_dict[key]

            create_work_item(work_item_dict, work_item.url, user_object)
            print(work_item_dict)

            states_conf.change_state(user_object, initial_state.InitialState.STATE_LABEL)
            work_item.delete()

            return views.text_format("Your work item has been saved.")
            # return views.generate_work_item(work_item)

        elif message == "Title":
            user_object.state = title_state.TitleState.STATE_LABEL
            user_object.save()

            return views.text_format("Please enter your issue Title.")

        elif message == "Description":
            user_object.state = description_state.DescriptionState.STATE_LABEL
            user_object.save()

            return views.text_format("Please describe your issue.")

        elif message == "Hardware Type":
            user_object.state = hardware_choice.HardwareChoice.STATE_LABEL
            user_object.save()

            hardware_type = ["Internet/Wifi", "Laptop/Computer", "Mobile Device", "Other", "Printer"]
            return views.generate_choices("Choose Hardware Type", hardware_type, "hardware_type")

        elif message == "Severity":
            user_object.state = severity_choice.SeverityChoice.STATE_LABEL
            user_object.save()

            severities = ["1 - Critical", "2 - High", "3 - Medium", "4 - Low"]
            return views.generate_choices("How severe is this issue?", severities, "severity")

        elif message == "Third Party":
            user_object.state = software_choice.SoftwareChoice.STATE_LABEL
            user_object.save()

            third_party = ["GSuite", "Power BI", "VSTS", "Fill your own.."]
            return views.generate_choices("Choose 3rd Party Software", third_party, "software_type")

    @staticmethod
    def where():
        return "You're near the finish line. Please evaluate your issue at the card above and click" \
               " `save` when you're done."
