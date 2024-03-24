from abc import ABC, abstractmethod
from functools import wraps
from threading import Thread
from typing import *

import schedule

from thread_safe_collections import ThreadSafeDict


class Reporter(ABC):
    """
    The reporter represents the layer we might be using to persist our metrics.
    Some examples of a metrics persistence layer:
    - stdout
    - file
    - influx
    - sql database
    - ...
    """

    @abstractmethod
    def report(self, metrics: ThreadSafeDict[str, int]):
        """
        Contains the core logic of the metrics persistence layer

        :param metrics: Dictionary from metric name to metric value
        :return: Void
        :raises Exception in case of any errors upon the persistence process
        """
        pass


class StdOutMetricsReporter(Reporter):
    """
    Naive metrics collector printing all collected metrics to stdout
    """

    def report(self, metrics: ThreadSafeDict[str, int]):
        """
         Once the metrics are persisted we can start tracking metrics for the new reporting interval.
         That is why we are truncating the metrics map upon successful reporting
        """
        print(f'Printing all metrics collected so far {metrics}')

        metrics.clear()


class FileMetricsReporter(Reporter):
    def report(self, metrics: ThreadSafeDict[str, int]):
        pass


class InfluxMetricsReporter(Reporter):
    def report(self, metrics: ThreadSafeDict[str, int]):
        pass


class ReporterFactory:
    """
    Implemented just the sake of abstraction
    """

    @staticmethod
    def create():
        return StdOutMetricsReporter()


class MetricsCollector:
    """
    Metrics collector interface. This was defined as a separate interface
    mainly for futureproof-ness. Many metrics collectors apply aggregations
    before sending data to the reporting database or persisting the data
    somewhere on disk. Collect is a separate method for testing purposes.
    """

    @staticmethod
    def _run_scheduled_metrics_collection():
        while True:
            schedule.run_pending()

    # Method counts is a static member variable shared by all instances of MetricsCollector
    method_counts: ThreadSafeDict[str, int] = ThreadSafeDict()

    # The thread where the metrics collection runs is also static and shared
    scheduler_thread: Thread = Thread(target=_run_scheduled_metrics_collection, daemon=True)

    def __init__(self, reporting_interval_in_seconds: int, reporter: Reporter):

        schedule.every(reporting_interval_in_seconds).seconds.do(self.collect_and_report)
        self.reporter = reporter

    def start(self):
        print(f'Starting metric collection and reporting...')
        MetricsCollector.scheduler_thread.start()

    def kill(self):
        if self.scheduler_thread:
            MetricsCollector.scheduler_thread.join(timeout=2)

    def collect(self) -> ThreadSafeDict[str, int]:
        return MetricsCollector.method_counts

    def collect_and_report(self):
        self.reporter.report(self.collect())


def method_counter(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    After every method call the decorator with increment the counter indicating
    how many times the method was invoked. This is primarily used from the root API
    methods. The wrapper need to be annotated with @wraps: https://stackoverflow.com/a/64656733/6566916

    :param func: Method to track for metrics
    :return: Returns the decorator itself
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        result: Any = func(*args, **kwargs)

        # Update metrics
        method_name = func.__name__
        individual_method_count: Optional[int] = MetricsCollector.method_counts.get(method_name)
        method_counts_so_far: int = individual_method_count if individual_method_count else 0
        MetricsCollector.method_counts.put(method_name, method_counts_so_far + 1)
        return result

    return wrapper
