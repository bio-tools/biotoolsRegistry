from backend.elixir.tool_helper import ToolHelper
from .schema_parser import SchemaParser
import json


class TestGenerator:
    def __init__(self):
        parser = SchemaParser()
        self.test_dict = parser.create_test_dict()

    def test_all(self):
        # TODO
        self.test_string()

    def test_string(self):
        string_test_dict = self.test_dict["string"]

        input_tool = ToolHelper.get_input_tool()

        for attr_name, attr_constraints in zip(string_test_dict.keys(), string_test_dict.values()):
            self.create_valid_string_values(attr_constraints)
            self.create_invalid_string_values(attr_constraints)

    def create_invalid_string_values(self, constraint_dict: dict):
        if "minLength" in constraint_dict:
            print("todo test minLength with invalid values by inserting them into the test tool")

    def create_valid_string_values(self, constraint_dict: dict):
        if "minLength" in constraint_dict:
            print("todo test minLength with invalid values by inserting them into the test tool")


testgen = TestGenerator()
testgen.test_all()