from .state import State
from .choice_state import ChoiceState

from hangouts.cards import generate_edit_work_item, generate_choices, generate_fields_dict, generate_saved_work_item, text_format, generate_signin_card
from hangouts.models import HardwareSupport, SoftwareSupport

from vsts.views import create_work_item, token_expired_or_refresh

available_types = ["Hardware Support", "Software Support"]


def change_state(user_object, next_state):
    current_state = states_list[user_object.state]

    if user_object.is_finished:
        next_state = EndState.STATE_LABEL

    print("current state: " + current_state.STATE_LABEL)
    print("next state: " + next_state)

    user_object.state = next_state
    user_object.save()
    return next_state


class InitialState(State):
    STATE_LABEL = "initial"

    @staticmethod
    def is_waiting_text():
        return True

    @staticmethod
    def action(user_object, message, event):
        if message.lower() == 'support':
            if user_object.jwt_token is None:
                return generate_signin_card(user_object)
            else:
                token_expired_or_refresh(user_object)
                change_state(user_object, ItemTypeState.STATE_LABEL)
                return generate_choices("Choose work item type", available_types, ItemTypeState.STATE_LABEL)
        else:
            message = "I'm not sure what you mean. Type /help to see available commands."
            return text_format(message)

    @staticmethod
    def where():
        return "You're nowhere. Type `support` to begin issuing new Work Item."


class ItemTypeState(ChoiceState):
    STATE_LABEL = "item_type"

    @staticmethod
    def is_waiting_text():
        return False

    @staticmethod
    def action(user_object, message, event):
        # views.delete_message(event['message']['name'])

        if message == 'Hardware Support':
            work_item_object = HardwareSupport.objects.create()
        elif message == 'Software Support':
            work_item_object = SoftwareSupport.objects.create()

        user_object.work_item = work_item_object
        user_object.save()

        change_state(user_object, TitleState.STATE_LABEL)

        return text_format("You've chosen `%s`\n\nPlease enter your issue Title." % message)

    @staticmethod
    def where():
        return "You're on `Choose Type`. Please pick desired work item Type from the card above."


class TitleState(State):
    STATE_LABEL = "title"

    @staticmethod
    def is_waiting_text():
        return True

    @staticmethod
    def action(user_object, message, event):

        work_item = user_object.get_work_item()
        work_item.title = message
        work_item.save()

        next_state = change_state(user_object, DescriptionState.STATE_LABEL)

        if next_state == EndState.STATE_LABEL:
            return generate_edit_work_item(work_item)

        return text_format("Please describe your issue.")

    @staticmethod
    def where():
        return "You're on `Title`. Please enter issue Title."


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
            return generate_edit_work_item(work_item)
        elif next_state == HardwareChoice.STATE_LABEL:
            return generate_choices("Choose Hardware Type", work_item.hardware_list, "hardware_type")
        elif next_state == SoftwareChoice.STATE_LABEL:
            return generate_choices("Choose 3rd Party Software", work_item.software_list, "software_type")

    @staticmethod
    def where():
        return "You're on `Description`. Please describe your issue."


class HardwareChoice(ChoiceState):
    STATE_LABEL = "hardware_type"

    @staticmethod
    def action(user_object, message, event):
        # views.delete_message(event['message']['name'])

        work_item = user_object.get_work_item()
        work_item.hardware_type = message
        work_item.save()

        next_state = change_state(user_object, SeverityChoice.STATE_LABEL)

        if next_state == EndState.STATE_LABEL:
            return generate_edit_work_item(work_item)

        return generate_choices("How severe is this issue?", work_item.severities_list, SeverityChoice.STATE_LABEL)

    @staticmethod
    def where():
        return "You're on `Choose Hardware`. Please select one Hardware Type that is being issued from the card above."


class SoftwareChoice(ChoiceState):
    STATE_LABEL = "software_type"

    @staticmethod
    def action(user_object, message, event):
        # views.delete_message(event['message']['name'])

        work_item = user_object.get_work_item()
        user_email = str(event['user']['email'])
        user_email = user_email.split("@")[0] + '@staff.gramedia.com'
        work_item.requested_by = user_email

        if message == "Fill your own..":
            work_item.save()
            user_object.state = OtherSoftwareType.STATE_LABEL
            user_object.save()
            return text_format("Please enter your own software type")

        work_item.third_party = message
        work_item.save()

        next_state = change_state(user_object, SeverityChoice.STATE_LABEL)

        if next_state == EndState.STATE_LABEL:
            return generate_edit_work_item(work_item)

        return generate_choices("How severe is this issue?", work_item.severities_list, SeverityChoice.STATE_LABEL)

    @staticmethod
    def where():
        return "You're on `Choose Software`. Please select 3rd Party App that is being issued from the card above."


class OtherSoftwareType(State):
    STATE_LABEL = "other_software_type"

    @staticmethod
    def is_waiting_text():
        return True

    @staticmethod
    def action(user_object, message, event):

        work_item = user_object.get_work_item()
        work_item.third_party = message
        work_item.save()

        next_state = change_state(user_object, SeverityChoice.STATE_LABEL)

        if next_state == EndState.STATE_LABEL:
            return generate_edit_work_item(work_item)

        return generate_choices("How severe is this issue?", work_item.severities_list, SeverityChoice.STATE_LABEL)

    @staticmethod
    def where():
        return "You're on `Custom Software Type`. Please enter your own desired 3rd party software."


class SeverityChoice(ChoiceState):
    STATE_LABEL = "severity"

    @staticmethod
    def action(user_object, message, event):
        # views.delete_message(event['message']['name'])

        work_item = user_object.get_work_item()
        work_item.severity = message
        work_item.save()

        change_state(user_object, EndState.STATE_LABEL)
        return generate_edit_work_item(work_item)

    @staticmethod
    def where():
        return "You're on `Choose Severity`. Please select this issue's severity level from the card above."


class EndState(ChoiceState):
    STATE_LABEL = "end"

    @staticmethod
    def action(user_object, message, event):
        work_item = user_object.get_work_item()

        user_object.is_finished = True
        user_object.save()

        if message == "save":
            # views.delete_message(event['message']['name'])
            user_object.is_finished = False
            user_object.save()

            path_dict = work_item.path_dict
            fields_dict = generate_fields_dict(work_item)

            work_item_dict = {}

            for key, value in path_dict.items():
                work_item_dict[value] = fields_dict[key]

            req = create_work_item(work_item_dict, work_item.url, user_object)
            print(work_item_dict)
            print("req")
            print(req)

            work_item.saved_url = str(req['_links']['html']['href'])
            work_item.save()

            # body = views.generate_saved_work_item(work_item)
            # views.send_message(body, event['space']['name'])

            # text_response = views.text_format("Your work item has been saved.")
            # card_response = views.generate_work_item(work_item, req['_links']['html']['href'])
            # response = [text_response, card_response]

            # return response

            change_state(user_object, InitialState.STATE_LABEL)
            work_item.delete()

            return generate_saved_work_item(work_item)

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

            return generate_choices("Choose Hardware Type", work_item.hardware_list, HardwareChoice.STATE_LABEL)

        elif message == "Severity":
            user_object.state = SeverityChoice.STATE_LABEL
            user_object.save()

            return generate_choices("How severe is this issue?", work_item.severities_list,
                                          SeverityChoice.STATE_LABEL)

        elif message == "Third Party":
            user_object.state = SoftwareChoice.STATE_LABEL
            user_object.save()

            return generate_choices("Choose 3rd Party Software", work_item.software_list,
                                          SoftwareChoice.STATE_LABEL)

    @staticmethod
    def where():
        return "You're near the finish line. Please evaluate your issue at the card above and click" \
               " `save` when you're done."

states_list = {InitialState.STATE_LABEL: InitialState,
               ItemTypeState.STATE_LABEL: ItemTypeState,
               TitleState.STATE_LABEL: TitleState,
               DescriptionState.STATE_LABEL: DescriptionState,
               HardwareChoice.STATE_LABEL: HardwareChoice,
               SoftwareChoice.STATE_LABEL: SoftwareChoice,
               OtherSoftwareType.STATE_LABEL: OtherSoftwareType,
               SeverityChoice.STATE_LABEL: SeverityChoice,
               EndState.STATE_LABEL: EndState}