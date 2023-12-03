#!python3


from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: snipeit_catagory 

short_description: This creates/manages categories in SnipeIT

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: This module allows you to create categories in SnipeIT

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
        description: >
            The name of the category. Only when combined with a category_type, this is the unique identifier for the category.
            It does NOT need to be unique across different category types, it only must be unique in its category type. 
        required: true
        type: str
    category_type:
       description: The type of category. This can be one of ["asset", "accessory", "consumable", "component"]
       required: true
       type: str

author:
    - Daniel Podwysocki (@danielpodwysocki)
"""

EXAMPLES = r"""

- name: Create a new category
    danielpodwysocki.snipeit_category:
        api_key: "API_KEY"
        snipe_url: "https://snipeit.example.com"
        name: "my_category"
        category_type: "asset"
"""

RETURN = r"""
# These are examples of possible return values, and in general should use other names for return values.

category_id:
  description: The ID of the category that was created
  type: int
  returned: always


"""


import json

import requests

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.snipeit import get_category


def create_category(
    snipe_url: str,
    api_key: str,
    name: str,
    category_type: str,
    module: AnsibleModule,
    dry_run: bool,
) -> bool:
    """Create a new category in SnipeIT. Return False if it already exists

    :param snipe_url: The URL of the SnipeIT instance
    :param api_key: The API key to use to authenticate to SnipeIT
    :param name: The name of the category to create
    :param category_type: The type of category to create. This can be one of ["asset", "accessory", "consumable", "component"]
    :param module: The AnsibleModule object
    :param dry_run: If True, don't actually create the category.
    :return: True if the category was created, False if it already exists. In dry-run mode, return True if it would have been created and False otherwise.
    """
    category = get_category(snipe_url, api_key, name, category_type)
    if category:
        return False
    if not category and dry_run:
        return True
    payload = {
        "name": name,
        "category_type": category_type,
    }
    response = requests.post(
        f"{snipe_url.rstrip('/')}/api/v1/categories",
        json=payload,
        headers={"Authorization": f"Bearer {api_key}"},
    )
    data = json.loads(response.text)
    if data["status"] == "error":
        module.fail_json(msg=f"Error creating category: {data['messages']}")
    return True


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = {
        "snipe_url": {"type": "str", "required": True},
        "api_key": {"type": "str", "required": True, "no_log": True},
        "name": {"type": "str", "required": True},
        "category_type": {
            "type": "str",
            "required": True,
            "choices": ["asset", "accessory", "consumable", "component"],
        },
    }

    result = {"changed": False}

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    changed = False
    changed = create_category(
        module.params["snipe_url"],
        module.params["api_key"],
        module.params["name"],
        module.params["category_type"],
        module,
        dry_run=False,
    )

    result["changed"] = changed
    # if we supported deleting categories, we'd need to account for that here
    result["category_id"] = get_category(
        module.params["snipe_url"],
        module.params["api_key"],
        module.params["name"],
        module.params["category_type"],
    )["id"]

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
