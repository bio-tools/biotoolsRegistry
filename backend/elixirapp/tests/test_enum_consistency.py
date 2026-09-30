"""Consistency tests between backend enums and frontend dropdown options.

The backend validates controlled-vocabulary fields with ``ENUMValidator`` calls
that live inside the serializer modules under
``elixir/serialization/resource_serialization/`` (plus ``ALLOWED_LICENSES`` in
``elixir/licenses.py``).  The frontend exposes the same vocabularies as
dropdown options in ``frontend/js/controllers.js`` (``$scope.xxxOptions``).

These tests parse both sides statically (via ``ast`` / regex) and fail whenever
the two drift apart, e.g. when a value is added to the backend but the frontend
dropdown is not updated (or vice versa).

Run with: ``python manage.py test elixirapp.tests.test_enum_consistency``
"""

import ast
import re
from pathlib import Path

from django.test import SimpleTestCase

from elixir.licenses import ALLOWED_LICENSES

BACKEND_DIR = (
    Path(__file__).resolve().parents[2] / "elixir" / "serialization" / "resource_serialization"
)
FRONTEND_CONTROLLERS = Path(__file__).resolve().parents[3] / "frontend" / "js" / "controllers.js"

# (frontend array name in controllers.js,
#  backend serializer file,
#  backend class name,
#  backend method holding the ENUMValidator call)
FRONTEND_TO_BACKEND = [
    ("languageOptions", "language.py", "LanguageSerializer", "to_internal_value"),
    ("toolTypeOptions", "toolType.py", "ToolTypeSerializer", "to_internal_value"),
    ("platformOptions", "operatingSystem.py", "OperatingSystemSerializer", "to_internal_value"),
    ("linkTypeOptions", "link.py", "LinkTypeSerializer", "to_internal_value"),
    ("downloadTypeOptions", "download.py", "DownloadSerializer", "validate_type"),
    ("documentationTypeOptions", "documentation.py", "DocumentationTypeSerializer", "to_internal_value"),
    ("publicationTypeOptions", "publication.py", "PublicationTypeSerializer", "to_internal_value"),
    ("entityTypeOptions", "credit.py", "CreditSerializer", "validate_typeEntity"),
    ("roleTypeOptions", "credit.py", "CreditTypeRoleSerializer", "to_internal_value"),
    ("elixirPlatformOptions", "resource.py", "ElixirPlatformSerializer", "to_internal_value"),
    ("elixirNodeOptions", "resource.py", "ElixirNodeSerializer", "to_internal_value"),
    ("elixirCommunityOptions", "resource.py", "ElixirCommunitySerializer", "to_internal_value"),
    ("relationTypeOptions", "resource.py", "RelationSerializer", "validate_type"),
    ("confidenceOptions", "resource.py", "ResourceSerializer", "validate_confidence_flag"),
    ("costOptions", "resource.py", "ResourceSerializer", "validate_cost"),
    ("maturityOptions", "resource.py", "ResourceSerializer", "validate_maturity"),
    ("accessibilityOptions", "resource.py", "ResourceSerializer", "validate_accessibility"),
]

# Deliberately NOT compared:
# - otherIdTypeOptions: the backend also accepts 'biotoolsCURIE', which is
#   admin-only and intentionally hidden from the frontend dropdown.
#
# NOTE: ENUMValidator matches case-insensitively, so the comparison below is
# case-insensitive too. There is a known cosmetic casing drift for the
# download type 'VM Image' (frontend) vs 'VM image' (backend).


def _extract_enum(source, class_name, method_name):
    """Return the list of allowed values from an ENUMValidator call."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not (isinstance(node, ast.ClassDef) and node.name == class_name):
            continue
        for item in ast.walk(node):
            if not (isinstance(item, ast.FunctionDef) and item.name == method_name):
                continue
            for call in ast.walk(item):
                if (
                    isinstance(call, ast.Call)
                    and isinstance(call.func, ast.Name)
                    and call.func.id == "ENUMValidator"
                    and call.args
                ):
                    arg = call.args[0]
                    if isinstance(arg, (ast.List, ast.Tuple)):
                        return [
                            elt.value
                            for elt in arg.elts
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                        ]
    raise AssertionError(
        f"No ENUMValidator list found in {class_name}.{method_name} "
        f"(looked in {BACKEND_DIR})"
    )


def _backend_enum(filename, class_name, method_name):
    source = (BACKEND_DIR / filename).read_text()
    return _extract_enum(source, class_name, method_name)


def _frontend_options(array_name):
    """Return the 'value' entries of a $scope.<array_name> = [...] list."""
    text = FRONTEND_CONTROLLERS.read_text()
    match = re.search(
        r"\$scope\." + re.escape(array_name) + r"\s*=\s*\[(.*?)\];",
        text,
        re.DOTALL,
    )
    if not match:
        raise AssertionError(f"Array '{array_name}' not found in {FRONTEND_CONTROLLERS}")
    return re.findall(r"value:\s*'((?:[^'\\]|\\.)*)'", match.group(1))


class TestEnumConsistency(SimpleTestCase):
    """Backend and frontend controlled vocabularies must stay in sync."""

    def _assert_same_set(self, frontend_name, backend_values, frontend_values):
        # ENUMValidator matches case-insensitively, so compare that way too.
        backend_set = {v.lower() for v in backend_values}
        frontend_set = {v.lower() for v in frontend_values}

        self.assertEqual(
            backend_set,
            frontend_set,
            f"Enum mismatch for '{frontend_name}':\n"
            f"  in backend but not frontend: {sorted(backend_set - frontend_set)}\n"
            f"  in frontend but not backend: {sorted(frontend_set - backend_set)}",
        )

    def test_frontend_file_exists(self):
        self.assertTrue(FRONTEND_CONTROLLERS.is_file(), f"{FRONTEND_CONTROLLERS} is missing")

    def test_enum_consistency(self):
        for frontend_name, filename, class_name, method_name in FRONTEND_TO_BACKEND:
            with self.subTest(enum=frontend_name):
                backend_values = _backend_enum(filename, class_name, method_name)
                frontend_values = _frontend_options(frontend_name)
                self._assert_same_set(frontend_name, backend_values, frontend_values)

    def test_license_consistency(self):
        # The backend license vocabulary is generated in elixir/licenses.py
        # (see that module before editing); the frontend mirrors it in
        # licenseOptions, plus its own header values.
        frontend_values = _frontend_options("licenseOptions")
        self._assert_same_set("licenseOptions", ALLOWED_LICENSES, frontend_values)
