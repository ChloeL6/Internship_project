import json


def get_credentials(file_name: str) -> dict:
    """
    Get credentials in dict form from a JSON file
    :param file_name: Name of JSON file
    :return: Dict containing credentials
    """
    if file_name.endswith('json'):
        with open(file_name, 'r') as f:
            return json.load(f)
    else:
        raise SystemError('This function only reads JSON files.')