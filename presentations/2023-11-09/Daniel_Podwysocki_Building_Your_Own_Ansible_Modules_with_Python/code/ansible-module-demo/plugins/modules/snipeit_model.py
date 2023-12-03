#!python3


from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: snipeit_model

short_description: This creates/manages models in SnipeIT

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: This module allows you to create asset models in SnipeIT

options:
    api_key:
        description: The API key to use to authenticate to SnipeIT
        required: true
        type: str
    snipe_url:
        description: The URL of the SnipeIT instance
        required: true
        type: str
    name:
        description: The name of the model to create. Unique identifier for the model as far as we're concerned.
        required: true
        type: str
    category:
        description: The name of the category to use for the model. The type of the category must be "asset"!
        required: true
        type: int
    manufacturer_id:
        required: false
        description: The id of the manufacturer to use for the model. You can get this by using the snipeit_manufacturer module.
        type: int
    

author:
    - Daniel Podwysocki (@danielpodwysocki)
"""

EXAMPLES = r"""

- name: Create a new model
    danielpodwysocki.snipeit_category:
        api_key: "API_KEY"
        snipe_url: "https://snipeit.example.com"
        name: "my_model"
        category: server
        
"""

RETURN = r"""
# These are examples of possible return values, and in general should use other names for return values.


"""

import json

import requests

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.snipeit import get_category, get_model


# pylint: disable=too-many-arguments
def create_model(
    snipe_url: str,
    api_key: str,
    name: str,
    category_id: int,
    module: AnsibleModule,
    dry_run: bool,
    manufacturer_id: int = None,
) -> bool:
    """Create a new model in SnipeIT. Return False if it already exists, True if it was created

    :param snipe_url: The URL of the SnipeIT instance
    :param api_key: The API key to use to authenticate to SnipeIT
    :param name: The name of the model to create
    :param category_id: The ID of the category to use for the model. You can get this by using the snipeit_category module.
    :param manufacturer_id: The ID of the manufacturer to use for the model. You can get this by using the snipeit_manufacturer module.
    :param module: The AnsibleModule object
    :param dry_run: If True, don't actually create the model, but still return True if it would have been created
    :return: True if the model was created, False if it already exists
    """
    model = get_model(snipe_url, api_key, name, module)
    if model:
        return False
    if not model and dry_run:
        return True
    payload = {
        "name": name,
        "category_id": category_id,
    }
    if manufacturer_id:
        payload["manufacturer_id"] = manufacturer_id
    response = requests.post(
        f"{snipe_url.rstrip('/')}/api/v1/models",
        json=payload,
        headers={"Authorization": f"Bearer {api_key}"},
    )
    data = json.loads(response.text)
    if data["status"] == "error":
        module.fail_json(msg=f"Error creating model: {data['messages']}")
    return True


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = {
        "snipe_url": {"type": "str", "required": True},
        "api_key": {"type": "str", "required": True, "no_log": True},
        "name": {"type": "str", "required": True},
        "category": {"type": "str", "required": True},
        "manufacturer_id": {"type": "int", "required": False},
        "dry_run": {"type": "bool", "required": False, "default": False},
    }

    result = {"changed": False}

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    category = get_category(
        module.params["snipe_url"],
        module.params["api_key"],
        module.params["category"],
        "asset",
    )
    if not category:
        module.fail_json(msg=f"Category {module.params['category']} not found!")
    category_id = category["id"]

    changed = False
    changed = create_model(
        module.params["snipe_url"],
        module.params["api_key"],
        module.params["name"],
        category_id,
        module,
        module.params["dry_run"],
        manufacturer_id=module.params["manufacturer_id"],
    )

    result["changed"] = changed

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
