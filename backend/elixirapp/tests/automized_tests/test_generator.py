from schema_parser import SchemaParser


class TestGenerator:
    def __init__(self):
        parser = SchemaParser()

        self.test_dict = parser.create_test_dict()
        # print(self.test_dict)


testgen = TestGenerator()