from backend.elixir.tool_helper import ToolHelper
from .schema_parser import SchemaParser
from .string_tester import StringTester
from .array_tester import ArrayTester
from .object_tester import ObjectTester
from .constants import STRING, ARRAY, VALID, INVALID, OBJECT

TESTCOUNT = 0

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
        self.create_values_by_level()  # create valid and invalid values

        self.test_string_or_object(self.string_values)
        self.test_string_or_object(self.object_values)
        self.test_array(self.array_values)

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
        new_obj_entry = ObjectTester.create_object_values(self.object_restrictions[path], path, self.string_values,
                                                          self.object_values)
        self.object_values[path] = new_obj_entry

    def test_string_or_object(self, test_dict: dict):
        """
        Description:    Method for testing attributes in the tool based on schema restrictions.
        """
        input_tool = ToolHelper.get_input_tool()

        for path, constraints in test_dict.items():

            if path not in self.array_restrictions:  # only test real strings
                constraints = test_dict[path]
                path_list = path.split('/')

                value_before = self._test_valid_values(constraints, input_tool, path_list)  # extract original
                self._test_invalid_values(constraints, input_tool, path_list)

                # change back to original
                self._alter_tool(input_tool, path_list, value_before)

    def test_array(self, test_dict: dict):
        """
        Description:    Method for testing attributes in the tool based on schema restrictions.
        """
        input_tool = ToolHelper.get_input_tool()

        for path, constraints in test_dict.items():
            constraints = test_dict[path]
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
        original_value = self._get_tool_value(input_tool, path_list)

        if isinstance(values[VALID], list):
            for valid_value in values[VALID]:
                if isinstance(original_value, list) and not isinstance(valid_value, list):
                    valid_value = [valid_value]
                original_value = self._alter_tool(input_tool, path_list, valid_value)
        else:
            original_value = self._alter_tool(input_tool, path_list, values[VALID])

        self._alter_tool(input_tool, path_list, original_value)

        return original_value

    def _test_invalid_values(self, constraints: dict, input_tool: object, path_list: list):
        """
        Description:    Alters tool based on path using the invalid values specified for the attribute.
        Returns:        Value at the specified path for the input tool before replacement.
        """
        original_value = self._get_tool_value(input_tool, path_list)

        for invalid_value in constraints[INVALID]:
            if isinstance(original_value, list) and not isinstance(invalid_value, list):
                invalid_value = [invalid_value]

            original_value = self._alter_tool(input_tool, path_list, invalid_value)
        return original_value

    def _get_tool_value(self, parsing_object, path):
        if not path:
            return parsing_object

        key = path[0]

        if isinstance(parsing_object, list):
            if not parsing_object:
                return None
            next_obj = parsing_object[0].get(key)
        else:
            next_obj = parsing_object.get(key)

        return self._get_tool_value(next_obj, path[1:]) if next_obj is not None else None

    def _alter_tool(self, input_tool: dict, path: list, new_value):
        """
        Description:    Wrapper for updating a tool value.
        """
        return self._update_tool_value(input_tool, path, new_value)

    def _update_tool_value(self, parsing_object, path, new_value):
        """
        Description:    Modifies the parsing_object in-place by replacing the value at the path with new_value.
                        Returns the value before replacement (if any).
        """
        key = path[0]

        if len(path) == 1:
            if isinstance(parsing_object, list):
                if parsing_object:
                    value_before = parsing_object[0].get(key)
                    parsing_object[0][key] = new_value
                    return value_before
                else:
                    parsing_object.append({key: new_value})
                    return None
            else:
                value_before = parsing_object.get(key)
                parsing_object[key] = new_value
                return value_before

        if isinstance(parsing_object, list):
            next_object = parsing_object[0].get(key)
        else:
            next_object = parsing_object.get(key)

        return self._update_tool_value(next_object, path[1:], new_value)


testgen = TestGenerator()
testgen.test_all()
