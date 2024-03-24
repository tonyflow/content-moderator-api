from fastapi import FastAPI
from metrics import method_counter, MetricsCollector, Reporter, ReporterFactory
from classifier import Classifier, ClassifierFactory

import os
import yaml


def bootstrap() -> (Classifier, MetricsCollector):
    with open('app_conf.yml') as config_file:
        config = yaml.safe_load(config_file)
        classifier: Classifier = ClassifierFactory.create(name=config['classifier']['name'],
                                                          url=config['classifier']['config']['url'],
                                                          bearer_token=os.environ.get('BEARER_TOKEN'))

        stdout_reporter: Reporter = ReporterFactory.create()
        metrics_collector: MetricsCollector = MetricsCollector(
            reporter=stdout_reporter,
            reporting_interval_in_seconds=config['metrics']['config']['reporting_interval_in_seconds'])

        return classifier, metrics_collector


content_moderator = FastAPI()
classifier, metrics_collector = bootstrap()
metrics_collector.start()


@content_moderator.get("/")
def root():
    return "Welcome to a content moderation application"


@content_moderator.get("/healthcheck")
@method_counter
def healthcheck():
    return 200


@content_moderator.get("/classify")
@method_counter
def classify(message: str):
    return classifier.classify(message)
