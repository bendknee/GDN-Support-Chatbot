from .description_state import DescriptionState
from .end_state import EndState
from .hardware_choice import HardwareChoice
from .initial_state import InitialState
from .item_type_state import ItemTypeState
from .other_software_type import OtherSoftwareType
from .severity_choice import SeverityChoice
from .software_choice import SoftwareChoice
from .title_state import TitleState


states_list = {InitialState.STATE_LABEL: InitialState, ItemTypeState.STATE_LABEL: ItemTypeState,
               TitleState.STATE_LABEL: TitleState, DescriptionState.STATE_LABEL: DescriptionState,
               HardwareChoice.STATE_LABEL: HardwareChoice, SoftwareChoice.STATE_LABEL: SoftwareChoice,
               OtherSoftwareType.STATE_LABEL: OtherSoftwareType, SeverityChoice.STATE_LABEL: SeverityChoice,
               EndState.STATE_LABEL: EndState}


def change_state(user_object, next_state):
    current_state = states_list[user_object.state]

    if user_object.is_finished:
        next_state = EndState.STATE_LABEL

    print("current state: " + current_state.STATE_LABEL)
    print("next state: " + next_state)

    user_object.state = next_state
    user_object.save()
    return next_state
