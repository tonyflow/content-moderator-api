from typing import *
import requests


def query_http_endpoint(url: str, bearer_token: str, payload: Dict[str, Any]):
    """
    Post HTTP request

    :param url: URL to be consumed
    :param bearer_token: Bearer token for authentication
    :param payload: Request body
    :return: Response in JSON
    """
    headers = {'Authorization': f'Bearer {bearer_token}'}
    response = requests.post(url, headers=headers, json=payload)
    return response.json()


def flatten_concatenation(xss: List[List[Any]]) -> List[Any]:
    """
    Flatten a generic list of lists.

    :param xss: List of lists
    :return: Flattened list
    """
    return [x for xs in xss for x in xs]
