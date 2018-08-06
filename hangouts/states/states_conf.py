from . import description_state, end_state, hardware_choice, initial_state, item_type_state, other_software_type, \
    severity_choice, software_choice, title_state


states_list = {initial_state.InitialState.STATE_LABEL: initial_state.InitialState,
               item_type_state.ItemTypeState.STATE_LABEL: item_type_state.ItemTypeState,
               title_state.TitleState.STATE_LABEL: title_state.TitleState,
               description_state.DescriptionState.STATE_LABEL: description_state.DescriptionState,
               hardware_choice.HardwareChoice.STATE_LABEL: hardware_choice.HardwareChoice,
               software_choice.SoftwareChoice.STATE_LABEL: software_choice.SoftwareChoice,
               other_software_type.OtherSoftwareType.STATE_LABEL: other_software_type.OtherSoftwareType,
               severity_choice.SeverityChoice.STATE_LABEL: severity_choice.SeverityChoice,
               end_state.EndState.STATE_LABEL: end_state.EndState}


def change_state(user_object, next_state):
    current_state = states_list[user_object.state]

    if user_object.is_finished:
        next_state = end_state.EndState.STATE_LABEL

    print("current state: " + current_state.STATE_LABEL)
    print("next state: " + next_state)

    user_object.state = next_state
    user_object.save()
    return next_state
