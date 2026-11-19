import json
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import SimpleTestCase
from github import GithubException

from elixir.biotools_to_github import ecosytem_handle_tool_operations
from elixir.ecosystem.biotools_handler import BioToolsData
from elixir.ecosystem.ecosystem_exceptions import ToolCreationException, ToolDeleteException
from elixir.ecosystem.github_handler import GithubToolHandler


class EcosystemRecoveryTests(SimpleTestCase):
    def setUp(self):
        self.handler = GithubToolHandler.__new__(GithubToolHandler)
        self.handler._GithubToolHandler__logged_in = True
        self.repo = Mock()
        self.handler._GithubToolHandler__repo = self.repo
        self.branch = 'editor__test-tool'
        self.path = 'data/test-tool/test-tool.biotools.json'
        self.data = BioToolsData('Editor', json.dumps({'biotoolsID': 'test-tool', 'name': 'Test'}))
        self.handler.MASTER_BRANCH = 'master'
        self.handler.ROOT_GITHUB_FOLDER = 'data'
        self.repo.get_branches.return_value = [SimpleNamespace(name=self.branch)]
        self.repo.get_pulls.return_value = []
        self.repo.get_branch.return_value = SimpleNamespace(commit=SimpleNamespace(sha='base'))
        self.repo.create_file.return_value = {'created': True}
        self.repo.create_pull.return_value = SimpleNamespace(number=42)

    def test_retry_creates_missing_file_on_unchanged_branch(self):
        created = SimpleNamespace(decoded_content=self.data.tool_json.encode())
        self.repo.get_contents.side_effect = [GithubException(404, {}, {}), created]
        _, pr = self.handler.create_tool(self.data)
        self.assertEqual(pr.number, 42)
        self.assertEqual(self.repo.create_file.call_args.kwargs['path'], self.path)
        self.repo.create_git_ref.assert_not_called()

    def test_retry_reuses_matching_record_and_pull_request(self):
        existing = SimpleNamespace(decoded_content=self.data.tool_json.encode())
        pr = SimpleNamespace(number=17, head=SimpleNamespace(ref=self.branch))
        self.repo.get_contents.return_value = existing
        self.repo.compare.return_value.files = [SimpleNamespace(filename=self.path)]
        self.repo.get_pulls.return_value = [pr]
        _, result = self.handler.create_tool(self.data)
        self.assertIs(result, pr)
        self.repo.create_file.assert_not_called()
        self.repo.create_pull.assert_not_called()

    def test_retry_does_not_modify_a_branch_when_base_has_advanced(self):
        self.repo.get_contents.side_effect = GithubException(404, {}, {})
        self.repo.get_branch.side_effect = [SimpleNamespace(commit=SimpleNamespace(sha='old')),
                                            SimpleNamespace(commit=SimpleNamespace(sha='new'))]
        with self.assertRaises(ToolCreationException):
            self.handler.create_tool(self.data)
        self.repo.create_file.assert_not_called()
        self.repo.create_pull.assert_not_called()

    def test_retry_refuses_conflicting_content_or_unrelated_changes(self):
        self.repo.get_contents.return_value = SimpleNamespace(decoded_content=b'{"name":"different"}')
        self.repo.compare.return_value.files = [SimpleNamespace(filename=self.path)]
        with self.assertRaises(ToolCreationException):
            self.handler.create_tool(self.data)
        self.repo.get_contents.return_value = SimpleNamespace(decoded_content=self.data.tool_json.encode())
        self.repo.compare.return_value.files = [SimpleNamespace(filename='other.txt')]
        with self.assertRaises(ToolCreationException):
            self.handler.create_tool(self.data)
        self.repo.create_file.assert_not_called()
        self.repo.create_pull.assert_not_called()

    def test_github_failure_is_not_treated_as_missing_file(self):
        self.repo.get_contents.side_effect = GithubException(500, {}, {})
        with self.assertRaises(GithubException):
            self.handler.create_tool(self.data)
        self.repo.create_file.assert_not_called()

    def test_update_after_merge_creates_a_new_branch_and_pull_request(self):
        self.repo.get_branches.return_value = []
        self.repo.get_contents.return_value = SimpleNamespace(sha='original')
        _, pr = self.handler.update_tool(self.data)
        self.assertEqual(pr.number, 42)
        self.repo.create_git_ref.assert_called_once()
        self.assertEqual(self.repo.update_file.call_args.kwargs['path'], self.path)
        self.assertEqual(self.repo.create_pull.call_args.kwargs['head'], self.branch)

    def test_deletion_after_merge_uses_a_separate_branch(self):
        self.repo.get_branches.return_value = []
        deleted = False

        def contents(path, ref):
            if deleted and ref.endswith('__delete'):
                raise GithubException(404, {}, {})
            return SimpleNamespace(sha='original')

        def remove(**kwargs):
            nonlocal deleted
            deleted = True
            return {'deleted': True}

        self.repo.get_contents.side_effect = contents
        self.repo.delete_file.side_effect = remove
        _, pr = self.handler.delete_tool(self.data)
        self.assertEqual(pr.number, 42)
        self.assertEqual(self.repo.delete_file.call_args.kwargs['path'], self.path)
        self.assertEqual(self.repo.create_pull.call_args.kwargs['head'], self.branch + '__delete')

    def test_delete_locates_an_unmerged_branch_with_normalized_user_name(self):
        self.repo.get_pulls.return_value = [SimpleNamespace(head=SimpleNamespace(ref=self.branch))]
        deleted = False

        def contents(path, ref):
            if ref == 'master' or (deleted and ref.endswith('__delete')):
                raise GithubException(404, {}, {})
            return SimpleNamespace(sha='original')

        def remove(**kwargs):
            nonlocal deleted
            deleted = True
            return {'deleted': True}

        self.repo.get_contents.side_effect = contents
        self.repo.delete_file.side_effect = remove
        self.handler.delete_tool(self.data)
        self.repo.get_branch.assert_called_with(self.branch)

    def test_delete_resumes_when_branch_exists_but_file_was_not_deleted(self):
        delete_branch = self.branch + '__delete'
        self.repo.get_branches.return_value = [SimpleNamespace(name=delete_branch)]
        deleted = False

        def contents(path, ref):
            if deleted and ref == delete_branch:
                raise GithubException(404, {}, {})
            return SimpleNamespace(sha='original')

        def remove(**kwargs):
            nonlocal deleted
            deleted = True
            return {'deleted': True}

        self.repo.get_contents.side_effect = contents
        self.repo.delete_file.side_effect = remove
        _, pr = self.handler.delete_tool(self.data)
        self.assertEqual(pr.number, 42)
        self.repo.create_git_ref.assert_not_called()
        self.repo.delete_file.assert_called_once()

    def test_delete_recovers_after_file_was_removed(self):
        delete_branch = self.branch + '__delete'
        self.repo.get_branches.return_value = [SimpleNamespace(name=delete_branch)]
        self.repo.get_contents.side_effect = GithubException(404, {}, {})
        self.repo.compare.return_value.files = [SimpleNamespace(filename=self.path, status='removed')]
        _, pr = self.handler.delete_tool(self.data)
        self.assertEqual(pr.number, 42)
        self.repo.delete_file.assert_not_called()
        self.repo.create_pull.assert_called_once()
        existing = SimpleNamespace(number=9, head=SimpleNamespace(ref=delete_branch))
        self.repo.get_pulls.return_value = [existing]
        self.repo.create_pull.reset_mock()
        _, pr = self.handler.delete_tool(self.data)
        self.assertIs(pr, existing)
        self.repo.create_pull.assert_not_called()

    def test_delete_refuses_to_reuse_branch_with_unrelated_changes(self):
        self.repo.get_branches.return_value = [SimpleNamespace(name=self.branch + '__delete')]
        self.repo.get_contents.side_effect = GithubException(404, {}, {})
        self.repo.compare.return_value.files = [SimpleNamespace(filename='other.txt', status='removed')]
        with self.assertRaises(ToolDeleteException):
            self.handler.delete_tool(self.data)
        self.repo.delete_file.assert_not_called()
        self.repo.create_pull.assert_not_called()

    def test_delete_contents_server_error_falls_back_to_non_forced_git_commit(self):
        self.handler._GithubToolHandler__load_data(self.data, delete=True)
        self.repo.delete_file.side_effect = GithubException(500, {}, {})
        ref = self.repo.get_git_ref.return_value
        ref.object.sha = 'head'
        self.repo.get_git_commit.return_value = SimpleNamespace(sha='head', tree=SimpleNamespace(sha='tree'))
        self.repo.compare.return_value.files = []
        self.repo.get_contents.return_value = SimpleNamespace(sha='original')
        self.repo.create_git_commit.return_value = SimpleNamespace(sha='new-commit')
        self.handler._GithubToolHandler__delete_data(self.branch + '__delete', self.path, 'original')
        ref.edit.assert_called_once_with('new-commit', force=False)
        tree_item = self.repo.create_git_tree.call_args.args[0][0]
        self.assertEqual(tree_item._identity, {'path': self.path, 'mode': '100644', 'type': 'blob', 'sha': None})

    def test_delete_fallback_refuses_a_changed_blob(self):
        self.handler._GithubToolHandler__load_data(self.data, delete=True)
        self.repo.delete_file.side_effect = GithubException(500, {}, {})
        self.repo.get_git_ref.return_value.object.sha = 'head'
        self.repo.get_git_commit.return_value = SimpleNamespace(sha='head', tree=SimpleNamespace(sha='tree'))
        self.repo.compare.return_value.files = []
        self.repo.get_contents.return_value = SimpleNamespace(sha='changed')
        with self.assertRaises(ToolDeleteException):
            self.handler._GithubToolHandler__delete_data(self.branch + '__delete', self.path, 'original')
        self.repo.create_git_tree.assert_not_called()

    def test_failure_reaches_background_runner_for_retry(self):
        with patch('elixir.biotools_to_github.init_ecosystem_logger', return_value=None), \
             patch('elixir.biotools_to_github.handle_ecosystem_error') as report, \
             patch('elixir.biotools_to_github.GithubToolHandler', side_effect=GithubException(500, {}, {})):
            with self.assertRaises(GithubException):
                ecosytem_handle_tool_operations('Editor', self.data.tool_json, 'CREATE')
            report.assert_called_once()
