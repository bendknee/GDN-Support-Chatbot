from . import DescriptionState, EndState, HardwareChoice, InitialState, ItemTypeState, OtherSoftwareType, \
    SeverityChoice, SoftwareChoice, TitleState


states_list = {InitialState.STATE_LABEL: InitialState,
               ItemTypeState.STATE_LABEL: ItemTypeState,
               TitleState.STATE_LABEL: TitleState,
               DescriptionState.STATE_LABEL: DescriptionState,
               HardwareChoice.STATE_LABEL: HardwareChoice,
               SoftwareChoice.STATE_LABEL: SoftwareChoice,
               OtherSoftwareType.STATE_LABEL: OtherSoftwareType,
               SeverityChoice.STATE_LABEL: SeverityChoice,
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
