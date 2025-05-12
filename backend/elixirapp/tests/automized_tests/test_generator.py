import random

from backend.elixir.tool_helper import ToolHelper
from .schema_parser import SchemaParser
import rstr
import random
import copy
import string
import re

MIN_LENGTH = "minLength"    # done
MAX_LENGTH = "maxLength"    # done
ENUM = "enum"               # done
PATTERN = "pattern"         # TODO
ANY_OF = "anyOf"            # can use pattern implementation

test_dict = {}

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
        # TODO array

    def test_string(self):
        string_test_dict = self.test_dict["string"]

        input_tool = ToolHelper.get_input_tool()

        for attr_name, attr_constraints in zip(string_test_dict.keys(), string_test_dict.values()):
            print(attr_name)
            self.create_string_values(attr_constraints)

    def create_string_values(self, constraint_dict: dict):
        value_dict = copy.deepcopy(VALUE_DICT_BASE)
        base_string = DEFAULT_BASE_STRING

        if PATTERN in constraint_dict:
            pattern = constraint_dict[PATTERN]
            base_string = self.create_string_matching_pattern(pattern)
            # self.create_pattern_test_values(pattern, value_dict)

        if MIN_LENGTH in constraint_dict:
            minLength_value = constraint_dict[MIN_LENGTH]
            self.create_minLength_test_values(minLength_value, base_string, value_dict)

        if MAX_LENGTH in constraint_dict:
            maxLength_value = constraint_dict[MAX_LENGTH]
            self.create_maxLength_test_values(maxLength_value, base_string, value_dict)

        if ENUM in constraint_dict:
            self.create_enum_test_values(constraint_dict[ENUM], value_dict)
            None

        if ANY_OF in constraint_dict:
            None

        print(value_dict)


    # PATTERN ----------------------------------------------------------------------------------------------------------
    def create_string_matching_pattern(self, pattern: str):
        return rstr.xeger(pattern)

    def create_invalid_string_for_pattern(self, input_string: str, pattern: str):
        if not pattern:  # TODO handle empty pattern
            return DEFAULT_BASE_STRING

        compiled_pattern = re.compile(pattern)
        s = input_string
        while True:
            index = random.randint(0, len(s) - 1)
            char_at_index = s[index]
            corrupted_char = 'x' if s[index].isdigit() else '1'
            s = s[:index] + corrupted_char + s[index + 1:]
            print(f"trying {s} for pattern {pattern}")
            if not compiled_pattern.fullmatch(s):
                return s
            else:
                s = s.replace(corrupted_char, char_at_index)

    def manipulate_string_by_pattern(self, input_string: str, pattern: str):
        None

    def create_pattern_test_values(self, pattern: str, value_dict: dict):
        valid_string = self.create_string_matching_pattern(pattern)
        value_dict[VALID] = valid_string

        invalid_string = self.create_invalid_string_for_pattern(valid_string, pattern)

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
