import os

import pandas as pd
import asana as asana_api

from .. import utils

SECRETS_PATH = os.getenv('SECRETS_PATH')
CLIENT_NAME = os.getenv('CLIENT_NAME')
CREDENTIAL_FILE_NAME = 'asana_credentials.json'


def get_projects(workspace: str, file_name: str):
    """
    Get projects for a workspace
    :param workspace: ID of the workspace to download
    :param file_name: File_name to save data to
    :return: 
    """
    credentials_path = f'{SECRETS_PATH}/{CLIENT_NAME}/{CREDENTIAL_FILE_NAME}'
    credentials = utils.get_credentials(credentials_path)
    client = asana_api.Client.access_token(credentials['ACCESS_TOKEN'])
    client.LOG_ASANA_CHANGE_WARNINGS = False

    data = []
    response = client.projects.get_projects_for_workspace(workspace, limit=100, full_payload=True, iterator_type=None)
    
    # Extract data from the response
    for project in response['data']:
        data.append(project)

    # Handle pagination
    while response['next_page']:
        offset = response['next_page']['offset']
        response = client.projects.get_projects_for_workspace(workspace, limit=100,full_payload=True,
                                                              iterator_type=None, offset=offset)
        for project in response['data']:
            data.append(project)

    df = pd.DataFrame(data)
    df.to_csv(file_name, index=False)
