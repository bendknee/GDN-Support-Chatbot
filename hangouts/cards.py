from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static

from hangouts.helpers import generate_fields_dict, create_url_of_work_item


def text_format(message):
    return {"text": message}


# ----------------------- card template generators -----------------------#
def generate_card_layout(num_of_sections):
    card = {
        "cards": [
            {
                "sections": [
                ]
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


# update card after CARD CLICKED event
def generate_update_response(response):
    response["actionResponse"] = {"type": "UPDATE_MESSAGE"}

    return response


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

    # remove fields that does not need to be displayed
    temp_dict = generate_fields_dict(work_item)
    del temp_dict["title"]

    # capitalize field names
    work_item_dict = {}

    for old_key in temp_dict.keys():
        new_key = old_key.replace("_", " ").title()
        work_item_dict[new_key] = temp_dict[old_key]

    # add widgets
    title_widget = {
        "keyValue": {
            "content": work_item.title,
            "iconUrl": settings.WEBHOOK_URL +
                       static('png/' + create_url_of_work_item(work_item) + '.png')
        }
    }

    card['cards'][0]['sections'][0]['widgets'].append(title_widget)

    return card, work_item_dict


def generate_edit_work_item(work_item, state):
    card, work_item_dict = generate_work_item(work_item)

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


def generate_saved_work_item(work_item, url_href):
    card, work_item_dict = generate_work_item(work_item)

    # add widgets
    buttons_widget = {
        "buttons": [
            {
                "textButton": {
                    "text": "MORE",
                    "onClick": {
                        "openLink": {
                            "url": url_href
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

    image_url = settings.WEBHOOK_URL + static('png/' +
                                              work_item['revision']['fields'][
                                                  'System.WorkItemType'].replace(" ", "%20") + '.png')

    if 'System.State' in work_item['fields']:
        fields['State'] = work_item['fields']['System.State']['oldValue'] + \
                          ' --> ' + work_item['fields']['System.State']['newValue']

    if 'System.History' in work_item['fields']:
        fields['Comment'] = work_item['fields']['System.History']['newValue']

    if 'System.AssignedTo' in work_item['fields']:
        fields['Assigned To'] = work_item['fields']['System.AssignedTo']['newValue']

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
    signin_url = "app.vssps.visualstudio.com/oauth2/authorize?client_id=" + settings.VSTS_OAUTH_ID + \
                 "&response_type=Assertion&state=" + str(user.pk) + "&scope=vso.work_full&redirect_" \
                                                                   "uri=" + settings.WEBHOOK_URL + "/api/vsts/oauth/"

    card = generate_card_layout(1)

    header = {
        "title": "Please sign in to your VSTS account."
    }

    card['cards'][0]['header'] = header  # bisa gak nih

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
