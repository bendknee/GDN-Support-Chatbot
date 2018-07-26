from .models import *
import abc
import hangouts.views
import vsts.views


def change_state(space_name):
    user_object = User.objects.get(name=space_name)
    current_state = states_list[user_object.state]

    if user_object.final:
        next_state = EndState.STATE_LABEL
    else:
        next_state = current_state.next_state(space_name)

    print("current state: " + current_state.STATE_LABEL)
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

    @staticmethod
    @abc.abstractmethod
    def where():
        pass


class InitialState(State):
    STATE_LABEL = "initial"

    @staticmethod
    def action(message, event):
        if message.lower() == 'support':
            change_state(event['space']['name'])
            return hangouts.views.generate_choices("Choose work item type",
                                                   ["Hardware Support", "Software Support"], "choose_type")
        else:
            message = 'You said: `%s`' % message
            return hangouts.views.text_format(message)

    @staticmethod
    def is_waiting_text():
        return True

    @staticmethod
    def next_state(*args):
        return ChoiceState.STATE_LABEL

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
        user_object = User.objects.get(name=event['space']['name'])
        if message == 'Hardware Support':
            work_item_object = HardwareSupport.objects.create()
        elif message == 'Software Support':
            work_item_object = SoftwareSupport.objects.create()

        user_object.work_item = work_item_object
        user_object.save()

        change_state(event['space']['name'])

        return hangouts.views.text_format("You've chosen `%s`\n\nPlease enter your issue Title." % message)

    @staticmethod
    def next_state(*args):
        return TitleState.STATE_LABEL

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

        next_state = change_state(event['space']['name'])

        if next_state == EndState.STATE_LABEL:
            return hangouts.views.generate_edit_work_item(work_item)

        return hangouts.views.text_format("Please describe your issue.")

    @staticmethod
    def next_state(*args):
        return DescriptionState.STATE_LABEL

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
        user_email = str(event['message']['sender']['email'])
        user_email = user_email.split("@")[0] + '@staff.gramedia.com'
        message += "\n\n- Issued by %s via GDN's Hangouts Chat bot" % user_email
        work_item.description = message
        work_item.save()

        next_state = change_state(event['space']['name'])

        if next_state == HardwareChoice.STATE_LABEL:
            hardware_type = ["Internet/Wifi", "Laptop/Computer", "Mobile Device", "Other", "Printer"]
            return hangouts.views.generate_choices("Choose Hardware Type", hardware_type, "hardware_type")
        elif next_state == SoftwareChoice.STATE_LABEL:
            third_party = ["GSuite", "Power BI", "VSTS"]
            return hangouts.views.generate_choices("Choose 3rd Party Software", third_party, "software_type")
        elif next_state == EndState.STATE_LABEL:
            return hangouts.views.generate_edit_work_item(work_item)

    @staticmethod
    def next_state(*args):
        user_object = User.objects.get(name=args[0])
        work_item = user_object.get_work_item()
        if isinstance(work_item, HardwareSupport):
            return HardwareChoice.STATE_LABEL
        elif isinstance(work_item, SoftwareSupport):
            return SoftwareChoice.STATE_LABEL

    @staticmethod
    def where():
        return "You're on `Description`. Please describe your issue."


class HardwareChoice(ChoiceState):
    STATE_LABEL = "hardware_type"

    @staticmethod
    def action(message, event):
        user_object = User.objects.get(name=event['space']['name'])

        work_item = user_object.get_work_item()
        work_item.hardware_type = message
        work_item.save()

        next_state = change_state(event['space']['name'])

        if next_state == EndState.STATE_LABEL:
            return hangouts.views.generate_edit_work_item(work_item)

        severities = ["1 - Critical", "2 - High", "3 - Medium", "4 - Low"]
        return hangouts.views.generate_choices("How severe is this issue?", severities, "severity")

    @staticmethod
    def next_state(*args):
        return SeverityChoice.STATE_LABEL

    @staticmethod
    def where():
        return "You're on `Choose Hardware`. Please select one Hardware Type that is being issued from the card above."


class SoftwareChoice(ChoiceState):
    STATE_LABEL = "software_type"

    @staticmethod
    def action(message, event):
        user_object = User.objects.get(name=event['space']['name'])

        work_item = user_object.get_work_item()
        work_item.third_party = message
        user_email = str(event['message']['sender']['email'])
        user_email = user_email.split("@")[0] + '@staff.gramedia.com'
        work_item.requested_by = user_email
        work_item.save()

        next_state = change_state(event['space']['name'])

        if next_state == EndState.STATE_LABEL:
            return hangouts.views.generate_edit_work_item(work_item)

        severities = ["1 - Critical", "2 - High", "3 - Medium", "4 - Low"]
        return hangouts.views.generate_choices("How severe is this issue?", severities, "severity")

    @staticmethod
    def next_state(*args):
        return SeverityChoice.STATE_LABEL

    @staticmethod
    def where():
        return "You're on `Choose Software`. Please select 3rd Party App that is being issued from the card above."


class SeverityChoice(ChoiceState):
    STATE_LABEL = "severity"

    @staticmethod
    def action(message, event):
        user_object = User.objects.get(name=event['space']['name'])

        work_item = user_object.get_work_item()
        work_item.severity = message
        work_item.save()

        change_state(event['space']['name'])
        return hangouts.views.generate_edit_work_item(work_item)

    @staticmethod
    def next_state(*args):
        return EndState.STATE_LABEL

    @staticmethod
    def where():
        return "You're on `Choose Severity`. Please select this issue's severity level from the card above."


class EndState(ChoiceState):
    STATE_LABEL = "end"

    @staticmethod
    def action(message, event):
        user_object = User.objects.get(name=event['space']['name'])
        work_item = user_object.get_work_item()

        user_object.final = True
        user_object.save()

        if message == "save":
            path_dict = work_item.path_dict
            fields_dict = hangouts.views.generate_fields_dict(work_item)

            work_item_dict = {}

            for key, value in path_dict.items():
                work_item_dict[value] = fields_dict[key]

            if isinstance(work_item, HardwareSupport):
                url = "Hardware%20Support"
            elif isinstance(work_item, SoftwareSupport):
                url = "Software%20Support"

            vsts.views.create_work_item(work_item_dict, url)
            print(work_item_dict)

            work_item.delete()

            return hangouts.views.text_format("Your work item has been saved.")

        elif message == "Title":
            user_object.state = TitleState.STATE_LABEL
            user_object.save()

            return hangouts.views.text_format("Please enter your issue Title.")

        elif message == "Description":
            user_object.state = DescriptionState.STATE_LABEL
            user_object.save()

            return hangouts.views.text_format("Please describe your issue.")

        elif message == "Hardware Type":
            user_object.state = HardwareChoice.STATE_LABEL
            user_object.save()

            hardware_type = ["Internet/Wifi", "Laptop/Computer", "Mobile Device", "Other", "Printer"]
            return hangouts.views.generate_choices("Choose Hardware Type", hardware_type, "hardware_type")

        elif message == "Severity":
            user_object.state = SeverityChoice.STATE_LABEL
            user_object.save()

            severities = ["1 - Critical", "2 - High", "3 - Medium", "4 - Low"]
            return hangouts.views.generate_choices("How severe is this issue?", severities, "severity")

    @staticmethod
    def next_state(*args):
        return InitialState.STATE_LABEL

    @staticmethod
    def where():
        return "You're near the finish line. Please evaluate your issue at the card above and click" \
               " <b>save</b> when you're done."


states_list = {InitialState.STATE_LABEL: InitialState, ChoiceState.STATE_LABEL: ChoiceState,
               TitleState.STATE_LABEL: TitleState, DescriptionState.STATE_LABEL: DescriptionState,
               HardwareChoice.STATE_LABEL: HardwareChoice, SoftwareChoice.STATE_LABEL: SoftwareChoice,
               SeverityChoice.STATE_LABEL: SeverityChoice, EndState.STATE_LABEL: EndState}
