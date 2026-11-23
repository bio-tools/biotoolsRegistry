"""Small read-only latency baseline for a local, database-backed preview."""
import argparse
import json
import math
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


ROUTES = {
    'home': '/',
    'search_fastqc': '/_search/data/?q=fastqc&per_page=25',
    'search_sequence': '/_search/data/?q=sequence%20analysis&per_page=25',
    'tool_detail': '/fastqc',
    'workflows': '/workflows',
    'statistics': '/stats',
}


def request(url):
    started = time.perf_counter()
    try:
        with urlopen(Request(url, headers={'User-Agent': 'biotools-local-benchmark'}), timeout=15) as response:
            response.read()
            status = response.status
    except HTTPError as exc:
        status = exc.code
    except (TimeoutError, URLError):
        status = 0
    return {'status': status, 'ms': round((time.perf_counter() - started) * 1000, 1)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', default='http://localhost:8005')
    parser.add_argument('--samples', type=int, default=20, choices=range(1, 31), metavar='1-30')
    args = parser.parse_args()
    if urlsplit(args.base_url).hostname not in ('localhost', '127.0.0.1', '::1'):
        parser.error('Use a local preview, not a remote server.')
    base = args.base_url.rstrip('/')
    results = {}
    for name, route in ROUTES.items():
        request(base + route)  # Warm the local page and caches.
        samples = [request(base + route) for _ in range(args.samples)]
        timings = sorted(item['ms'] for item in samples)
        results[name] = {'samples': len(samples), 'p95_ms': timings[math.ceil(len(timings) * .95) - 1],
                         'max_ms': timings[-1], 'failures': [item['status'] for item in samples if item['status'] != 200]}
    with ThreadPoolExecutor(max_workers=4) as pool:
        concurrent = list(pool.map(request, [base + ROUTES['search_sequence']] * 4))
    results['four_concurrent_searches'] = concurrent
    print(json.dumps(results, indent=2))
    if any(item.get('failures') for item in results.values() if isinstance(item, dict)) or any(item['status'] != 200 for item in concurrent):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
