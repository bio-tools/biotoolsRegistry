import os
import json

schema_dir = os.path.dirname(os.path.abspath(__file__))
schema_filename = "biotoolsj.json"

TYPE_STRING_STR = "string"
TYPE_OBJECT_STR = "object"
TYPE_ARRAY_STR = "array"
TYPE_INTEGER_STR = "integer"

# automatically created : ("string": ["name": {"minLength": 1, ..., "path": ["parent1", "parent2", ...]]}])
test_dict = {
    TYPE_STRING_STR: [],
    TYPE_OBJECT_STR: [],
    TYPE_ARRAY_STR: []
}

# specifies constraints for data types; can be extended (e.g. numbers)
type_dict = {  # data types and constraints (e.g. "string": ["minLength", "pattern"]; TODO prefill
    TYPE_STRING_STR: ["minLength", "maxLength", "enum", "pattern", "anyOf"]
}


class SchemaParser:
    def create_test_dict(self):
        self.schema = self.read_schema()
        self.tool_properties = self.schema["definitions"]["tool"]["properties"]
        self.definitions = self.schema["definitions"]
        self.build_dict()
        return test_dict

    @staticmethod
    def read_schema():
        with open(f"{schema_dir}/{schema_filename}", 'r', encoding='utf-8') as schema_file:
            return json.load(schema_file)

    def build_dict(self):
        level_one_properties = self.tool_properties.keys()  # extract names of all 1st level properties
        for prop in level_one_properties:
            prop_def = self.tool_properties[prop]  # get property definition

            if self.has_type_attribute(prop_def):
                self.handle_property(prop_def, prop,  [])  # parse the property
            else:
                # print("TODO handle special type")
                # TODO handle special type
                None    # TODO del
    # TODO parse special types (e.g. urlftpType)

    def has_type_attribute(self, property: object):
        return "type" in property

    def handle_property(self, property: object, prop_name: str, path_to_prop: list):
        prop_type = property["type"]
        path_to_prop.append(prop_name)

        if prop_type == TYPE_STRING_STR:
            self.parse_string(property, path_to_prop)
        elif prop_type == TYPE_ARRAY_STR:
            self.parse_array(property, path_to_prop)  # TODO extend path
        elif prop_type == TYPE_OBJECT_STR:
            self.parse_object(property, path_to_prop)
        elif prop_type == TYPE_INTEGER_STR:
            raise RuntimeWarning(f"Type '{prop_type}' (property '{prop_name}') is not being handled.")
        else:
            raise RuntimeError(f"[ERROR] Received invalid type '{prop_type}' for property '{prop_name}'")

    def parse_array(self, array_prop: object, path: list):
        if "type" in array_prop and array_prop["type"] in [TYPE_STRING_STR]:
            # fill dictionary
            self.create_dict_entry(array_prop, path)
        elif "items" in array_prop:
            items = array_prop["items"]
            if "type" in items:
                if items["type"] == TYPE_STRING_STR:
                    self.handle_property(array_prop["items"], None, path)
                elif items["type"] == TYPE_OBJECT_STR:
                    for prop in items["properties"]:
                        path.append(prop)
                        self.parse_array(items["properties"][prop], path)
                        path.remove(prop)
            else:  # TODO throw error or handle ref
                None
        else:      # TODO handle ref
            None

    def parse_object(self, object_prop, path):
        for prop_key, prop_val in object_prop["properties"].items():
            self.handle_property(prop_val, prop_key)

    def parse_string(self, string_prop, path):
        self.create_dict_entry(string_prop, path)

    def create_dict_entry(self, prop, path):
        restriction_dict = {}
        prop_type = prop["type"]

        for type_restriction in type_dict[prop_type]:
            if type_restriction in prop:
                restriction_dict[type_restriction] = prop[type_restriction]
        restriction_dict["path"] = path

        test_dict[prop_type].append({f"{path[len(path) - 1]}": restriction_dict})


parser = SchemaParser()
