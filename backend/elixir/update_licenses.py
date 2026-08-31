#!/usr/bin/env python3
"""Refresh the generated SPDX block in licenses.py from the official list.

    python update_licenses.py            # fetch and rewrite
    python update_licenses.py --check    # report drift, change nothing

Only the block between the BEGIN/END markers is rewritten. The curated sets in
that file, DEPRECATED_SPDX_LICENSES and NON_SPDX_LICENSES, are left alone: a
retired identifier has to stay accepted for as long as records still use it, and
that is a judgement call rather than something to regenerate.
"""

import argparse
import json
import pathlib
import re
import sys
import urllib.request

SPDX_URL = "https://raw.githubusercontent.com/spdx/license-list-data/main/json/licenses.json"
LICENSES_PY = pathlib.Path(__file__).with_name("licenses.py")
BEGIN = "# --- BEGIN GENERATED SPDX LIST (update_licenses.py rewrites this block) ---"
END = "# --- END GENERATED SPDX LIST ---"


def fetch_spdx():
    with urllib.request.urlopen(SPDX_URL, timeout=60) as response:
        data = json.load(response)
    current = sorted(
        entry["licenseId"]
        for entry in data["licenses"]
        if not entry.get("isDeprecatedLicenseId")
    )
    return data.get("licenseListVersion", "unknown"), current


def render(version, ids):
    body = "\n".join(f'        "{i}",' for i in ids)
    return f"""{BEGIN}
SPDX_LICENSES = frozenset(
    {{
{body}
    }}
)
{END}"""


def check_case_collisions(source):
    """ENUMValidator rejects a value matching more than one entry case-insensitively."""
    values = re.findall(r'^\s+"([^"]+)",$', source, re.M)
    seen = {}
    clashes = []
    for value in values:
        key = value.lower()
        if key in seen:
            clashes.append((seen[key], value))
        seen[key] = value
    return clashes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="report whether the file is out of date, without writing",
    )
    args = parser.parse_args()

    version, ids = fetch_spdx()
    source = LICENSES_PY.read_text()
    start, end = source.index(BEGIN), source.index(END) + len(END)
    existing = set(re.findall(r'^\s+"([^"]+)",$', source[start:end], re.M))

    added, removed = sorted(set(ids) - existing), sorted(existing - set(ids))
    print(f"SPDX licence list {version}: {len(ids)} current identifiers")
    print(f"  in licenses.py: {len(existing)}")
    for label, group in (("would add", added), ("would drop", removed)):
        if group:
            shown = ", ".join(group[:8]) + (" ..." if len(group) > 8 else "")
            print(f"  {label} {len(group)}: {shown}")
    if not added and not removed:
        print("  already up to date")
        return 0
    if args.check:
        return 1

    updated = source[:start] + render(version, ids) + source[end:]
    updated = re.sub(
        r"Generated from SPDX licence list [^\n.]*\.",
        f"Generated from SPDX licence list {version}.",
        updated,
    )
    clashes = check_case_collisions(updated)
    if clashes:
        sys.exit(
            "refusing to write: identifiers differing only by case would make "
            f"both unusable in ENUMValidator: {clashes}"
        )
    LICENSES_PY.write_text(updated)
    print(f"  rewrote {LICENSES_PY.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
