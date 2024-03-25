import logging
from abc import ABC, abstractmethod

from pydantic import BaseModel

from helpers import *


class KoalaTextModerationLabel(BaseModel):
    """
    Response model of the Koala AI Text Moderation API. More information about the labels
    can be found here https://huggingface.co/KoalaAI/Text-Moderation
    """
    label: str
    score: float


R = TypeVar('R')


class Classifier(ABC, Generic[R]):
    """
    Base class for all classifier models
    """

    @abstractmethod
    def classify(self, message: str) -> R:
        """
        Run the core classification code. Either call an external API or access internal models

        :param message: Text to be classified. Warning: The length is currently unrestricted
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


class KoalaClassifier(Classifier[List[KoalaTextModerationLabel]]):
    """
    The KoalaClassifier is an implementation of the Classifier class which uses the KoalaAI text moderation
    model from hugging face. For a detailed description about the model and its capabilities please visit
    its dedicated page at: https://huggingface.co/KoalaAI/Text-Moderation?inference_api=true
    """

    def __init__(self, **kwargs):
        self._validate_config_args(**kwargs)
        self.url: str = kwargs['url']
        self.bearer_token: Any = kwargs['bearer_token']

    def classify(self, message: str) -> List[KoalaTextModerationLabel]:
        """
        Contact the serverless endpoint provided my hugging face and provide
        a text classification

        :param message: The string that needs to be classified
        :return: A list of rating for certain text classification dimensions
        e.g. hate, violence etc.
        """

        response_json = query_http_endpoint(url=self.url, bearer_token=self.bearer_token, payload={
            "inputs": message,
        })

        if 'error' in response_json:
            logging.error(f'Classifier failed with {response_json}')
            return []

        return flatten_concatenation(response_json)

    def _validate_config_args(self, **kwargs):
        if not kwargs:
            raise Exception('Koala Classifier requires further configuration')

        if 'url' not in kwargs:
            raise Exception('Cannot create Koala Classifier without a URL to the model')

        if 'bearer_token' not in kwargs:
            raise Exception(
                'Koala Classifier uses an OAuth authenticated API which needs a personal bearer token which was not provided')


class ClassifierFactory:
    """
    Helper method for creating the classifier used from the moderator service
    """

    @staticmethod
    def create(name: str = 'koala', **kwargs) -> Classifier:
        if kwargs:
            if name == 'koala':
                return KoalaClassifier(**kwargs)

        raise Exception('Was not able to create any classifier: Too little info provided')
