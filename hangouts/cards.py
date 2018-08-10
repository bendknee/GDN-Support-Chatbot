from django.contrib.staticfiles.templatetags.staticfiles import static
from django.forms.models import model_to_dict


def text_format(message):
    return {"text": message}

# ----------------------- card generators -----------------------#
def generate_card_layout(num_of_sections):
    card = {
        "cards": [
            {
                "sections": [
                ]
            },
            {
                "header": {
                    "title": "Pizza Bot Customer Support",
                    "subtitle": "pizzabot@example.com",
                    "imageUrl": "https://goo.gl/aeDtrS",
                    "imageStyle": "IMAGE"
                  },
            }
        ]
    }

    for i in range(num_of_sections):
        section = {
            "widgets": [
            ]
        }

        card['cards'][0]['sections'].append(section)

    return card


def generate_choices(title, choices, method):
    card = generate_card_layout(1)

    # add widgets
    header = {
        "title": title
    }

    card['cards'][0]['header'] = header  # bisa gak nih

    for item in choices:
        item_widget = {
            "keyValue": {
                "content": item,
                "onClick": {
                    "action": {
                        "actionMethodName": method,
                        "parameters": [
                            {
                                "key": "param",
                                "value": item
                            }
                        ]
                    }
                }
            }
        }

        card['cards'][0]['sections'][0]['widgets'].append(item_widget)

    return card

def generate_work_item(work_item):
    card = generate_card_layout(3)
    print("three sections")
    print(card)

    # remove fields that does not need to be displayed
    temp_dict = generate_fields_dict(work_item)

    del temp_dict["title"]
    del temp_dict["saved_url"]
    if "requested_by" in temp_dict:
        del temp_dict["requested_by"]

    # capitalize field names
    work_item_dict = {}

    for old_key in temp_dict.keys():
        new_key = old_key.replace("_", " ").title()
        work_item_dict[new_key] = temp_dict[old_key]

    # add widgets
    title_widget = {
        "keyValue": {
            "content": work_item.title,
            "iconUrl": "http://hangouts-vsts.herokuapp.com" +
                       static('png/' + work_item.url + '.png')
        }
    }

    print(card['cards'][0]['sections'][0]['widgets'])
    card['cards'][0]['sections'][0]['widgets'].append(title_widget)

    return card, work_item_dict

def generate_edit_work_item(work_item, state):
    card, work_item_dict = generate_work_item(work_item)
    print("card before")
    print(card)

    # add widgets
    edit_title_button = {
        "textButton": {
            "text": "Edit",
            "onClick": {
                "action": {
                    "actionMethodName": state,
                    "parameters": [
                        {
                            "key": "field",
                            "value": "Title"
                        }
                    ]
                }
            }

        }
    }

    buttons_widget = {
        "buttons": [
            {
                "textButton": {
                    "text": "SAVE",
                    "onClick": {
                        "action": {
                            "actionMethodName": state,
                            "parameters": [
                                {
                                    "key": "field",
                                    "value": "save"
                                }
                            ]
                        }
                    }
                }
            }
        ]
    }

    card['cards'][0]['sections'][0]['widgets'][0]['keyValue']['button'] = edit_title_button
    print("card now")
    print(card)
    card['cards'][0]['sections'][2]['widgets'].append(buttons_widget)


    for label, content in work_item_dict.items():
        field_widget = {
            "keyValue": {
                "topLabel": label,
                "content": content,
                "button": {
                    "textButton": {
                        "text": "Edit",
                        "onClick": {
                            "action": {
                                "actionMethodName": state,
                                "parameters": [
                                    {
                                        "key": "field",
                                        "value": label
                                    }
                                ]
                            }
                        }

                    }
                }
            }
        }

        card['cards'][0]['sections'][1]['widgets'].append(field_widget)

    return card

def generate_saved_work_item(work_item):
    card, work_item_dict = generate_work_item(work_item)

    # add widgets
    buttons_widget = {
        "buttons": [
            {
                "textButton": {
                    "text": "MORE",
                    "onClick": {
                        "openLink": {
                            "url": work_item.saved_url
                        }
                    }
                }
            }
        ]
    }

    card['cards'][0]['sections'][2]['widgets'].append(buttons_widget)

    for label, content in work_item_dict.items():
        field_widget = {
            "keyValue": {
                "topLabel": label,
                "content": content,
            }
        }

        card['cards'][0]['sections'][1]['widgets'].append(field_widget)

    return card

def generate_updated_work_item(work_item):
    card = generate_card_layout(3)

    fields = {'Revised by': work_item['revisedBy']['name']}

    image_url = "http://hangouts-vsts.herokuapp.com" + static('png/' +
                                                              work_item['revision']['fields'][
                                                                  'System.WorkItemType'].replace(" ", "%20") + '.png')

    if 'System.State' in work_item['fields']:
        fields['State'] = work_item['fields']['System.State']['oldValue'] + \
                          ' --> ' + work_item['fields']['System.State']['newValue']

    if 'System.History' in work_item['fields']:
        fields['Comment'] = work_item['fields']['System.History']['newValue']

    # add widgets
    title_widget = {
        "keyValue": {
            "content": work_item['revision']['fields']['System.Title'],
            "iconUrl": image_url
        }
    }

    buttons_widget = {
        "buttons": [
            {
                "textButton": {
                    "text": "MORE",
                    "onClick": {
                        "openLink": {
                            "url": work_item['_links']['html']['href']
                        }
                    }
                }
            }
        ]
    }

    card['cards'][0]['sections'][0]['widgets'].append(title_widget)
    card['cards'][0]['sections'][2]['widgets'].append(buttons_widget)

    for label, content in fields.items():
        item_widget = {
            "keyValue": {
                "topLabel": label,
                "content": content
            }
        }

        card['cards'][0]['sections'][1]['widgets'].append(item_widget)

    return card

def generate_signin_card(user):
    signin_url = "app.vssps.visualstudio.com/oauth2/authorize?client_id=C8A33DD9-D575-428F-A0CA-7210BC9A4363&" \
                 "response_type=Assertion&state=" + str(user.pk) + "&scope=vso.work_full&redirect_" \
                                                                   "uri=https://hangouts-vsts.herokuapp.com/vsts/oauth"

    card = generate_card_layout(1)

    header = {
        "title": "Please sign in to your VSTS account."
    }

    card['cards'][0]['header'] = header # bisa gak nih

    # add widgets
    buttons_widget = {
        "buttons": [
            {
                "textButton": {
                    "text": "SIGN IN",
                    "onClick": {
                        "openLink": {
                            "url": signin_url
                        }
                    }
                }
            }
        ]
    }

    card['cards'][0]['sections'][0]['widgets'].append(buttons_widget)

    return card


def generate_fields_dict(work_item):
    dict = model_to_dict(work_item)

    del dict["id"]
    del dict["workitem_ptr"]

    return dict