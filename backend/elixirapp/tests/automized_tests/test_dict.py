import os
import json

schema_dir = os.path.dirname(os.path.abspath(__file__))
schema_filename = "biotoolsj.json"

# automatically created & filled: ("string": ["name": {"minLength": {"schemaValue": 1, "valid": [xy], "invalid": [yz]}])
test_dict = {}
type_dict = { # data types and constraints (e.g. "string": ["minLength", "pattern"]; prefilled
    "string": ["minLength", "maxLength", "enum", "pattern", "anyOf"],
    "array": ["items"],
    "referenceType": []
}


class SchemaParser:
    def __init__(self):
        self.schema = self.read_schema()
        self.tool_properties = self.schema["definitions"]["tool"]["properties"]
        self.definitions = self.schema["definitions"]

    @staticmethod
    def read_schema():
        with open(f"{schema_dir}/{schema_filename}", 'r', encoding='utf-8') as schema_file:
            return json.load(schema_file)

    def build_dict(self):
        level_one_properties = self.tool_properties.keys()  # extract names of all 1st level properties
        for prop in level_one_properties:
            prop_def = self.tool_properties[prop]  # get property definition

            if self.has_preknown_type(prop_def):
                self.handle_property(prop_def, prop)  # parse the property
            else:
                print("TODO handle special type")
                # TODO handle special type

    # TODO save special types ("$.definitions.{type}"; e.g. urlftpType) in dictionary

    def has_preknown_type(self, property: object):
        return "type" in property

    def handle_property(self, property: object, prop_name: str, depth=0):
        prop_type = property["type"]
        if prop_type == "string":
            print(f"{'\t'*depth}{prop_name}: string")
            self.parse_string(property, depth)
        elif prop_type == "array":
            print(f"{'\t'*depth}{prop_name}: array")
            self.parse_array(property, 1)
        elif prop_type == "object":
            print(f"{'\t'*depth}{prop_name}: object")
            self.parse_object(property)
        else:
            raise RuntimeError(f"[ERROR] Received invalid type {prop_type}")

    def parse_array(self, array_prop: object, depth):
        if "type" in array_prop and array_prop["type"] == "string":
            print(f"{'\t' * depth}\tstring")
        elif "items" in array_prop:
            items = array_prop["items"]
            if "type" in items:
                if items["type"] == "string":
                    print(f"{'\t'*depth}\t[string]")
                    self.handle_property(array_prop["items"], "*name*", depth+1)
                elif items["type"] == "object":
                    print(f"{'\t'*depth}[object]")
                    # TODO this can still be an array (e.g. properties-function-items-type-properties-type
                    for prop in items["properties"]:
                        self.parse_array(items["properties"][prop], depth + 1)
            else:  # TODO throw error or handle ref
                print(f"{'\t'*depth}[ref]")  #, array_prop["items"]["$ref"])
        else:      # TODO handle ref
            print(f"{'\t'*depth}{array_prop["$ref"]}")
            return

    def parse_object(self, object_prop: object):
        return None

    def parse_string(self, string_prop: str, depth=0):
        for constraint in type_dict["string"]:
            if constraint in string_prop:
                print(f"\t{'\t'*depth}{constraint}: {string_prop[constraint]}")

    def get_prop_from_path(self, path_to_prop: list):
        depth = len(path_to_prop) - 1
        if depth == 0: return

        print(f"depth: {depth}")
        for idx in range(depth):
            print(f"entering with {idx}")
            current_element_name = path_to_prop[idx]
            current_element = self.tool_properties[current_element_name]
            print(f"{depth * '\t'}{current_element_name}")

            if idx < depth-1:
                next_element = current_element[path_to_prop[idx + 1]]
                print(next_element)
            else:
                break
        print(f"{depth * '\t'}{current_element["type"]}")


    # TODO enums are seen as strings right now

parser = SchemaParser()
parser.build_dict()
