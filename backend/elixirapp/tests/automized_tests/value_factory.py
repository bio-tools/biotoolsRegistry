from .schema_parser import SchemaParser
from .string_tester import StringTester
from .array_tester import ArrayTester
from .object_tester import ObjectTester
from .constants import STRING, ARRAY, OBJECT, REF_INFO, EDGE_CASE_PATHS


class ValueFactory:
    def __init__(self):
        parser = SchemaParser()
        self.restriction_dict = parser.create_restriction_dict()

        self.string_restrictions = self.restriction_dict[STRING]
        self.array_restrictions = self.restriction_dict[ARRAY]
        self.object_restrictions = self.restriction_dict[OBJECT]
        self.ref_info = self.restriction_dict[REF_INFO]

        self.string_values = {}
        self.object_values = {}
        self.array_values = {}

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

        for depth in range(max(depth_dict.keys()), min(depth_dict.keys()) - 1, -1):
            for path in depth_dict[depth]:
                self.create_value(path)

        self.string_values = self._clean_values(self.string_values, False)
        self.object_values = self._clean_values(self.object_values, False)
        self.array_values = self._clean_values(self.array_values, True)

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
        self.string_values[path] = StringTester.create_string_values(path, string_restrictions[path], self.ref_info)

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
        new_obj_entry = ObjectTester.create_object_values(self.object_restrictions[path], self.ref_info, path, self.string_values,
                                                          self.object_values)
        self.object_values[path] = new_obj_entry

    def _clean_values(self, value_dict: dict, is_array: bool):
        def get_edam_type(path: str, ref_info: dict):
            for key, values in ref_info.items():
                if key.startswith("EDAM") and path in values:
                    return key
            return None

        new_dict = {
            path: test_dict
            for path, test_dict in value_dict.items()
            if not any(
                get_edam_type('/'.join(path.split('/')[:i]), self.ref_info)
                for i in range(1, len(path.split('/')) + 1)
            )
        }
        edge_case_paths = [path for path in value_dict.keys() if path in EDGE_CASE_PATHS.keys()]
        for edge_case_path in edge_case_paths:
            new_val = [EDGE_CASE_PATHS[edge_case_path]] if is_array else EDGE_CASE_PATHS[edge_case_path]
            new_dict[edge_case_path] = new_val
        return new_dict

    def alter_tool(self, input_tool: dict, path: list, new_value):
        """
        Description:    Wrapper for updating a tool value.
        """
        return self._update_tool_value(input_tool, path, new_value)

    def _update_tool_value(self, parsing_object, path, new_value):
        """
        Description:    Modifies the parsing_object in-place by replacing the value at the path with new_value.
                        Returns the value before replacement (if any).
        """
        if not parsing_object:
            return

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
