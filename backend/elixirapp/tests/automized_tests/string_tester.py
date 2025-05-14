import rstr
import string
import random
import copy
import re
from .constants import INVALID, VALID, PATTERN, MIN_LENGTH, MAX_LENGTH, ENUM, VALUE_DICT_BASE, DEFAULT_BASE_STRING, ANY_OF, EXAMPLES


class StringTester:
    @staticmethod
    def create_string_values(constraint_dict: dict):
        value_dict = copy.deepcopy(VALUE_DICT_BASE)
        base_string = DEFAULT_BASE_STRING

        if PATTERN in constraint_dict:
            pattern = constraint_dict[PATTERN]
            base_string = StringTester.get_example_string(constraint_dict, pattern)
            StringTester.create_pattern_test_values(pattern, value_dict, base_string)

        if MIN_LENGTH in constraint_dict:
            minLength_value = constraint_dict[MIN_LENGTH]
            StringTester.create_minLength_test_values(minLength_value, base_string, value_dict)

        if MAX_LENGTH in constraint_dict:
            maxLength_value = constraint_dict[MAX_LENGTH]
            StringTester.create_maxLength_test_values(maxLength_value, base_string, value_dict)

        if ENUM in constraint_dict:
            allowed_values = constraint_dict[ENUM]
            StringTester.create_enum_test_values(allowed_values, value_dict)

        if ANY_OF in constraint_dict:
            patterns = constraint_dict[ANY_OF]
            StringTester.create_anyOf_test_values(patterns, value_dict, base_string)

        value_dict = StringTester.trim_value_dict(value_dict)
        return value_dict

    # PATTERN ----------------------------------------------------------------------------------------------------------
    @staticmethod
    def get_example_string(constraint_dict: dict, pattern: str):
        if EXAMPLES in constraint_dict and constraint_dict[EXAMPLES]:  # take given example if one exists
            return random.choice(constraint_dict[EXAMPLES])
        else:  # generate random value that matches pattern
            return StringTester.create_string_matching_pattern(pattern)

    @staticmethod
    def create_string_matching_pattern(pattern: str):
        return rstr.xeger(pattern)

    @staticmethod
    def create_invalid_string_for_pattern(input_string: str, pattern: str):
        if not pattern:
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

    @staticmethod
    def create_pattern_test_values(pattern: str, value_dict: dict, valid_string: str):
        value_dict[VALID].append(valid_string)

        invalid_string = StringTester.create_invalid_string_for_pattern(valid_string, pattern)
        value_dict[INVALID].append(invalid_string)

    # ANY OF -----------------------------------------------------------------------------------------------------------
    @staticmethod
    def create_anyOf_test_values(patterns: list, value_dict: dict, valid_string: str):
        for pattern in patterns:
            StringTester.create_pattern_test_values(pattern[PATTERN], value_dict, valid_string)

    # ENUM -------------------------------------------------------------------------------------------------------------
    @staticmethod
    def create_enum_test_values(valid_values: list, value_dict: dict):
        value_dict[VALID].append(random.choice(valid_values))
        value_dict[INVALID].extend([DEFAULT_BASE_STRING])

    # MIN LENGTH -------------------------------------------------------------------------------------------------------
    @staticmethod
    def create_minLength_test_values(min_length: int, base_str: str, value_dict: dict):
        multiplication_factor = min_length % len(base_str) + 1
        valid_string = base_str * multiplication_factor
        value_dict[VALID].append(valid_string)

        invalid_string = base_str[:min_length-1]
        value_dict[INVALID].append(invalid_string)

    # MAX LENGTH -------------------------------------------------------------------------------------------------------
    @staticmethod
    def create_maxLength_test_values(max_length: int, base_str: str, value_dict: dict):
        multiplication_factor = int(max_length/len(base_str))
        invalid_string = base_str * (multiplication_factor + 1)
        value_dict[INVALID].append(invalid_string)

        valid_string = invalid_string[:max_length-1]
        value_dict[VALID].append(valid_string)

    # CHECK -----------------------------------------------------------------------------------------------------------
    @staticmethod
    def trim_value_dict(value_dict: dict):
        valid_values = value_dict["valid"]

        if not valid_values:  # no restrictions were specified
            value_dict["valid"].append(DEFAULT_BASE_STRING)
        else:  # choose one valid value
            value_dict["valid"] = random.choice(valid_values)

        return value_dict
