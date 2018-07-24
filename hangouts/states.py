from .views import *
import abc
from .models import *


def change_state(space_name):
    user_object = User.objects.get(name=space_name)
    current_state = states_list[user_object.state]
    next_state = current_state.next_state(space_name)
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
    def next_state(*args):
        pass

    @staticmethod
    @abc.abstractmethod
    def where():
        pass


class InitialState(State):
    STATE_LABEL = "initial"

    @staticmethod
    def action(message, event):
        if message.lower() == 'support':
            response = generate_choices("Choose work item type", ["Hardware Support", "Software Support"],
                                        "choose_type")
            change_state(event['space']['name'])
        else:
            message = 'You said: `%s`' % message
            response = text_format(message)

        return response

    @staticmethod
    def is_waiting_text():
        return True

    @staticmethod
    def next_state(*args):
        return ChoiceState.STATE_LABEL

    @staticmethod
    def where():
        return "You're nowhere. Type '%s' to begin issuing new Work Item." % 'support'


class ChoiceState(State):
    STATE_LABEL = "choice"

    @staticmethod
    def is_waiting_text():
        return False

    @staticmethod
    def action(message, event):
        user_object = User.objects.get(name=event['space']['name'])
        if message == 'Hardware Support':
            work_item_object = HardwareSupport.objects.create()
        elif message == 'Software Support':
            work_item_object = SoftwareSupport.objects.create()

        user_object.work_item = work_item_object
        user_object.save()
        return text_format("You've chosen '%s'\nPlease enter your issue Title." % message)

    @staticmethod
    def next_state(*args):
        return TitleState.STATE_LABEL

    @staticmethod
    def where():
        return "You're on Choose Type. Please pick desired work item Type from the card above."


class TitleState(State):
    STATE_LABEL = "title"

    @staticmethod
    def is_waiting_text():
        return True

    @staticmethod
    def action(message, event):
        user_object = User.objects.get(name=event['space']['name'])

        work_item = user_object.work_item
        work_item.title = message
        work_item.save()

        change_state(event['space']['name'])
        return text_format("Please describe your issue.")

    @staticmethod
    def next_state(*args):
        return DescriptionState.STATE_LABEL

    @staticmethod
    def where():
        return "You're on Title. Please enter issue Title."


class DescriptionState(State):
    STATE_LABEL = "description"

    @staticmethod
    def is_waiting_text():
        return True

    @staticmethod
    def action(message, event):
        user_object = User.objects.get(name=event['space']['name'])

        work_item = user_object.work_item
        work_item.description = message
        work_item.save()

        next_state = change_state(event['space']['name'])

        if next_state == HardwareChoice.STATE_LABEL:
            hardware_type = ["Internet/Wifi", "Laptop/Computer", "Mobile Device", "Other", "Printer"]
            response = generate_choices("Choose Hardware Type", hardware_type, "hardware_type")
        elif next_state == SoftwareChoice.STATE_LABEL:
            third_party = ["GSuite", "Power BI", "VSTS"]
            response = generate_choices("Choose 3rd Party Software", third_party, "software_type")

        return response

    @staticmethod
    def next_state(*args):
        user_object = User.objects.get(name=args[0])
        work_item = user_object.work_item
        if isinstance(work_item, HardwareSupport):
            return HardwareChoice.STATE_LABEL
        elif isinstance(work_item, SoftwareSupport):
            return SoftwareChoice.STATE_LABEL

    @staticmethod
    def where():
        return "You're on Description. Please describe your issue."


class HardwareChoice(ChoiceState):
    STATE_LABEL = "hardware_type"

    @staticmethod
    def action(message, event):
        user_object = User.objects.get(name=event['space']['name'])

        work_item = user_object.work_item
        work_item.hardware_type = message
        work_item.save()

        change_state(event['space']['name'])
        severities = ["1 - Critical", "2 - High", "3 - Medium", "4 - Low"]
        response = generate_choices("How severe is this issue?", severities, "severity")
        return response

    @staticmethod
    def next_state(*args):
        return SeverityChoice.STATE_LABEL

    @staticmethod
    def where():
        return "You're on Choose Hardware. Please select one Hardware Type that is being issued from the card above."


class SoftwareChoice(ChoiceState):
    STATE_LABEL = "software_type"

    @staticmethod
    def action(message, event):
        user_object = User.objects.get(name=event['space']['name'])

        work_item = user_object.work_item
        work_item.third_party = message
        user_email = str(event['message']['sender']['email'])
        user_email = user_email.split("@")[0] + '@staff.gramedia.com'
        work_item.requested_by = user_email
        work_item.save()

        change_state(event['space']['name'])
        severities = ["1 - Critical", "2 - High", "3 - Medium", "4 - Low"]
        response = generate_choices("How severe is this issue?", severities, "severity")
        return response

    @staticmethod
    def next_state(*args):
        return SeverityChoice.STATE_LABEL

    @staticmethod
    def where():
        return "You're on Choose Software. Please select 3rd Party App that is being issued from the card above."


class SeverityChoice(ChoiceState):
    STATE_LABEL = "severity"

    @staticmethod
    def next_state(*args):
        return EndState.STATE_LABEL


class EndState(ChoiceState):
    STATE_LABEL = "end"

    @staticmethod
    def next_state(*args):
        return InitialState.STATE_LABEL


states_list = {InitialState.STATE_LABEL: InitialState, ChoiceState.STATE_LABEL: ChoiceState,
               TitleState.STATE_LABEL: TitleState, DescriptionState.STATE_LABEL: DescriptionState,
               HardwareChoice.STATE_LABEL: HardwareChoice, SoftwareChoice.STATE_LABEL: SoftwareChoice,
               SeverityChoice.STATE_LABEL: SeverityChoice, EndState.STATE_LABEL: EndState}
