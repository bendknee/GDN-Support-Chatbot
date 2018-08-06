from .models import *
from hangouts import views as hangouts
from vsts import views as vsts
import abc


def change_state(user_object, next_state):
    current_state = states_list[user_object.state]

    if user_object.is_finished:
        next_state = EndState.STATE_LABEL

    print("current state: " + current_state.STATE_LABEL)
    print("next state: " + next_state)

    user_object.state = next_state
    user_object.save()
    return next_state


class State(metaclass=abc.ABCMeta):
    STATE_LABEL = None

    @staticmethod
    @abc.abstractmethod
    def action(message, event):
        pass

    @staticmethod
    @abc.abstractmethod
    def is_waiting_text():
        pass

    @staticmethod
    @abc.abstractmethod
    def where():
        pass


class InitialState(State):
    STATE_LABEL = "initial"

    @staticmethod
    def is_waiting_text():
        return True

    @staticmethod
    def action(message, event):
        if message.lower() == 'support':
            user_object = User.objects.get(name=event['space']['name'])
            if user_object.jwt_token is None:
                return hangouts.generate_signin_card(user_object)
            else:
                vsts.token_expired_or_refresh(user_object)
                change_state(user_object, ChoiceState.STATE_LABEL)
                return hangouts.generate_choices("Choose work item type",
                                                       ["Hardware Support", "Software Support"], "choose_type")
        else:
            message = "I'm not sure what you mean. Type /help to see available commands."
            return hangouts.text_format(message)

    @staticmethod
    def where():
        return "You're nowhere. Type `support` to begin issuing new Work Item."


class ChoiceState(State):
    STATE_LABEL = "choice"

    @staticmethod
    def is_waiting_text():
        return False

    @staticmethod
    def action(message, event):
        hangouts.delete_message(event['message']['name'])

        user_object = User.objects.get(name=event['space']['name'])
        if message == 'Hardware Support':
            work_item_object = HardwareSupport.objects.create()
        elif message == 'Software Support':
            work_item_object = SoftwareSupport.objects.create()

        user_object.work_item = work_item_object
        user_object.save()

        change_state(user_object, TitleState.STATE_LABEL)

        return hangouts.text_format("You've chosen `%s`\n\nPlease enter your issue Title." % message)

    @staticmethod
    def where():
        return "You're on `Choose Type`. Please pick desired work item Type from the card above."


class TitleState(State):
    STATE_LABEL = "title"

    @staticmethod
    def is_waiting_text():
        return True

    @staticmethod
    def action(message, event):
        user_object = User.objects.get(name=event['space']['name'])

        work_item = user_object.get_work_item()
        work_item.title = message
        work_item.save()

        next_state = change_state(user_object, DescriptionState.STATE_LABEL)

        if next_state == EndState.STATE_LABEL:
            return hangouts.generate_edit_work_item(work_item)

        return hangouts.text_format("Please describe your issue.")

    @staticmethod
    def where():
        return "You're on `Title`. Please enter issue Title."


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
            return hangouts.generate_edit_work_item(work_item)
        elif next_state == HardwareChoice.STATE_LABEL:
            hardware_type = ["Internet/Wifi", "Laptop/Computer", "Mobile Device", "Other", "Printer"]
            return hangouts.generate_choices("Choose Hardware Type", hardware_type, "hardware_type")
        elif next_state == SoftwareChoice.STATE_LABEL:
            third_party = ["GSuite", "Power BI", "VSTS", "Fill your own.."]
            return hangouts.generate_choices("Choose 3rd Party Software", third_party, "software_type")

    @staticmethod
    def where():
        return "You're on `Description`. Please describe your issue."


class HardwareChoice(ChoiceState):
    STATE_LABEL = "hardware_type"

    @staticmethod
    def action(message, event):
        hangouts.delete_message(event['message']['name'])

        user_object = User.objects.get(name=event['space']['name'])

        work_item = user_object.get_work_item()
        work_item.hardware_type = message
        work_item.save()

        next_state = change_state(user_object, SeverityChoice.STATE_LABEL)

        if next_state == EndState.STATE_LABEL:
            return hangouts.generate_edit_work_item(work_item)

        severities = ["1 - Critical", "2 - High", "3 - Medium", "4 - Low"]
        return hangouts.generate_choices("How severe is this issue?", severities, "severity")

    @staticmethod
    def where():
        return "You're on `Choose Hardware`. Please select one Hardware Type that is being issued from the card above."


class SoftwareChoice(ChoiceState):
    STATE_LABEL = "software_type"

    @staticmethod
    def action(message, event):
        hangouts.delete_message(event['message']['name'])

        user_object = User.objects.get(name=event['space']['name'])
        work_item = user_object.get_work_item()
        user_email = str(event['user']['email'])
        user_email = user_email.split("@")[0] + '@staff.gramedia.com'
        work_item.requested_by = user_email

        if message == "Fill your own..":
            work_item.save()
            user_object.state = OtherSoftwareType.STATE_LABEL
            user_object.save()
            return hangouts.text_format("Please enter your own software type")

        work_item.third_party = message
        work_item.save()

        next_state = change_state(user_object, SeverityChoice.STATE_LABEL)

        if next_state == EndState.STATE_LABEL:
            return hangouts.generate_edit_work_item(work_item)

        severities = ["1 - Critical", "2 - High", "3 - Medium", "4 - Low"]
        return hangouts.generate_choices("How severe is this issue?", severities, "severity")

    @staticmethod
    def where():
        return "You're on `Choose Software`. Please select 3rd Party App that is being issued from the card above."


class OtherSoftwareType(State):
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

        next_state = change_state(user_object, SeverityChoice.STATE_LABEL)

        if next_state == EndState.STATE_LABEL:
            return hangouts.generate_edit_work_item(work_item)

        severities = ["1 - Critical", "2 - High", "3 - Medium", "4 - Low"]
        return hangouts.generate_choices("How severe is this issue?", severities, "severity")

    @staticmethod
    def where():
        return "You're on `Custom Software Type`. Please enter your own desired 3rd party software."


class SeverityChoice(ChoiceState):
    STATE_LABEL = "severity"

    @staticmethod
    def action(message, event):
        hangouts.delete_message(event['message']['name'])

        user_object = User.objects.get(name=event['space']['name'])

        work_item = user_object.get_work_item()
        work_item.severity = message
        work_item.save()

        change_state(user_object, EndState.STATE_LABEL)
        return hangouts.generate_edit_work_item(work_item)

    @staticmethod
    def where():
        return "You're on `Choose Severity`. Please select this issue's severity level from the card above."


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
            fields_dict = hangouts.generate_fields_dict(work_item)

            work_item_dict = {}

            for key, value in path_dict.items():
                work_item_dict[value] = fields_dict[key]

            vsts.create_work_item(work_item_dict, work_item.url, user_object)
            print(work_item_dict)

            change_state(user_object, InitialState.STATE_LABEL)
            work_item.delete()

            return hangouts.text_format("Your work item has been saved.")

        elif message == "Title":
            user_object.state = TitleState.STATE_LABEL
            user_object.save()

            return hangouts.text_format("Please enter your issue Title.")

        elif message == "Description":
            user_object.state = DescriptionState.STATE_LABEL
            user_object.save()

            return hangouts.text_format("Please describe your issue.")

        elif message == "Hardware Type":
            user_object.state = HardwareChoice.STATE_LABEL
            user_object.save()

            hardware_type = ["Internet/Wifi", "Laptop/Computer", "Mobile Device", "Other", "Printer"]
            return hangouts.generate_choices("Choose Hardware Type", hardware_type, "hardware_type")

        elif message == "Severity":
            user_object.state = SeverityChoice.STATE_LABEL
            user_object.save()

            severities = ["1 - Critical", "2 - High", "3 - Medium", "4 - Low"]
            return hangouts.generate_choices("How severe is this issue?", severities, "severity")

        elif message == "Third Party":
            user_object.state = SoftwareChoice.STATE_LABEL
            user_object.save()

            third_party = ["GSuite", "Power BI", "VSTS", "Fill your own.."]
            return hangouts.generate_choices("Choose 3rd Party Software", third_party, "software_type")

    @staticmethod
    def where():
        return "You're near the finish line. Please evaluate your issue at the card above and click" \
               " `save` when you're done."


states_list = {InitialState.STATE_LABEL: InitialState, ChoiceState.STATE_LABEL: ChoiceState,
               TitleState.STATE_LABEL: TitleState, DescriptionState.STATE_LABEL: DescriptionState,
               HardwareChoice.STATE_LABEL: HardwareChoice, SoftwareChoice.STATE_LABEL: SoftwareChoice,
               OtherSoftwareType.STATE_LABEL: OtherSoftwareType, SeverityChoice.STATE_LABEL: SeverityChoice,
               EndState.STATE_LABEL: EndState}
