"""Build a local JSON index from the public RSEc Atlas metadata."""
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlencode, urlsplit

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from rdflib import Graph, Literal, Namespace, RDF, URIRef


ATLAS = 'https://research-software-ecosystem.org/RSEc-Atlas/metadata/'
GALAXY_DATA = 'https://raw.githubusercontent.com/galaxyproject/galaxy_codex/main/communities/all/resources/tools.json'
RSEC_DATASETS = 'https://raw.githubusercontent.com/research-software-ecosystem/content/master/datasets/'
SCHEMA = Namespace('http://schema.org/')
SAFE_NAME = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._+-]{0,199}$')
GALAXY_SERVERS = {'UseGalaxy.eu': 'usegalaxy.eu', 'UseGalaxy.org (Main)': 'usegalaxy.org',
                  'UseGalaxy.org.au': 'usegalaxy.org.au', 'UseGalaxy.be': 'usegalaxy.be',
                  'UseGalaxy.cz': 'usegalaxy.cz', 'UseGalaxy.fr': 'usegalaxy.fr', 'UseGalaxy.no': 'usegalaxy.no'}


def name(value):
    return value if isinstance(value, str) and SAFE_NAME.fullmatch(value) else None


def add(links, service, label, url):
    entries = links.setdefault(service, [])
    if not any(entry['url'] == url for entry in entries):
        entries.append({'label': label, 'url': url})


def summary_links(record):
    metadata = record.get('fetched_metadata') or {}
    links = {}
    for source, label, pattern in (
        ('bioconda', 'Bioconda', 'https://anaconda.org/bioconda/{}'),
        ('biocontainers', 'BioContainers', 'https://quay.io/repository/biocontainers/{}?tab=tags'),
        ('debian', 'Debian', 'https://tracker.debian.org/pkg/{}'),
        ('bioconductor', 'Bioconductor', 'https://bioconductor.org/packages/{}/'),
    ):
        values = metadata.get(source) or []
        if isinstance(values, dict):
            values = [values]
        if not isinstance(values, list):
            continue
        for value in values:
            identifier = name(value.get('name')) if isinstance(value, dict) else None
            if identifier:
                add(links, label, identifier, pattern.format(quote(identifier, safe='')))
    return links


def galaxy_links(record):
    links = {}
    suite = name(record.get('Suite ID')) or 'Galaxy tool'
    source = record.get('Suite source')
    parsed = urlsplit(source) if isinstance(source, str) else None
    if parsed and parsed.scheme == 'https' and parsed.hostname == 'github.com':
        add(links, 'Galaxy', suite + ' source', source)
    ids = record.get('Tool IDs') or []
    if isinstance(ids, list) and len(ids) == 1 and name(ids[0]):
        for server, host in GALAXY_SERVERS.items():
            count = record.get('Number of tools on ' + server)
            if isinstance(count, (int, float)) and count > 0:
                add(links, 'Galaxy', host + ' · ' + ids[0], 'https://' + host + '/?' + urlencode({'tool_id': ids[0]}))
    return links


def rdf_graph(data):
    graph = Graph()
    try:
        graph.parse(data=data, format='turtle')
    except (ValueError, SyntaxError) as exc:
        raise ValueError('Invalid RSEc RDF dataset') from exc
    if not graph:
        raise ValueError('RSEc RDF dataset is empty')
    return graph


def add_bioconda(tools, known_ids, data):
    graph = rdf_graph(data)
    for subject in graph.subjects(RDF.type, SCHEMA.SoftwareApplication):
        identifiers = [str(value) for value in graph.objects(subject, SCHEMA.identifier)]
        packages = [name(value.removeprefix('bioconda:')) for value in identifiers if value.startswith('bioconda:')]
        for value in identifiers:
            if value.startswith('biotools:'):
                identifier = name(value.removeprefix('biotools:'))
            elif value.startswith('https://bio.tools/'):
                identifier = name(value.removeprefix('https://bio.tools/'))
            else:
                continue
            if identifier and identifier.casefold() in known_ids:
                for package in filter(None, packages):
                    add(tools.setdefault(identifier.casefold(), {}), 'Bioconda', package,
                        'https://anaconda.org/bioconda/' + quote(package, safe=''))


def add_workflows(tools, known_ids, data):
    graph = rdf_graph(data)
    for workflow in graph.subjects(RDF.type, SCHEMA.ComputationalWorkflow):
        url = str(workflow)
        if not isinstance(workflow, URIRef) or not re.fullmatch(r'https://workflowhub\.eu/workflows/[0-9]+(?:\?version=[0-9]+)?', url):
            continue
        label = str(graph.value(workflow, SCHEMA.name) or 'Workflow')[:200]
        for value in graph.objects(workflow, SCHEMA.hasPart):
            identifier = name(str(value)) if isinstance(value, Literal) else None
            if identifier and identifier.casefold() in known_ids:
                add(tools.setdefault(identifier.casefold(), {}), 'WorkflowHub', label, url)


def build_index(records, galaxy_records, bioconda_data, workflow_data):
    if not isinstance(records, list) or not isinstance(galaxy_records, list) or not galaxy_records:
        raise ValueError('RSEc and Galaxy metadata must be nonempty lists')
    tools, known_ids = {}, set()
    for record in records:
        if not isinstance(record, dict) or 'biotools' not in (record.get('contents') or []):
            continue
        identifier = name(record.get('tool_name'))
        if not identifier:
            continue
        known_ids.add(identifier.casefold())
        links = summary_links(record)
        if links:
            tools[identifier.casefold()] = links
    if not tools:
        raise ValueError('RSEc summary contains no usable bio.tools associations')
    for record in galaxy_records:
        if not isinstance(record, dict):
            continue
        identifier = name(record.get('bio.tool ID'))
        if not identifier or identifier.casefold() not in known_ids:
            continue
        for service, links in galaxy_links(record).items():
            for link in links:
                add(tools.setdefault(identifier.casefold(), {}), service, link['label'], link['url'])
    add_bioconda(tools, known_ids, bioconda_data)
    add_workflows(tools, known_ids, workflow_data)
    for services in tools.values():
        for links in services.values():
            links.sort(key=lambda item: (item['label'].casefold(), item['url']))
    return {'updated': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'tools': tools}


def write_index(index, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as output:
            temporary = output.name
            json.dump(index, output, ensure_ascii=False, separators=(',', ':'), sort_keys=True)
        os.chmod(temporary, 0o644)
        os.replace(temporary, path)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


class Command(BaseCommand):
    help = 'Refresh the local RSEc service-link index.'
    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument('--summary', help='Read a local Atlas summary JSON instead of downloading it.')
        parser.add_argument('--galaxy', help='Read local Galaxy CoDex JSON instead of downloading it.')
        parser.add_argument('--bioconda', help='Read a local RSEc Bioconda Turtle dataset.')
        parser.add_argument('--workflows', help='Read a local RSEc WorkflowHub Turtle dataset.')

    def handle(self, *args, **options):
        try:
            if options['summary']:
                with open(options['summary'], encoding='utf-8') as source:
                    records = json.load(source)
            else:
                response = requests.get(ATLAS + 'combined_metadata.json', timeout=(10, 180))
                response.raise_for_status()
                records = response.json()
            if options['galaxy']:
                with open(options['galaxy'], encoding='utf-8') as source:
                    galaxy_records = json.load(source)
            else:
                response = requests.get(GALAXY_DATA, timeout=(10, 180))
                response.raise_for_status()
                galaxy_records = response.json()
            datasets = []
            for option, filename in (('bioconda', 'bioconda-dump.ttl'), ('workflows', 'workflowhub-dump.ttl')):
                if options[option]:
                    datasets.append(Path(options[option]).read_text(encoding='utf-8'))
                else:
                    response = requests.get(RSEC_DATASETS + filename, timeout=(10, 180))
                    response.raise_for_status()
                    datasets.append(response.text)
            index = build_index(records, galaxy_records, *datasets)
            write_index(index, settings.RSEC_INDEX_PATH)
        except (OSError, ValueError, requests.RequestException) as exc:
            raise CommandError('RSEc refresh failed; the previous index was kept: ' + str(exc)) from exc
        self.stdout.write(f"RSEc links updated for {len(index['tools'])} tools.")
