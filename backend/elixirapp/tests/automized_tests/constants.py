# --------------- GENERAL ---------------

INVALID = "invalid"
VALID = "valid"
STRING = "string"
ARRAY = "array"
OBJECT = "object"
REF_INFO = "ref_info"

DEFINITIONS = "definitions"
PROPERTIES = "properties"
ITEMS = "items"
TOOL = "tool"
REF = "$ref"
TYPE = "type"

LEFT_OUT_PATHS = [
    "topic",
    "function",
    "rorid",
    "orcidid",
    "fundrefid",
    "otherID",
    "url",
    "credit/email",
    "relation",
    "publication",
    "homepage",
    "biotoolsCURIE",
]

# --------- DICTIONARY TEMPLATES --------

VALUE_DICT_BASE = {VALID: [], INVALID: []}

TYPE_DICT = {
    STRING: ["minLength", "maxLength", "enum", "pattern", "anyOf", "examples"],
    ARRAY: ["minItems", "maxItems"],
    OBJECT: ["additionalProperties", "required"],
}

# ---------- STRING ATTRIBUTES ----------

MIN_LENGTH = "minLength"
MAX_LENGTH = "maxLength"
ENUM = "enum"
PATTERN = "pattern"
ANY_OF = "anyOf"
EXAMPLES = "examples"

# ------------ STRING VALUES ------------

DEFAULT_BASE_STRING = "TEST"
EMPTY_STRING = ""

# ----------- ARRAY ATTRIBUTES ----------

MIN_ITEMS = "minItems"
MAX_ITEMS = "maxItems"

# ------------ OBJECT VALUES ------------

DEFAULT_KEY = "someKey"
DEFAULT_VALUE = "someValue"
DEFAULT_KVP = {DEFAULT_KEY: DEFAULT_VALUE}

# ---------- OBJECT ATTRIBUTES ----------

ADDITIONAL_PROPERTIES = "additionalProperties"
REQUIRED = "required"
