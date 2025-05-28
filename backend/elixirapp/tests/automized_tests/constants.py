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

EDAM_DATA = "EDAMdata"
EDAM_FORMAT = "EDAMformat"

# --------- DICTIONARY TEMPLATES --------

VALUE_DICT_BASE = {VALID: [], INVALID: []}

TYPE_DICT = {
    STRING: ["minLength", "maxLength", "enum", "pattern", "anyOf", "examples"],
    ARRAY: ["minItems", "maxItems"],
    OBJECT: ["additionalProperties", "required"]
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

VALID_EDAM_DATA = {
    "uri": "http://edamontology.org/data_3917",
    "term": "Count matrix"
}

INVALID_EDAM_DATA = {
    "uri": "http://edamontology.org/data_3917",
    "term": "INVALID DATA"
}

VALID_EDAM_FORMAT = {
    "uri": "http://edamontology.org/format_3989",
    "term": "GZIP format"
}

INVALID_EDAM_FORMAT = {
    "uri": "http://edamontology.org/format_3989",
    "term": "INVALID FORMAT"
}

VALID_EDAM_OPERATION = {
    "uri": "http://edamontology.org/operation_3800",
    "term": "RNA-Seq quantification"
}

INVALID_EDAM_OPERATION = {
    "uri": "http://edamontology.org/operation_3800",
    "term": "INVALID OPERATION"
}

VALID_EDAM_TOPIC = {
    "uri": "http://edamontology.org/topic_0659",
    "term": "Functional, regulatory and non-coding RNA"
}

INVALID_EDAM_TOPIC = {
    "uri": "http://edamontology.org/topic_0659",
    "term": "INVALID TOPIC"
}

EDGE_CASE_PATHS = {
    'function/operation': {
        VALID: VALID_EDAM_OPERATION,
        INVALID: INVALID_EDAM_OPERATION
    },
    'topic': {
        VALID: VALID_EDAM_TOPIC,
        INVALID: INVALID_EDAM_TOPIC
    }
}

# ---------- OBJECT ATTRIBUTES ----------

ADDITIONAL_PROPERTIES = "additionalProperties"
REQUIRED = "required"
