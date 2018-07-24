from .models import *
import abc
import hangouts.views
import vsts.views


def change_state(space_name):
    user_object = User.objects.get(name=space_name)
    current_state = states_list[user_object.state]
    print("current state: " + current_state.STATE_LABEL)
    next_state = current_state.next_state(space_name)
    print("next state:")
    print(next_state)
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


class InitialState(State):
    STATE_LABEL = "initial"

    @staticmethod
    def action(message, event):
        if message.lower() == 'support':
            response = hangouts.views.generate_choices("Choose work item type", ["Hardware Support", "Software Support"],
                                        "choose_type")
            change_state(event['space']['name'])
        else:
            message = 'You said: `%s`' % message
            response = hangouts.views.text_format(message)

        return response

    @staticmethod
    def is_waiting_text():
        return True

    @staticmethod
    def next_state(*args):
        return ChoiceState.STATE_LABEL


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
        return hangouts.views.text_format("You've chosen '%s'\nPlease enter title" % message)

    @staticmethod
    def next_state(*args):
        return TitleState.STATE_LABEL


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
        # hardware_type = ["Internet/Wifi", "Laptop/Computer", "Mobile Device", "Other", "Printer"]
        # response = generate_choices("Choose Hardware Type", hardware_type, "hardware_type")

        return hangouts.views.text_format("Please enter description")

    @staticmethod
    def next_state(*args):
        return DescriptionState.STATE_LABEL


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
            response = hangouts.views.generate_choices("Choose Hardware Type", hardware_type, "hardware_type")
        elif next_state == SoftwareChoice.STATE_LABEL:
            third_party = ["GSuite", "Power BI", "VSTS"]
            response = hangouts.views.generate_choices("Choose 3rd Party Software", third_party, "software_type")

        return response

    @staticmethod
    def next_state(*args):
        user_object = User.objects.get(name=args[0])
        work_item = user_object.work_item
        if isinstance(work_item, HardwareSupport):
            return HardwareChoice.STATE_LABEL
        elif isinstance(work_item, SoftwareSupport):
            return SoftwareChoice.STATE_LABEL


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
        response = hangouts.views.generate_choices("How severe is this issue?", severities, "severity")
        return response

    @staticmethod
    def next_state(*args):
        return SeverityChoice.STATE_LABEL


class SoftwareChoice(ChoiceState):
    STATE_LABEL = "software_type"

    @staticmethod
    def action(message, event):
        user_object = User.objects.get(name=event['space']['name'])

        work_item = user_object.work_item
        work_item.third_party = message
        user_email = str(event['message']['sender']['email'])
        user_email = user_email.split("@")[0] + 'staff.gramedia.com'
        work_item.requested_by = user_email
        work_item.save()

        change_state(event['space']['name'])
        severities = ["1 - Critical", "2 - High", "3 - Medium", "4 - Low"]
        response = hangouts.views.generate_choices("How severe is this issue?", severities, "severity")
        return response

    @staticmethod
    def next_state(*args):
        return SeverityChoice.STATE_LABEL


class SeverityChoice(ChoiceState):
    STATE_LABEL = "severity"

    @staticmethod
    def action(message, event):
        user_object = User.objects.get(name=event['space']['name'])

        work_item = user_object.work_item
        work_item.severity = message
        work_item.save()

        change_state(event['space']['name'])
        response = hangouts.views.generate_edit_work_item(work_item)
        return response

    @staticmethod
    def next_state(*args):
        return EndState.STATE_LABEL


class EndState(ChoiceState):
    STATE_LABEL = "end"

    @staticmethod
    def action(message, event):
        if message == "save":
            user_object = User.objects.get(name=event['space']['name'])
            work_item = user_object.work_item

            path_dict = work_item.path_dict
            fields_dict = hangouts.views.generate_fields_dict(work_item)

            work_item_dict = {}

            for key, value in path_dict.items():
                work_item_dict[value] = fields_dict[key]

            vsts.views.create_work_item(work_item_dict)
            print(work_item_dict)

            change_state(event['space']['name'])
            response = hangouts.views.text_format("Your work item has been saved.")
        else:
            response = hangouts.views.text_format("Gimana hayo")

        return response

    @staticmethod
    def next_state(*args):
        return InitialState.STATE_LABEL


states_list = {InitialState.STATE_LABEL: InitialState, ChoiceState.STATE_LABEL: ChoiceState,
               TitleState.STATE_LABEL: TitleState, DescriptionState.STATE_LABEL: DescriptionState,
               HardwareChoice.STATE_LABEL: HardwareChoice, SoftwareChoice.STATE_LABEL: SoftwareChoice,
               SeverityChoice.STATE_LABEL: SeverityChoice, EndState.STATE_LABEL: EndState}
