"""Opt-in public API crawl; retain only anonymous function annotation URIs."""
import argparse
import json
import math
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


API = 'https://bio.tools/api/t?format=json&per_page=100&page={}'


def read_page(page):
    for attempt in range(3):
        try:
            with urlopen(Request(API.format(page), headers={'User-Agent': 'bio.tools-migration-corpus/1.0'}), timeout=30) as response:
                return json.load(response)
        except (HTTPError, URLError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def uri(value):
    if not isinstance(value, dict):
        raise ValueError('Unexpected ontology annotation shape.')
    result = value.get('uri')
    if result is not None and not isinstance(result, str):
        raise ValueError('Unexpected ontology URI shape.')
    return {'uri': result}


def anonymous(tool):
    functions = []
    for function in tool.get('function') or []:
        entry = {'operation': [uri(item) for item in function.get('operation') or []]}
        for direction in ('input', 'output'):
            entry[direction] = [
                {'data': uri(item.get('data') or {}), 'format': [uri(fmt) for fmt in item.get('format') or []]}
                for item in function.get(direction) or []
            ]
        functions.append(entry)
    return {'functions': functions}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--all', action='store_true', required=True, help='Explicitly opt into the whole public registry crawl.')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    started = datetime.now(timezone.utc).isoformat()
    first = read_page(1)
    initial_count = first['count']
    pages = math.ceil(initial_count / 100)
    if not 0 < pages <= 1000:
        raise ValueError('Unexpected registry size; stop and review before continuing.')
    seen, corpus, duplicates = set(), [], 0
    for page in range(1, pages + 1):
        data = first if page == 1 else read_page(page)
        if not isinstance(data.get('list'), list):
            raise ValueError('Unexpected public API response.')
        for tool in data['list']:
            identifier = tool.get('biotoolsID')
            if not isinstance(identifier, str) or not identifier:
                raise ValueError('A public resource has no identifier.')
            key = identifier.casefold()
            if key in seen:
                duplicates += 1
                continue
            seen.add(key)
            corpus.append(anonymous(tool))
        if page % 25 == 0 or page == pages:
            print(f'Pages {page}/{pages}; unique records {len(corpus)}; duplicates {duplicates}', flush=True)
        time.sleep(0.3)
    final_count = read_page(1)['count']
    counts = Counter()
    for tool in corpus:
        counts['resources'] += 1
        counts['resources_with_functions'] += bool(tool['functions'])
        counts['resources_with_multiple_functions'] += len(tool['functions']) > 1
        for function in tool['functions']:
            counts['functions'] += 1
            counts['functions_without_operation'] += not any(item['uri'] for item in function['operation'])
            for direction in ('input', 'output'):
                counts['functions_without_' + direction] += not function[direction]
                counts['multiple_' + direction] += len(function[direction]) > 1
                for item in function[direction]:
                    counts[direction + '_records'] += 1
                    counts[direction + '_without_data'] += not item['data']['uri']
                    counts[direction + '_without_format'] += not any(fmt['uri'] for fmt in item['format'])
    args.output.write_text(json.dumps(corpus, separators=(',', ':')))
    metadata = {'started': started, 'finished': datetime.now(timezone.utc).isoformat(),
                'initial_count': initial_count, 'final_count': final_count, 'pages': pages,
                'duplicates': duplicates, 'counts': dict(counts),
                'note': 'Live paginated crawl; concurrent edits can cause omissions even when counts are unchanged.'}
    args.output.with_suffix('.metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(json.dumps(metadata, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
