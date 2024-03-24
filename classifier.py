from abc import ABC, abstractmethod
from typing import *
import requests
from pydantic import BaseModel


class ContentModeratorResponseData(BaseModel):
    label: str
    score: float


class Classifier(ABC):
    """

    """

    @abstractmethod
    def classify(self, message: str) -> List[List[ContentModeratorResponseData]]:
        """

        :param message:
        :return:
        """
        pass

    @abstractmethod
    def _validate_config_args(self, **kwargs):
        """
        Private method to check the config properties needed for a classifier
        :param kwargs: All keyword arguments provided from the caller
        :return: Void if all validations succeed
        :raises: Exception if one of the validation fails
        """
        pass


'''
{
"error": "Model KoalaAI/Text-Moderation is currently loading",
"estimated_time": 22.272043228149414
}
'''


class KoalaClassifier(Classifier):
    """
    The KoalaClassifier is an implementation of the Classifier class which uses the KoalaAI text moderation
    model from hugging face. For a detailed description about the model and its capabilities please visit
    its dedicated page at: https://huggingface.co/KoalaAI/Text-Moderation?inference_api=true
    """

    def __init__(self, **kwargs):
        self._validate_config_args(**kwargs)
        self.url: str = kwargs['url']
        self.bearer_token: Any = kwargs['bearer_token']

    def classify(self, message: str) -> List[List[ContentModeratorResponseData]]:
        """
        Contact the serverless endpoint provided my hugging face and provide
        a text classification

        :param message: The string that needs to be classified
        :return: A list of rating for certain text classification dimensions
        e.g. hate, violence etc.
        """

        response_json = self._query_http_endpoint({
            "inputs": message,
        })

        if 'error' in response_json:
            return []

        return response_json

    def _validate_config_args(self, **kwargs):
        if not kwargs:
            raise Exception('Koala Classifier requires further configuration')

        if 'url' not in kwargs:
            raise Exception('Cannot create Koala Classifier without a URL to the model')

        if 'bearer_token' not in kwargs:
            raise Exception(
                'Koala Classifier uses an OAuth authenticated API which needs a personal bearer token which was not provided')

    def _query_http_endpoint(self, payload: Dict[str, Any]):
        headers = {'Authorization': f'Bearer {self.bearer_token}'}
        response = requests.post(self.url, headers=headers, json=payload)
        return response.json()


class ClassifierFactory:
    @staticmethod
    def create(name: str = 'koala', **kwargs) -> Classifier:
        if kwargs:
            if name == 'koala':
                return KoalaClassifier(**kwargs)

        raise Exception('Was not able to create any classifier: Too little info provided')
