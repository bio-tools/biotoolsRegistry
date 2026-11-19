import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

import requests
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, override_settings

from elixir.management.commands.update_rsec_links import build_index, galaxy_links, write_index
from elixirapp.rsec import tool_links


SUMMARY = [
    {'tool_name': 'FastQC', 'contents': ['biotools', 'bioconda', 'biocontainers', 'debian', 'galaxy'],
     'fetched_metadata': {'bioconda': {'name': 'fastqc'}, 'biocontainers': {'name': 'fastqc'},
                          'debian': [{'name': 'fastqc'}, {'name': 'other'}]}},
    {'tool_name': 'unlinked', 'contents': ['bioconda'], 'fetched_metadata': {'bioconda': {'name': 'unlinked'}}},
    {'tool_name': 'no-links', 'contents': ['biotools'], 'fetched_metadata': {}},
]
BIOCONDA = '''@prefix schema: <http://schema.org/> .
<https://github.com/bioconda/bioconda-recipes/tree/master/recipes/fastqc> a schema:SoftwareApplication ;
  schema:identifier <biotools:fastqc>, <bioconda:fastqc>, <bioconda:fastqc-extra> .
<https://example.org/other> a schema:SoftwareApplication ; schema:identifier <biotools:unlinked>, <bioconda:other> .
'''
WORKFLOWS = '''@prefix schema: <http://schema.org/> .
<https://workflowhub.eu/workflows/42?version=2> a schema:ComputationalWorkflow ;
  schema:name "Quality control" ; schema:hasPart "fastqc", "unlinked" .
<https://example.org/workflows/3> a schema:ComputationalWorkflow ; schema:hasPart "fastqc" .
'''


class RsecLinksTests(SimpleTestCase):
    def test_summary_and_galaxy_links(self):
        galaxy = [{'bio.tool ID': 'fastqc', 'Suite ID': 'fastqc',
                   'Suite source': 'https://github.com/galaxyproject/tools-iuc/tree/main/tools/fastqc',
                   'Tool IDs': ['fastqc'], 'Number of tools on UseGalaxy.eu': 1,
                   'Number of tools on UseGalaxy.fr': 0}]
        index = build_index(SUMMARY, galaxy, BIOCONDA, WORKFLOWS)
        links = index['tools']['fastqc']
        self.assertEqual(links['Bioconda'][0]['url'], 'https://anaconda.org/bioconda/fastqc')
        self.assertEqual([item['label'] for item in links['Bioconda']], ['fastqc', 'fastqc-extra'])
        self.assertIn('quay.io/repository/biocontainers/fastqc', links['BioContainers'][0]['url'])
        self.assertEqual(len(links['Debian']), 2)
        self.assertTrue(any(link['url'] == 'https://usegalaxy.eu/?tool_id=fastqc' for link in links['Galaxy']))
        self.assertFalse(any('usegalaxy.fr' in link['url'] for link in links['Galaxy']))
        self.assertEqual(links['WorkflowHub'], [{'label': 'Quality control', 'url': 'https://workflowhub.eu/workflows/42?version=2'}])
        self.assertNotIn('unlinked', index['tools'])
        self.assertNotIn('no-links', index['tools'])

    def test_galaxy_requires_matching_identifier_and_does_not_guess_multiple_tools(self):
        galaxy = {'bio.tool ID': 'other', 'Suite source': 'https://github.com/example/tool',
                  'Tool IDs': ['one', 'two'], 'Number of tools on UseGalaxy.eu': 1}
        index = build_index(SUMMARY, [galaxy], BIOCONDA, WORKFLOWS)
        self.assertNotIn('Galaxy', index['tools']['fastqc'])
        self.assertNotIn('usegalaxy.eu', str(galaxy_links(galaxy)))
        galaxy['bio.tool ID'] = 'fastqc'
        second = {**galaxy, 'Suite source': 'https://github.com/example/another'}
        self.assertEqual(len(build_index(SUMMARY, [galaxy, second], BIOCONDA, WORKFLOWS)['tools']['fastqc']['Galaxy']), 2)

    def test_invalid_rdf_is_not_accepted(self):
        with self.assertRaises(ValueError):
            build_index(SUMMARY, [{'bio.tool ID': 'fastqc'}], BIOCONDA, 'not turtle')

    def test_failed_refresh_keeps_previous_index_and_reader_picks_up_new_file(self):
        with TemporaryDirectory() as directory, override_settings(RSEC_INDEX_PATH=directory + '/links.json'):
            path = Path(directory) / 'links.json'
            old = {'updated': '2026-01-01', 'tools': {'fastqc': {'Bioconda': [{'label': 'old', 'url': 'https://example.org'}]}}}
            write_index(old, path)
            self.assertEqual(tool_links('FASTQC')['services']['Bioconda'][0]['label'], 'old')
            with patch('elixir.management.commands.update_rsec_links.requests.get', side_effect=requests.ConnectionError('offline')):
                with self.assertRaises(CommandError):
                    call_command('update_rsec_links')
            self.assertEqual(json.loads(path.read_text()), old)
            response = Mock(json=Mock(return_value=SUMMARY))
            with patch('elixir.management.commands.update_rsec_links.requests.get', side_effect=[response, requests.ConnectionError('offline')]):
                with self.assertRaises(CommandError):
                    call_command('update_rsec_links')
            self.assertEqual(json.loads(path.read_text()), old)
            summary = Path(directory) / 'summary.json'
            galaxy = Path(directory) / 'galaxy.json'
            bioconda = Path(directory) / 'bioconda.ttl'
            workflows = Path(directory) / 'workflows.ttl'
            summary.write_text(json.dumps(SUMMARY))
            galaxy.write_text(json.dumps([{'bio.tool ID': 'fastqc'}]))
            bioconda.write_text(BIOCONDA)
            workflows.write_text('invalid turtle')
            with self.assertRaises(CommandError):
                call_command('update_rsec_links', summary=str(summary), galaxy=str(galaxy), bioconda=str(bioconda), workflows=str(workflows))
            self.assertEqual(json.loads(path.read_text()), old)
            old['tools']['fastqc']['Bioconda'][0]['label'] = 'updated'
            write_index(old, path)
            self.assertEqual(tool_links('fastqc')['services']['Bioconda'][0]['label'], 'updated')
