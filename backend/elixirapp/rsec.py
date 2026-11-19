"""Local, read-only links imported from the RSEc Atlas."""
import json
from functools import lru_cache
from pathlib import Path

from django.conf import settings


@lru_cache(maxsize=2)
def _read_index(path, modified, size):
    with open(path, encoding='utf-8') as source:
        data = json.load(source)
    if not isinstance(data, dict) or not isinstance(data.get('tools'), dict):
        raise ValueError('Invalid RSEc index')
    return data


def tool_links(identifier):
    path = Path(settings.RSEC_INDEX_PATH)
    try:
        stat = path.stat()
        data = _read_index(str(path), stat.st_mtime_ns, stat.st_size)
        links = data['tools'].get(identifier.casefold(), {})
        return {'updated': data.get('updated', ''), 'services': links} if links else None
    except (OSError, ValueError, TypeError):
        return None
