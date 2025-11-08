import copy
import random

from .constants import INVALID, MAX_ITEMS, MIN_ITEMS, VALID, VALUE_DICT_BASE


class ArrayTester:
    @staticmethod
    def create_array_values(
        path: str, constraint_dict: dict, string_dict: dict, obj_dict: dict
    ):
        value_dict = copy.deepcopy(VALUE_DICT_BASE)

        source = (string_dict if path in string_dict else obj_dict)[path]

        valid_value = source[VALID]
        ArrayTester.create_values_for_constraints(
            valid_value, True, constraint_dict, value_dict
        )

        if INVALID in source:
            invalid_value = (
                random.choice(source[INVALID]) if source[INVALID] else None
            )  # choose an invalid value
            ArrayTester.create_values_for_constraints(
                invalid_value, False, constraint_dict, value_dict
            )

        return value_dict

    @staticmethod
    def create_values_for_constraints(
        value, is_valid: bool, constraint_dict: dict, value_dict: dict
    ):
        validity = VALID if is_valid else INVALID

        if MIN_ITEMS in constraint_dict:
            minItems_value = constraint_dict[MIN_ITEMS]
            ArrayTester.create_minItems_test_values(
                value, minItems_value, value_dict, is_valid
            )
        if MAX_ITEMS in constraint_dict:
            maxItems_value = constraint_dict[MAX_ITEMS]
            ArrayTester.create_maxItems_test_values(
                value, maxItems_value, value_dict, is_valid
            )

        if not value_dict[validity]:  # no constraints
            value_dict[validity].append(value)

    # MIN ITEMS --------------------------------------------------------------------------------------------------------
    @staticmethod
    def create_minItems_test_values(
        value, min_items: int, value_dict: dict, is_valid: bool
    ):
        valid_val = [value] * min_items
        value_dict[VALID if is_valid else INVALID].append(valid_val)

        if is_valid:
            if min_items == 1:
                invalid_val = []
                value_dict[INVALID].append(invalid_val)
        else:
            if min_items > 1:
                invalid_val = [value] * (min_items - 1)
                value_dict[VALID].append(invalid_val)

    # MAX ITEMS --------------------------------------------------------------------------------------------------------
    @staticmethod
    def create_maxItems_test_values(
        value, max_items: int, value_dict: dict, is_valid: bool
    ):
        valid_val = [value] * max_items
        value_dict[VALID if is_valid else INVALID].append(valid_val)

        if is_valid:
            invalid_val = [value] * (max_items + 1)
            value_dict[INVALID].append(invalid_val)
        else:
            if max_items > 0:
                valid_boundary_val = [value] * max_items
                value_dict[VALID].append(valid_boundary_val)
