from hangouts import views
from hangouts.states import EndState, SeverityChoice, change_state, State


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
            return views.generate_edit_work_item(work_item)

        return views.generate_choices("How severe is this issue?", work_item.severities_list, SeverityChoice.STATE_LABEL)

    @staticmethod
    def where():
        return "You're on `Custom Software Type`. Please enter your own desired 3rd party software."
