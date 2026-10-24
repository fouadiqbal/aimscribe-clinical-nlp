"""Cloud recovery checks; no network, downloads or model process required."""
import unittest
from unittest.mock import patch, MagicMock
from urllib.error import URLError
from cloud import bootstrap


class CloudRecoveryTests(unittest.TestCase):
    def test_rechecks_health_after_previous_success(self):
        with patch.object(bootstrap.urllib.request, 'urlopen', return_value=MagicMock()) as health:
            bootstrap.ensure_model_server()
            bootstrap.ensure_model_server()
            self.assertEqual(health.call_count, 2)

    def test_dead_server_retries_setup_after_success(self):
        with patch.object(bootstrap.urllib.request, 'urlopen', return_value=MagicMock()):
            bootstrap.ensure_model_server()
        with patch.object(bootstrap.urllib.request, 'urlopen', side_effect=URLError('stopped')), patch.object(bootstrap.st, 'status', return_value=MagicMock()), patch.object(bootstrap, '_download', side_effect=RuntimeError('setup retried')):
            with self.assertRaisesRegex(RuntimeError, 'setup retried'):
                bootstrap.ensure_model_server()


if __name__ == '__main__':
    unittest.main()
