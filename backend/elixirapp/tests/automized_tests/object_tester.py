import rstr
import string
import random
import copy
import re
from .constants import INVALID, VALID, PATTERN, MIN_LENGTH, MAX_LENGTH, ENUM, VALUE_DICT_BASE, DEFAULT_BASE_STRING,\
                       ANY_OF, EXAMPLES


class ObjectTester:
    @staticmethod
    def create_object_values(string_values: dict):
        value_dict = copy.deepcopy(VALUE_DICT_BASE)
        base_string = DEFAULT_BASE_STRING

    # HELPER -----------------------------------------------------------------------------------------------------------
    @staticmethod
    def create_object(constraint_dict: dict):
        return {key: values["valid"] for key, values in constraint_dict.items()}