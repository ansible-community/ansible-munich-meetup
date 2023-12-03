import json
import requests

from typing import Union
from ansible.module_utils.basic import AnsibleModule


def get_category(
    snipe_url: str, api_key: str, name: str, category_type: str
) -> Union[dict, None]:
    """Return an existing category from SnipeIT or None if it doesn't exist

    :param snipe_url: The URL of the SnipeIT instance
    :param api_key: The API key to use to authenticate to SnipeIT
    :param name: The name of the category to retrieve
    :param category_type: The type of category to retrieve. This can be one of ["asset", "accessory", "consumable", "component"]
    :param module: The AnsibleModule object
    :return:
    """
    payload = {"name": name, "category_type": category_type}
    response = requests.get(
        f"{snipe_url.rstrip('/')}/api/v1/categories",
        headers={"Authorization": f"Bearer {api_key}"},
        params=payload,
    )
    data = json.loads(response.text)
    if data["total"] == 0:
        return None
    return data["rows"][0]


def get_model(
    snipe_url: str, api_key: str, name: str, module: AnsibleModule
) -> Union[dict, None]:
    """Return an existing model from SnipeIT or None if it doesn't exist

    :param snipe_url: The URL of the SnipeIT instance
    :param api_key: The API key to use to authenticate to SnipeIT
    :param name: The name of the model to retrieve
    :param module: The AnsibleModule object

    :return: Dict of model data or None if it doesn't exist
    """
    payload = {"name": name}
    response = requests.get(
        f"{snipe_url.rstrip('/')}/api/v1/models",
        headers={"Authorization": f"Bearer {api_key}"},
        params=payload,
    )
    data = json.loads(response.text)
    if data["total"] == 0:
        return None
    return data["rows"][0]


def get_entry(
    snipe_url: str, api_key: str, asset_tag: str, module: AnsibleModule
) -> Union[dict, None]:
    """Return an existing entry from SnipeIT or None if it doesn't exist

    :param snipe_url:
    :param api_key:
    :param asset_tag:
    :return:
    """
    response = requests.get(
        f"{snipe_url.rstrip('/')}/api/v1/hardware/bytag/{asset_tag}",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    data = json.loads(response.text)
    if "asset_tag" in data.keys():
        return data
    if data["status"] == "error" and data["messages"] == "Asset does not exist.":
        return None
    if data["status"] == "error":
        module.fail_json(msg=f"Error retrieving entry: {data['messages']}")
    module.fail_json("Unknown response from SnipeIT")
