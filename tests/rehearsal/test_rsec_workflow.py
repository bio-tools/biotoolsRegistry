import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest

import yaml


WORKFLOW = Path(__file__).with_name('rsec-pr-validator.yml')
STEPS = yaml.load(WORKFLOW.read_text(), Loader=yaml.BaseLoader)['jobs']['validate-and-merge']['steps']


class RsecWorkflowTests(unittest.TestCase):
    def run_step(self, name, *, branch='editor__test-tool', changes='', record=None, state='open\thead'):
        script = next(step['run'] for step in STEPS if step.get('name') == name)
        with TemporaryDirectory() as directory:
            root = Path(directory)
            gh = root / 'gh'
            gh.write_text('#!/bin/sh\nprintf "%s\\n" "$MOCK_GH_OUTPUT"\n')
            gh.chmod(0o755)
            output = root / 'output'
            output.touch()
            if record is not None:
                path = root / 'data/test-tool/test-tool.biotools.json'
                path.parent.mkdir(parents=True)
                path.write_text(record)
            env = {**os.environ, 'PATH': str(root) + os.pathsep + os.environ['PATH'],
                   'GH_TOKEN': 'fixture', 'GITHUB_REPOSITORY': 'fixture/content',
                   'PR_NUMBER': '1', 'BRANCH': branch, 'EVENT_SHA': 'head',
                   'GITHUB_OUTPUT': str(output), 'MOCK_GH_OUTPUT': changes if name == 'Verify the intended record' else state}
            result = subprocess.run(['bash', '-c', script], cwd=root, env=env, capture_output=True, text=True)
            return result, output.read_text()

    def test_shell_steps_are_valid_and_do_not_push_commits(self):
        for step in STEPS:
            if 'run' in step:
                result = subprocess.run(['bash', '-n'], input=step['run'], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertNotIn('git push', step['run'])

    def test_closed_or_changed_pull_request_is_skipped_before_checkout(self):
        for state in ('closed\thead', 'open\tnew-head'):
            result, output = self.run_step('Check that this pull request is still current', state=state)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn('run=true', output)
        result, output = self.run_step('Check that this pull request is still current')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('run=true', output)

    def test_only_the_expected_record_or_deletion_is_accepted(self):
        path = 'data/test-tool/test-tool.biotools.json'
        result, output = self.run_step('Verify the intended record', changes=path + '\tmodified',
                                       record='{"biotoolsID":"test-tool"}')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('deleted=false', output)
        result, _ = self.run_step('Verify the intended record', branch='editor__with__underscores__test-tool',
                                  changes=path + '\tmodified', record='{"biotoolsID":"test-tool"}')
        self.assertEqual(result.returncode, 0, result.stderr)
        result, output = self.run_step('Verify the intended record', branch='editor__test-tool__delete',
                                       changes=path + '\tremoved')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('deleted=true', output)
        for changes, record in ((path + '\tmodified\nother.txt\tadded', '{"biotoolsID":"test-tool"}'),
                                (path + '\tmodified', '{"biotoolsID":"another"}')):
            result, _ = self.run_step('Verify the intended record', changes=changes, record=record)
            self.assertNotEqual(result.returncode, 0)
        result, _ = self.run_step('Verify the intended record', branch='editor__../../unsafe', changes=path + '\tremoved')
        self.assertNotEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()
