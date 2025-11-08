import copy

from .constants import (
    ADDITIONAL_PROPERTIES,
    DEFAULT_KEY,
    DEFAULT_VALUE,
    INVALID,
    LEFT_OUT_PATHS,
    PROPERTIES,
    REQUIRED,
    VALID,
    VALUE_DICT_BASE,
)


class ObjectTester:
    @staticmethod
    def create_object_values(
        obj_restrictions: dict,
        ref_info: dict,
        path: str,
        string_value_dict: dict,
        object_value_dict: dict,
        array_value_dict: dict,
    ):
        """
        Description:    Method for creating valid and invalid values for the objects based on schema restrictions.
        """
        properties = obj_restrictions[PROPERTIES]
        object_values = copy.deepcopy(VALUE_DICT_BASE)

        object_values[VALID], object_values[INVALID] = (
            ObjectTester.mess_with_properties(
                properties,
                ref_info,
                path,
                string_value_dict,
                object_value_dict,
                array_value_dict,
            )
        )
        if ADDITIONAL_PROPERTIES in obj_restrictions:
            extended_object = ObjectTester.get_additionalProperties_test_value(
                object_values[VALID]
            )
            if obj_restrictions[
                ADDITIONAL_PROPERTIES
            ]:  # additional properties are allowed
                if not isinstance(object_values[VALID], list):
                    object_values[VALID] = [object_values[VALID]]
                object_values[VALID].append(extended_object)
            else:  # additional properties are not allowed
                object_values[INVALID].append(extended_object)

        if REQUIRED in obj_restrictions:
            object_values[INVALID].extend(
                ObjectTester.add_required_test_values(
                    object_values[VALID], obj_restrictions[REQUIRED]
                )
            )

        valid_object = copy.deepcopy(object_values[VALID])  # NOTE: this is a quick fix
        for key in object_values[VALID]:
            if (
                key in LEFT_OUT_PATHS
                and REQUIRED in obj_restrictions
                and key not in obj_restrictions[REQUIRED]
            ):
                valid_object.pop(key)
            elif key == "url":
                valid_object[key] = "https://someurl.org"
            elif key == "description":
                valid_object[key] = "Dummy description."
            elif key == "email":
                valid_object[key] = "some_email@gmail.com"

        object_values[VALID] = valid_object

        return object_values

    # TEST OBJECT PROPERTIES -------------------------------------------------------------------------------------------
    @staticmethod
    def mess_with_properties(
        properties: list,
        ref_info: dict,
        path: str,
        string_values: dict,
        object_values: dict,
        arr_values: dict,
    ):
        """
        Description:    Uses property list and restriction information to create valid and invalid objects and adds them
                        to the given obj_rest dictionary.
        """
        valid_object, invalid_values = {}, []  # instantiate
        for (
            item_name
        ) in properties:  # get valid value for each item using other dictionaries
            path_to_item = f"{path}/{item_name}"  # assemble path
            item_values = None

            if path_to_item in string_values:
                item_values = string_values[path_to_item]
                valid_object[item_name] = (
                    item_values[VALID]
                    if path_to_item not in arr_values
                    else [item_values[VALID]]
                )
            elif path_to_item in object_values:
                item_values = object_values[path_to_item]
                valid_object[item_name] = (
                    item_values[VALID]
                    if path_to_item not in arr_values
                    else [item_values[VALID]]
                )

            if (
                item_values
                and INVALID in item_values
                and item_name not in LEFT_OUT_PATHS
            ):
                invalid_values.extend(
                    ObjectTester.perturbate_object(
                        valid_object, item_name, item_values[INVALID]
                    )
                )

        return valid_object, invalid_values

    @staticmethod
    def perturbate_object(valid_object: dict, prop_name: str, invalid_values: list):
        """
        Description:    Perturbs object with given invalid values.
        """
        perturbed = []
        for val in invalid_values:
            obj_copy = copy.deepcopy(valid_object)
            obj_copy[prop_name] = val
            perturbed.append(obj_copy)
        return perturbed

    # TEST OBJECT RESTRICTIONS -----------------------------------------------------------------------------------------
    @staticmethod
    def get_additionalProperties_test_value(base_object: dict):
        """
        Description:    Creates new test value by adding a default property.
        """
        test_value = copy.deepcopy(base_object)
        test_value[DEFAULT_KEY] = DEFAULT_VALUE
        return test_value

    @staticmethod
    def add_required_test_values(base_object: dict, required_props: list):
        """
        Description:    Creates new test values by removing required properties.
        """
        test_values = []

        for req_prop in required_props:
            test_value = copy.deepcopy(base_object)

            if isinstance(test_value, list) and test_value:
                test_value[:-1].pop(req_prop)
                test_values.append(test_value)
            elif req_prop in test_value:
                test_value.pop(req_prop)
                test_values.append(test_value)

        return test_values
