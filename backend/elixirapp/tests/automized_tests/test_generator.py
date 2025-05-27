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

        print(self.restriction_dict)

        self.string_values = {}
        self.object_values = {}
        self.array_values = {}

    def test_all(self):
        """
        Description:    Method for automized testing based on restrictions parsed from the schema.
        """
        self.create_values_by_level()  # create valid and invalid values

        self.test_string(self.string_values)

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

            if path not in self.array_restrictions:  # only test real strings
                constraints = string_dict[path]
                path_list = path.split('/')

                value_before = self._test_valid_values(constraints, input_tool, path_list)  # extract original
                self._test_invalid_values(constraints, input_tool, path_list)

                # change back to original
                self._alter_tool(input_tool, path_list, value_before)

    def _test_valid_values(self, values: dict, input_tool: object, path_list: list):
        """
        Description:    Alters tool based on path using the valid values specified for the attribute.
        Returns:        Value at the specified path for the input tool before replacement.
        """
        value_before = None
        if isinstance(values[VALID], list):
            print(f"validvallist for {path_list}: {values[VALID]}")
            for valid_value in values[VALID]:
                value_before = self._alter_tool(input_tool, path_list, valid_value)
        else:
            print(f"validvalobj for {path_list}: {values[VALID]}")
            value_before = self._alter_tool(input_tool, path_list, values[VALID])

        self._alter_tool(input_tool, path_list, value_before)

        # print(f"altered tool after changing {path_list} from '{value_before}' to '{values[VALID]}':\n\t\t{input_tool}")

        return value_before

    def _test_invalid_values(self, constraints: dict, input_tool: object, path_list: list):
        """
        Description:    Alters tool based on path using the invalid values specified for the attribute.
        Returns:        Value at the specified path for the input tool before replacement.
        """
        value_before = None
        for invalid_value in constraints[INVALID]:
            value_before = self._alter_tool(input_tool, path_list, invalid_value)
            print(f"invalidval for {path_list}: {invalid_value} instead of {value_before}")
        return value_before

    def _alter_tool(self, input_tool: dict, path: list, new_value: str):
        """
        Description:    Wrapper for updating a tool value.
        """
        return self._update_tool_value(input_tool, path, new_value)

    def _update_tool_value(self, parsing_object, path, new_value):
        """
        Description:    Modifies the parsing_object by replacing the value at the path with the given new_value.
        Returns:        Value at the specified path for the parsing_object before replacement.
        """
        if len(path) == 1:  # last level reached
            attribute_name = path[0]
            if isinstance(parsing_object, list):
                if parsing_object:  # list is not empty
                    first_value = parsing_object[0]
                    value_before = first_value[attribute_name] if attribute_name in first_value else None
                    first_value[attribute_name] = new_value
                    # print(f"new chosen value1: '{new_value}' for '{attribute_name}' instead of '{value_before}'")
                    return value_before
                else:  # list is empty
                    parsing_object.append({attribute_name: new_value})
                    # print(f"new chosen value2: '{new_value}' for '{attribute_name}'")
                    return parsing_object
        else:
            if isinstance(parsing_object, list):
                return self._update_tool_value(parsing_object[0][path[0]], path[1:], new_value)
            else:
                return self._update_tool_value(parsing_object[path[0]], path[1:], new_value)


testgen = TestGenerator()
testgen.test_all()
