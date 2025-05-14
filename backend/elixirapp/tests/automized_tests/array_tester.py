import copy
from .constants import VALUE_DICT_BASE, MIN_ITEMS, MAX_ITEMS


class ArrayTester:
    @staticmethod
    def create_array_values(constraint_dict: dict, string_dict: dict):
        value_dict = copy.deepcopy(VALUE_DICT_BASE)

        if MIN_ITEMS in constraint_dict:
            minItems_value = constraint_dict[MIN_ITEMS]
            ArrayTester.create_minItems_test_values(minItems_value, value_dict, string_dict)

        if MAX_ITEMS in constraint_dict:
            maxItems_value = constraint_dict[MAX_ITEMS]
            ArrayTester.create_maxItems_test_values(maxItems_value, value_dict, string_dict)

        return value_dict

    # MIN ITEMS --------------------------------------------------------------------------------------------------------
    @staticmethod
    def create_minItems_test_values(min_items: int, value_dict: dict, string_dict: dict):
        created_object = ArrayTester.create_object(string_dict)

        value_dict["valid"].append([created_object for _ in range(min_items)])
        value_dict["invalid"].append([created_object for _ in range(min_items-1)])

    # MAX ITEMS --------------------------------------------------------------------------------------------------------
    @staticmethod
    def create_maxItems_test_values(max_items: int, value_dict: dict, string_dict: dict):
        created_object = ArrayTester.create_object(string_dict)

        value_dict["valid"].append([created_object for _ in range(max_items)])
        value_dict["invalid"].append([created_object for _ in range(max_items+1)])

    # HELPER -----------------------------------------------------------------------------------------------------------
    @staticmethod
    def create_object(constraint_dict: dict):
        return { key: values["valid"] for key, values in constraint_dict.items() }




