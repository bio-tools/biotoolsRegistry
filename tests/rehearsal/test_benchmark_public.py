import contextlib
import io
import json
import unittest
from unittest.mock import patch

import benchmark_public


class PublicBenchmarkTests(unittest.TestCase):
    def test_reports_local_requests_and_concurrent_searches(self):
        response = {'status': 200, 'ms': 12.0}
        output = io.StringIO()
        with patch('sys.argv', ['benchmark', '--samples', '2']), \
             patch.object(benchmark_public, 'request', return_value=response), \
             contextlib.redirect_stdout(output):
            benchmark_public.main()
        result = json.loads(output.getvalue())
        self.assertEqual(result['home'], {'samples': 2, 'p95_ms': 12.0, 'max_ms': 12.0, 'failures': []})
        self.assertEqual(len(result['four_concurrent_searches']), 4)

    def test_rejects_remote_targets_before_requesting(self):
        with patch('sys.argv', ['benchmark', '--base-url', 'https://example.org']), \
             patch.object(benchmark_public, 'request') as request, \
             contextlib.redirect_stderr(io.StringIO()), \
             self.assertRaises(SystemExit):
            benchmark_public.main()
        request.assert_not_called()

    def test_failed_responses_cause_a_failure(self):
        with patch('sys.argv', ['benchmark', '--samples', '1']), \
             patch.object(benchmark_public, 'request', return_value={'status': 503, 'ms': 1}), \
             contextlib.redirect_stdout(io.StringIO()), \
             self.assertRaises(SystemExit) as result:
            benchmark_public.main()
        self.assertEqual(result.exception.code, 1)


if __name__ == '__main__':
    unittest.main()
