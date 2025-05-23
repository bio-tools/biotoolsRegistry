from backend.elixir.tool_helper import ToolHelper
from .schema_parser import SchemaParser
from .string_tester import StringTester
from .array_tester import ArrayTester
from .object_tester import ObjectTester
from .constants import STRING, ARRAY, VALID, INVALID, OBJECT, PROPERTIES
import random

class TestGenerator:
    def __init__(self):
        parser = SchemaParser()
        self.restriction_dict = parser.create_restriction_dict()

        print(f"objdict: {self.restriction_dict[OBJECT]}")
        print(f"strdict: {self.restriction_dict[STRING]}")
        print(f"arrdict: {self.restriction_dict[ARRAY]}")

        self.string_values = {}
        self.array_values = {}
        self.object_values = {}

    def test_all(self):
        """
        Description:    Method for automized testing based on restrictions parsed from the schema.
        """
        self.string_values = self.create_string_values()
        self.object_values = self.create_object_values()
        self.array_values = self.create_array_values()

        # self.test_string(self.string_values)

    def create_string_values(self):
        """
        Description:    Method for creating valid and invalid values for the string attributes based on schema
                        restrictions.
        """
        string_restrictions = self.restriction_dict[STRING]
        string_test_dict = {}
        for attr_path, attr_constraints in zip(string_restrictions.keys(), string_restrictions.values()):
            string_test_dict[attr_path] = StringTester.create_string_values(attr_constraints)
        return string_test_dict

    def create_array_values(self):
        """
        Description:    Method for creating valid and invalid values for the array attributes based on schema
                        restrictions.
        """
        array_test_dict = self.restriction_dict[ARRAY]
        for attr_path, attr_constraints in zip(array_test_dict.keys(), array_test_dict.values()):
            filtered_dict = {k: v for k, v in self.string_values.items() if attr_path in k}
            array_test_dict[attr_path] = ArrayTester.create_array_values(attr_constraints, filtered_dict)
        return array_test_dict

    def create_object_values(self):
        """
        Description:    Method for creating valid and invalid values for the objects based on schema restrictions.
        """
        object_restrictions = self.restriction_dict[OBJECT]
        print(f"object restrictions: {object_restrictions}")
        object_test_dict = {}
        print(f"amount: {len(object_restrictions.keys())}")
        for attr_path, attr_constraints in zip(object_restrictions.keys(), object_restrictions.values()):
            items = attr_constraints[PROPERTIES]
            object_test_dict[attr_path] = {}
            valid_object, invalid_object = {}, {}

            print(f"attrpath: {attr_path}")

            object_test_dict[attr_path][VALID] = valid_object
            object_test_dict[attr_path][INVALID] = invalid_object

            # # print(f"test_dict for {path_to_prop}: {object_test_dict[attr_path]}")

        return object_test_dict

    def test_string(self, string_dict: dict):
        """
        Description:    Method for testing string attributes in the tool based on schema restrictions.
        """
        input_tool = ToolHelper.get_input_tool()

        for path, constraints in zip(string_dict.keys(), string_dict.values()):
            constraints = string_dict[path]
            path_list = path.split('/')

            value_before = self._test_valid_values(constraints, input_tool, path_list)  # extract original
            self._test_invalid_values(constraints, input_tool, path_list)

            # change back to original
            self._get_altered_tool(input_tool, path_list, value_before)

    def _test_valid_values(self, constraints: dict, input_tool: object, path_list: list):
        """
        Description:    Alters tool based on path using the valid values specified for the attribute.
        Returns:        Value at the specified path for the input tool before replacement.
        """
        value_before = None
        for valid_value in constraints[VALID]:
            value_before = self._get_altered_tool(input_tool, path_list, valid_value)
            # print(f"changed {path_list} from '{value_before}' to valid '{valid_value}'")
        return value_before

    def _test_invalid_values(self, constraints: dict, input_tool: object, path_list: list):
        """
        Description:    Alters tool based on path using the invalid values specified for the attribute.
        Returns:        Value at the specified path for the input tool before replacement.
        """
        value_before = None
        for invalid_value in constraints[INVALID]:
            value_before = self._get_altered_tool(input_tool, path_list, invalid_value)
            # print(f"changed {path_list} from '{value_before}' to invalid '{invalid_value}'")
        return value_before

    def _get_altered_tool(self, input_tool: dict, path: list, new_value: str):
        """
        Description:    Wrapper for updating a tool value.
        """
        return self._update_tool_value(input_tool, path, new_value)

    def _update_tool_value(self, parsing_object, path, new_value):
        """
        Description:    Modifies the parsing_object by replacing the value at the path with the given new_value.
        Returns:        Value at the specified path for the parsing_object before replacement.
        """
        if isinstance(parsing_object, list):  # current object is list
            value_before = parsing_object
            parsing_object.append({path[0]: new_value})
            return value_before
        elif len(path) == 1:  # last level reached
            value_before = parsing_object[path[0]] if path[0] in parsing_object else None
            parsing_object[path[0]] = new_value
            return value_before
        else:
            return self._update_tool_value(parsing_object[path[0]], path[1:], new_value)


testgen = TestGenerator()
testgen.test_all()
