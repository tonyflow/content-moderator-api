import unittest

from metrics import *
from unittest.mock import Mock, patch


class MetricsCollectorTest(unittest.TestCase):
    def test_collect(self):
        stdout_metrics_reporter: Reporter = StdOutMetricsReporter()
        metrics_collector: MetricsCollector = MetricsCollector(
            reporting_interval_in_seconds=3,
            reporter=stdout_metrics_reporter)
        MetricsCollector.method_counts.put('foo', 4)
        MetricsCollector.method_counts.put('bar', 5)
        actual_metrics: ThreadSafeDict[str, int] = metrics_collector.collect()
        expected_metrics = {
            'foo': 4,
            'bar': 5
        }

        self.assertEqual(actual_metrics.get_all(), expected_metrics)

    def test_successful_collect_and_report(self):
        """
        Reporter should truncate the metrics upon successful reporting
        """
        stdout_metrics_reporter: Reporter = StdOutMetricsReporter()
        metrics_collector: MetricsCollector = MetricsCollector(
            reporting_interval_in_seconds=3,
            reporter=stdout_metrics_reporter)
        MetricsCollector.method_counts.put('foo', 4)
        MetricsCollector.method_counts.put('bar', 5)
        metrics_collector.collect_and_report()

        self.assertEqual(MetricsCollector.method_counts.get_all(), {})

    @patch.object(StdOutMetricsReporter, 'report')
    def test_failed_collect_and_report(self, mocked_report_method: Mock):
        """
        Metrics should not be truncated if reporting was not successful
        """
        mocked_report_method.side_effect = Exception('Mock report exception')
        stdout_metrics_reporter: Reporter = StdOutMetricsReporter()
        metrics_collector: MetricsCollector = MetricsCollector(
            reporting_interval_in_seconds=3,
            reporter=stdout_metrics_reporter)
        MetricsCollector.method_counts.put('foo', 4)
        MetricsCollector.method_counts.put('bar', 5)
        metrics_collector.collect_and_report()
        expected_metrics = {
            'foo': 4,
            'bar': 5
        }

        self.assertEqual(MetricsCollector.method_counts.get_all(), expected_metrics)
