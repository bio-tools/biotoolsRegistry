from schema_parser import SchemaParser


class TestGenerator:
    def __init__(self):
        self.test_dict = SchemaParser.create_test_dict()
        print(self.test_dict)


testgen = TestGenerator()