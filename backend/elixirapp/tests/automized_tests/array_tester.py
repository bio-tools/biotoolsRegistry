import copy
from .constants import VALUE_DICT_BASE, MIN_ITEMS, MAX_ITEMS, VALID, INVALID


class ArrayTester:
    @staticmethod
    def create_array_values(path: str, constraint_dict: dict, string_dict: dict, obj_dict: dict):
        value_dict = copy.deepcopy(VALUE_DICT_BASE)
        valid_value = (string_dict[path] if path in string_dict else obj_dict[path])[VALID]
        invalid_value = (string_dict[path] if path in string_dict else obj_dict[path])[INVALID]

        ArrayTester.create_values_for_constraints(valid_value, True, constraint_dict, value_dict)
        ArrayTester.create_values_for_constraints(invalid_value, False, constraint_dict, value_dict)

        return value_dict

    @staticmethod
    def create_values_for_constraints(value, is_valid: bool, constraint_dict: dict, value_dict: dict):
        validity = VALID if is_valid else INVALID

        if MIN_ITEMS in constraint_dict:
            minItems_value = constraint_dict[MIN_ITEMS]
            ArrayTester.create_minItems_test_values(value, minItems_value, value_dict)
        if MAX_ITEMS in constraint_dict:
            maxItems_value = constraint_dict[MAX_ITEMS]
            ArrayTester.create_maxItems_test_values(value, maxItems_value, value_dict)

        if not value_dict[validity]:  # no constraints
            value_dict[validity].append([value])

    # MIN ITEMS --------------------------------------------------------------------------------------------------------
    @staticmethod
    def create_minItems_test_values(value, min_items: int, value_dict: dict):
        value_dict[VALID].append([value] * min_items)
        value_dict[INVALID].append([value] * (min_items-1))

    # MAX ITEMS --------------------------------------------------------------------------------------------------------
    @staticmethod
    def create_maxItems_test_values(value, max_items: int, value_dict: dict):
        value_dict[VALID].append([value] * (max_items))
        value_dict[INVALID].append([value] * (max_items + 1))




