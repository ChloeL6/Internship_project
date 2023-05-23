import os

import pandas as pd
import asana as asana_api

from .. import utils

SECRETS_PATH = os.getenv('SECRETS_PATH')
CLIENT_NAME = os.getenv('CLIENT_NAME')
CREDENTIAL_FILE_NAME = 'asana_credentials.json'


def get_tasks(project: str, file_name: str):
    """
    Get tasks for a project
    :param project: ID of the project to download
    :param file_name: File_name to save data to
    :return: 
    """
    credentials_path = f'{SECRETS_PATH}/{CLIENT_NAME}/{CREDENTIAL_FILE_NAME}'
    credentials = utils.get_credentials(credentials_path)
    client = asana_api.Client.access_token(credentials['ACCESS_TOKEN'])
    client.LOG_ASANA_CHANGE_WARNINGS = False 

    task_list = []
    response = client.tasks.get_tasks_for_project(project, limit=20, opt_fields='gid', full_payload=True, iterator_type=None)

    # Extract data from the response
    for task in response['data']:
        task_list.append(task['gid'])

    # Handle pagination
    while response['next_page']:
        offset = response['next_page']['offset']
        response = client.tasks.get_tasks_for_project(project, limit=20, opt_fields='gid', full_payload=True, iterator_type=None, offset=offset)
        for task in response['data']:
            task_list.append(task['gid'])

    # For each task ID, get all task info
    rows = []
    for task_gid in task_list:
        task = client.tasks.get_task(task_gid)
        data = {
            'assignee': 'None',
            'assigneeId': 'None',
            'due_at': task['due_at'],
            'start_on': task['start_on'],
            'due_on': task['due_on'],
            'created': task['created_at'],
            'modified': task['modified_at'],
            'completed': task['completed'],
            'completed_at': task['completed_at'],
            'task_description': task['name'],
            'type': task['resource_type'],
            'url': task['permalink_url'],
            'workspace': task['workspace']['name'],
            'workspaceId': task['workspace']['gid'],
            'notes': task['notes'],
            # Custom tags of interest
            'Clients': 'none',
            'Priority': 'none',
            'Hours': 0,
            'Status': 'none',
            'Lift': 'none',
            'Impact': 'none',
            'Type - Paid Media': 'none',
            'Channel': 'none',
            'Strategy': 'none'
        }
        
        # If there is an assignee, pull out the relevant info
        if task['assignee']: 
            data['assignee'] = task['assignee']['name']
            data['assigneeId'] = task['assignee']['gid']

            # Custom tags in Asana that are of interest for reporting purposes.
            # These are hard coded so that they are always in the same column place
            # Power BI doesn't do dynamic columns, so if the columns ever move the
            # reports will break.
            custom_tags_of_interest = ['Clients', 'Lift', 'Impact', 'Type - Paid Media', 'Channel', 'Strategy', 'Status']
                        
            for tag in task['custom_fields']:
                for custom_tag in custom_tags_of_interest:
                    if tag and tag['name'] == custom_tag:
                        data[custom_tag] = tag['display_value']
            rows.append(data)

    df = pd.DataFrame(rows)
    df.to_csv(file_name, index=False)