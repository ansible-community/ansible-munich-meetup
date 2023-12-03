#!python3


from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: snipeit_entry

short_description: This creates/manages entries in SnipeIT

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: This module allows you to create inventory entries in SnipeIT

options:
    api_key:
        description: The API key to use to authenticate to SnipeIT
        required: true
        type: str
    snipe_url:
        description: The URL of the SnipeIT instance
        required: true
        type: str
    asset_tag:
        description: The asset tag to use for the entry. This is the unique identifier for the entry
        required: true
        type: str
    status_id:
        description: The status ID to use for the entry. Defaults to 2 (Ready to Deploy)
        required: true
        type: int
        default: 2
    model_name:
        description: >
          The name of the model to use for the entry. A fresh instance
          doesn't have any models defined, so you'll need to create one first.
        required: true
        type: int
    state:
        description: "present" or "absent" - "present" ensures the entry exists, "absent" ensures it doesn't
        required: false
        type: str
        default: present

author:
    - Daniel Podwysocki (@danielpodwysocki)
"""

EXAMPLES = r"""

# Create a new entry in SnipeIT
- name: Create a new entry in SnipeIT
    danielpodwysocki.snipeit_entry:
       asset_tag: example_asset001
       snipe_url: http://localhost:8080/
       api_key: 1234567890abcdef
       model_name: server
"""

RETURN = r"""
# These are examples of possible return values, and in general should use other names for return values.


"""


import json

import requests

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.snipeit import get_model, get_entry


def create_entry(
    snipe_url: str,
    api_key: str,
    asset_tag: str,
    status_id: int,
    model_id: int,
    module: AnsibleModule,
    dry_run: bool,
) -> bool:
    """Create a new entry in SnipeIT. Return False if it already exists

    :param snipe_url: The URL of the SnipeIT instance
    :param api_key: The API key to use to authenticate to SnipeIT
    :param asset_tag: The asset tag to use for the entry
    :param status_id: The status ID to use for the entry
    :param model_id: The model ID to use for the entry
    :param module:  The AnsibleModule object
    :param dry_run: If True, don't actually create the entry.
    :return: True if the entry was created, False if it already exists.
    In dry-run mode, return True if it would have been created and False otherwise.
    """
    entry = get_entry(snipe_url, api_key, asset_tag, module)
    if entry:
        return False
    if not entry and dry_run:
        return True
    payload = {
        "asset_tag": asset_tag,
        "status_id": status_id,
        "model_id": model_id,
    }
    response = requests.post(
        f"{snipe_url.rstrip('/')}/api/v1/hardware",
        json=payload,
        headers={"Authorization": f"Bearer {api_key}"},
    )
    data = json.loads(response.text)
    if data["status"] == "error":
        module.fail_json(msg=f"Error creating entry: {data['messages']}")
    return True

def delete_entry(
    snipe_url: str,
    api_key: str,
    asset_tag: str,
    module: AnsibleModule,
    dry_run: bool,
) -> bool:
    """Delete an entry in SnipeIT. Return False if it doesn't exist

    :param snipe_url: The URL of the SnipeIT instance
    :param api_key: The API key to use to authenticate to SnipeIT
    :param asset_tag: The asset tag to use for the entry
    :param module:  The AnsibleModule object
    :param dry_run: If True, don't actually delete the entry.
    :return: True if the entry was deleted, False if it doesn't exist.
    In dry-run mode, return True if it would have been deleted and False otherwise.
    """
    entry = get_entry(snipe_url, api_key, asset_tag, module)
    if not entry:
        return False
    if entry and dry_run:
        return True
    response = requests.delete(
        f"{snipe_url.rstrip('/')}/api/v1/hardware/{entry['id']}",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    data = json.loads(response.text)
    if data["status"] == "error":
        module.fail_json(msg=f"Error deleting entry: {data['messages']}")
    return True

def update_entry_model(
    snipe_url: str,
    api_key: str,
    asset_tag: str,
    model_id: int,
    module: AnsibleModule,
    dry_run: bool,
):
    """Update the model of an existing entry in SnipeIT.
    Return False if it is already correct

    :param snipe_url: The URL of the SnipeIT instance
    :param api_key: The API key to use to authenticate to SnipeIT
    :param asset_tag: The asset tag to use for the entry
    :param model_id: The model ID to use for the entry
    :param module:  The AnsibleModule object
    :param dry_run: If True, don't actually update the entry.
    :return: True if the entry was updated, False if it already exists. In dry-run mode, return True if it would have been updated and False otherwise.
    """
    entry = get_entry(snipe_url, api_key, asset_tag, module)
    if entry["model"]["id"] == model_id:
        return False
    if entry["model"]["id"] != model_id and dry_run:
        return True
    payload = {
        "model_id": model_id,
    }
    response = requests.patch(
        f"{snipe_url.rstrip('/')}/api/v1/hardware/{entry['id']}",
        json=payload,
        headers={"Authorization": f"Bearer {api_key}"},
    )
    data = json.loads(response.text)
    if data["status"] == "error":
        module.fail_json(msg=f"Error updating entry: {data['messages']}")
    return True


def update_entry_status_label(
    snipe_url: str,
    api_key: str,
    asset_tag: str,
    status_id: int,
    module: AnsibleModule,
    dry_run: bool,
):
    """Update the status of an existing entry in SnipeIT. Return False if it is already correct

    :param snipe_url: The URL of the SnipeIT instance
    :param api_key: The API key to use to authenticate to SnipeIT
    :param asset_tag: The asset tag to use for the entry
    :param status_id: The status ID to use for the entry
    :param module: The AnsibleModule object
    :param dry_run: When True, don't actually update the entry
    :return: True if the entry was updated, False if it already exists. In dry-run mode, return True if it would have been updated and False otherwise.
    """
    entry = get_entry(snipe_url, api_key, asset_tag, module)
    if entry["status_label"]["id"] == status_id:
        return False
    if entry["status_label"]["id"] != status_id and dry_run:
        return True
    payload = {
        "status_id": status_id,
    }
    response = requests.patch(
        f"{snipe_url.rstrip('/')}/api/v1/hardware/{entry['id']}",
        json=payload,
        headers={"Authorization": f"Bearer {api_key}"},
    )
    data = json.loads(response.text)
    if data["status"] == "error":
        module.fail_json(msg=f"Error updating entry: {data['messages']}")
    return True


def verify_params(module: AnsibleModule) -> None:
    """  Any arg verification that Ansible cannot handle itself
    is done here.  This is a good place to check for arguments that are mutually exclusive, arguments that are required
    only in specific situations, etc. Executes module.fail_json() if verification fails.

    :param module: The AnsibleModule object
    :return: None
    """
    if module.params["state"] == "present" and not module.params["model_name"]:
        module.fail_json(msg="model_name is required when state is present")

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = {
        "asset_tag": {"type": "str", "required": True},
        "snipe_url": {"type": "str", "required": True},
        "api_key": {"type": "str", "required": True, "no_log": True},
        "status_id": {"type": "int", "required": False, "default": 2},
        "model_name": {"type": "str", "required": False}, # required on create/update, enforced by verify_params
        "state": {"type": "str", "required": False, "default": "present", "choices": ["present", "absent"]},
    }

    result = {"changed": False}

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    verify_params(module)

    if module.params["state"] == "absent":
        changed = delete_entry(
            module.params["snipe_url"],
            module.params["api_key"],
            module.params["asset_tag"],
            module,
            module.check_mode,
        )
        result["changed"] = changed
        module.exit_json(**result)

    dry_run = module.check_mode
    model = get_model(
        module.params["snipe_url"],
        module.params["api_key"],
        module.params["model_name"],
        module,
    )
    if not model:
        module.fail_json(msg=f"Model {module.params['model_name']} does not exist")

    changed = False  # noqa: F841
    changed = create_entry(
        module.params["snipe_url"],
        module.params["api_key"],
        module.params["asset_tag"],
        module.params["status_id"],
        model["id"],
        module,
        dry_run,
    )
    # order matters - if you use this pattern, always put changed last
    # Otherwise the interpreter will skip executing your function!
    changed = (
        update_entry_model(
            module.params["snipe_url"],
            module.params["api_key"],
            module.params["asset_tag"],
            model["id"],
            module,
            dry_run,
        )
        or changed
    )

    changed = (
        update_entry_status_label(
            module.params["snipe_url"],
            module.params["api_key"],
            module.params["asset_tag"],
            module.params["status_id"],
            module,
            dry_run,
        )
        or changed
    )

    result["changed"] = changed

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
