import random

from backend.elixir.tool_helper import ToolHelper
from .schema_parser import SchemaParser
from .string_tester import StringTester
from .array_tester import ArrayTester


class TestGenerator:
    def __init__(self):
        parser = SchemaParser()
        self.restriction_dict = parser.create_restriction_dict()

    def test_all(self):
        string_dict = self.create_string_values()
        array_dict = self.create_array_values(string_dict)
        # TODO are there object restrictions?

        input_tool = ToolHelper.get_input_tool()

        # TODO test by inserting into tool

    def test(self):
        self.test_array()

    def create_string_values(self):
        string_restrictions = self.restriction_dict["string"]
        string_test_dict = {}
        for attr_name, attr_constraints in zip(string_restrictions.keys(), string_restrictions.values()):
            string_test_dict[attr_name] = StringTester.create_string_values(attr_constraints)
        return string_test_dict

    def create_array_values(self, string_dict: dict):
        array_test_dict = self.restriction_dict["array"]
        for attr_name, attr_constraints in zip(array_test_dict.keys(), array_test_dict.values()):
            filtered_dict = {k: v for k, v in string_dict.items() if attr_name in k}
            ArrayTester.create_array_values(attr_constraints, filtered_dict)
        return array_test_dict


testgen = TestGenerator()
testgen.test_all()
