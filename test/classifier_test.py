import unittest
from classifier import *
from unittest.mock import Mock, patch
from typing import *


class KoalaClassifierTest(unittest.TestCase):
    """
    Since the Koala API endpoint is not always on, and we cannot
    immediately get a response, we are mocking the HTTP request
    """
    mock_koala_response = [
        [{"label": "OK", "score": 0.7044275999069214}, {"label": "SH", "score": 0.09657368808984756},
         {"label": "H", "score": 0.08526786416769028}, {"label": "V", "score": 0.038328953087329865},
         {"label": "HR", "score": 0.024068444967269897}, {"label": "S", "score": 0.01646522432565689},
         {"label": "V2", "score": 0.016412340104579926}, {"label": "H2", "score": 0.010275991633534431},
         {"label": "S3", "score": 0.008179856464266777}]]

    @patch.object(KoalaClassifier,
                  attribute='_query_http_endpoint',
                  return_value=mock_koala_response)
    def test_classify(self, _):
        koala_classifier: KoalaClassifier = KoalaClassifier(
            url='dummy url',
            bearer_token='foo')

        classification_response: List[List[ContentModeratorResponseData]] = koala_classifier.classify(
            "This is test message")

        self.assertEqual(self.mock_koala_response, classification_response)

    @patch.object(KoalaClassifier,
                  attribute='_query_http_endpoint',
                  side_effect=Exception('An error occurred'))
    def test_error(self, _):
        with self.assertRaises(Exception):
            koala_classifier: KoalaClassifier = KoalaClassifier(
                url='dummy url',
                bearer_token='foo')

            koala_classifier.classify("This is test message")


class ClassifierFactoryTest(unittest.TestCase):
    def test_should_return_koala_when_no_classifier_name_is_given(self):
        classifier: Classifier = ClassifierFactory.create(url='foo', bearer_token='bar')
        self.assertIsInstance(classifier, KoalaClassifier)

    def test_should_return_koala_when_koala_is_given(self):
        classifier: Classifier = ClassifierFactory.create(name='koala', url='foo', bearer_token='bar')
        self.assertIsInstance(classifier, KoalaClassifier)

    def test_raise_exception_when_no_kwargs_are_given(self):
        with self.assertRaises(Exception):
            ClassifierFactory.create()

