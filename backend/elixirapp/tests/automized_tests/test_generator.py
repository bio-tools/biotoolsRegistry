from schema_parser import SchemaParser
import json


class TestGenerator:
    def __init__(self):
        parser = SchemaParser()
        self.test_dict = parser.create_test_dict()


testgen = TestGenerator()