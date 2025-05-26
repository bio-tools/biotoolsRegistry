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

        self.string_values = {}
        self.object_values = {}
        self.array_values = {}

    def test_all(self):
        """
        Description:    Method for automized testing based on restrictions parsed from the schema.
        """
        self.create_values_by_level()

        # self.test_string(self.string_values)

    def get_paths_grouped_by_depth(self):
        from collections import defaultdict

        depth_to_paths = defaultdict(list)
        categories = [STRING, ARRAY, OBJECT]

        for category in categories:
            path_dict = self.restriction_dict[category]
            for path in path_dict.keys():
                depth = len(path.strip('/').split('/'))
                depth_to_paths[depth].append(path)

        return dict(depth_to_paths)

    def create_values_by_level(self):
        depth_dict = self.get_paths_grouped_by_depth()

        self.string_restrictions = self.restriction_dict[STRING]
        self.array_restrictions = self.restriction_dict[ARRAY]
        self.object_restrictions = self.restriction_dict[OBJECT]

        for depth in range(max(depth_dict.keys()), min(depth_dict.keys()) - 1, -1):
            for path in depth_dict[depth]:
                self.create_value(path)

    def create_value(self, path: str):
        if path in self.restriction_dict[STRING]:  # delegate to string dictionary
            self.create_string_value(path)
        if path in self.restriction_dict[OBJECT]:  # delegate to object dictionary
            self.create_object_value(path)
        if path in self.restriction_dict[ARRAY]:  # delegate to array dictionary
            self.create_array_value(path)

    def create_string_value(self, path: str):
        """
        Description:    Method for creating valid and invalid values for the string attributes based on schema
                        restrictions.
        """
        string_restrictions = self.restriction_dict[STRING]
        self.string_values[path] = StringTester.create_string_values(string_restrictions[path])

    def create_array_value(self, path: str):
        """
        Description:    Method for creating valid and invalid values for the array attributes based on schema
                        restrictions.
        """
        self.array_values[path] = ArrayTester.create_array_values(path, self.array_restrictions[path],
                                                                  self.string_values, self.object_values)

    def create_object_value(self, path: str):
        """
        Description:    Method for creating valid and invalid values for the objects based on schema restrictions.
        """
        # iterate all objects and create valid and invalid instances
        new_obj_entry = ObjectTester.create_object_values(self.object_restrictions[path], path, self.string_values,
                                                          self.object_values)
        self.object_values[path] = new_obj_entry

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
            print(f"changed {path_list} from '{value_before}' to valid '{valid_value}'")
        return value_before

    def _test_invalid_values(self, constraints: dict, input_tool: object, path_list: list):
        """
        Description:    Alters tool based on path using the invalid values specified for the attribute.
        Returns:        Value at the specified path for the input tool before replacement.
        """
        value_before = None
        for invalid_value in constraints[INVALID]:
            value_before = self._get_altered_tool(input_tool, path_list, invalid_value)
            print(f"changed {path_list} from '{value_before}' to invalid '{invalid_value}'")
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
