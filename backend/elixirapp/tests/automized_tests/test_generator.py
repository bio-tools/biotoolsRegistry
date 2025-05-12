from backend.elixir.tool_helper import ToolHelper
from .schema_parser import SchemaParser

import rstr
import string
import random
import copy
import re

MIN_LENGTH = "minLength"
MAX_LENGTH = "maxLength"
ENUM = "enum"
PATTERN = "pattern"
ANY_OF = "anyOf"

INVALID = "invalid"
VALID = "valid"
VALUE_DICT_BASE = {VALID: [], INVALID: []}

DEFAULT_BASE_STRING = "TEST"
EMPTY_STRING = ""


class TestGenerator:
    def __init__(self):
        parser = SchemaParser()
        self.test_dict = parser.create_restriction_dict()

    def test_all(self):
        self.test_string()
        # TODO array & ev. object

    def test_string(self):
        string_test_dict = self.test_dict["string"]

        input_tool = ToolHelper.get_input_tool()  # TODO insert into tool

        for attr_name, attr_constraints in zip(string_test_dict.keys(), string_test_dict.values()):
            print(attr_name)
            self.create_string_values(attr_constraints)

    def create_string_values(self, constraint_dict: dict):
        value_dict = copy.deepcopy(VALUE_DICT_BASE)
        base_string = DEFAULT_BASE_STRING

        if PATTERN in constraint_dict:
            pattern = constraint_dict[PATTERN]
            base_string = self.create_string_matching_pattern(pattern)
            self.create_pattern_test_values(pattern, value_dict)

        if MIN_LENGTH in constraint_dict:
            minLength_value = constraint_dict[MIN_LENGTH]
            self.create_minLength_test_values(minLength_value, base_string, value_dict)

        if MAX_LENGTH in constraint_dict:
            maxLength_value = constraint_dict[MAX_LENGTH]
            self.create_maxLength_test_values(maxLength_value, base_string, value_dict)

        if ENUM in constraint_dict:
            allowed_values = constraint_dict[ENUM]
            self.create_enum_test_values(allowed_values, value_dict)

        if ANY_OF in constraint_dict:
            patterns = constraint_dict[ANY_OF]
            self.create_anyOf_test_values(patterns, value_dict)

        print(value_dict)

    # PATTERN ----------------------------------------------------------------------------------------------------------
    def create_string_matching_pattern(self, pattern: str):
        return rstr.xeger(pattern)

    def create_invalid_string_for_pattern(self, input_string: str, pattern: str):
        if not pattern:  # TODO maybe handle empty pattern
            return DEFAULT_BASE_STRING

        compiled_pattern = re.compile(pattern)
        s = input_string
        while True:
            index = random.randint(0, len(s) - 1)
            char_at_index = s[index]
            corrupted_char = random.choice(string.punctuation)
            s = s[:index] + corrupted_char + s[index + 1:]
            if not compiled_pattern.fullmatch(s):
                return s
            else:
                s = s.replace(corrupted_char, char_at_index)

    def create_pattern_test_values(self, pattern: str, value_dict: dict):
        valid_string = self.create_string_matching_pattern(pattern)
        value_dict[VALID].append(valid_string)

        invalid_string = self.create_invalid_string_for_pattern(valid_string, pattern)
        value_dict[INVALID].append(invalid_string)

    # ANY OF -----------------------------------------------------------------------------------------------------------
    def create_anyOf_test_values(self, patterns: list, value_dict: dict):
        for pattern in patterns:
            self.create_pattern_test_values(pattern[PATTERN], value_dict)

    # ENUM -------------------------------------------------------------------------------------------------------------
    def create_enum_test_values(self, valid_values: list, value_dict: dict):
        value_dict[VALID].append(random.choice(valid_values))
        value_dict[INVALID].extend([DEFAULT_BASE_STRING])

    # MIN LENGTH -------------------------------------------------------------------------------------------------------
    def create_minLength_test_values(self, min_length: int, base_str: str, value_dict: dict):
        multiplication_factor = min_length % len(base_str) + 1
        valid_string = base_str * multiplication_factor
        value_dict[VALID].append(valid_string)

        invalid_string = base_str[:min_length-1]
        value_dict[INVALID].append(invalid_string)

    # MAX LENGTH -------------------------------------------------------------------------------------------------------
    def create_maxLength_test_values(self, max_length: int, base_str: str, value_dict: dict):
        multiplication_factor = int(max_length/len(base_str))
        invalid_string = base_str * (multiplication_factor + 1)
        value_dict[INVALID].append(invalid_string)

        valid_string = invalid_string[:max_length-1]
        value_dict[VALID].append(valid_string)


testgen = TestGenerator()
testgen.test_all()
