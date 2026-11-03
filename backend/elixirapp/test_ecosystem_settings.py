import os
from pathlib import Path
import subprocess
import sys
from unittest import TestCase


class EcosystemTokenSettingsTests(TestCase):
    def token_from_environment(self, **values):
        env = os.environ.copy()
        for key in ('ECO_PERSONAL_TOKEN', 'ECO_GITHUB_TOKEN', 'ECO_LOGGER_NAME'):
            env.pop(key, None)
        env.update(values)
        return subprocess.check_output(
            [sys.executable, '-c', 'from elixir.ecosystem.settings import ECO_PERSONAL_TOKEN; print(ECO_PERSONAL_TOKEN)'],
            cwd=Path(__file__).resolve().parents[1], env=env, text=True,
        ).strip()

    def test_personal_token_comes_from_its_own_environment_variable(self):
        self.assertEqual(self.token_from_environment(ECO_PERSONAL_TOKEN='personal', ECO_LOGGER_NAME='logger'), 'personal')

    def test_legacy_token_name_is_supported(self):
        self.assertEqual(self.token_from_environment(ECO_GITHUB_TOKEN='legacy'), 'legacy')

    def test_logger_name_is_not_used_as_a_token(self):
        self.assertEqual(self.token_from_environment(ECO_LOGGER_NAME='logger'), '')
