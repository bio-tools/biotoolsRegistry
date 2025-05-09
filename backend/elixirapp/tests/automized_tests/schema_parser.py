import os
import json

schema_dir = os.path.dirname(os.path.abspath(__file__))
schema_filename = "biotoolsj.json"

TYPE_STRING_STR = "string"
TYPE_OBJECT_STR = "object"
TYPE_ARRAY_STR = "array"

ARRAY_PATH_EXTENSION = ["items", "properties"]

# automatically created : ("string": ["name": {"minLength": 1, ..., "path": ["parent1", "parent2", ...]]}])
test_dict = {
    TYPE_STRING_STR: [],
    TYPE_OBJECT_STR: [],
    TYPE_ARRAY_STR: []
}

# specifies constraints for data types; can be extended (e.g. numbers)
type_dict = {  # data types and constraints (e.g. "string": ["minLength", "pattern"]; TODO finish prefilling
    TYPE_STRING_STR: ["minLength", "maxLength", "enum", "pattern", "anyOf"],
    TYPE_ARRAY_STR: ["minItems", "maxItems"]
}


class SchemaParser:
    @staticmethod
    def create_test_dict():
        schema = SchemaParser.read_schema()
        tool_properties = schema["definitions"]["tool"]["properties"]
        definitions = schema["definitions"]  # TODO
        SchemaParser.build_dict(tool_properties)
        return test_dict

    @staticmethod
    def read_schema():
        with open(f"{schema_dir}/{schema_filename}", 'r', encoding='utf-8') as schema_file:
            return json.load(schema_file)

    @staticmethod
    def build_dict(tool_properties):
        """
        Description: Iterates first-level dictionary items to build type-based test dictionary.
        """
        for prop in tool_properties.keys():
            prop_def = tool_properties[prop]  # extract definition of current property

            if SchemaParser.has_type_attribute(prop_def):  # known type
                SchemaParser.handle_prop(prop_def, [prop])  # parse the prop
            else:  # schema-defined type
                # TODO handle special type
                None  # TODO del

    # TODO parse special type definitions and save type info (e.g. urlftpType)

    @staticmethod
    def has_type_attribute(prop: object):
        """
        Description: Checks whether the current property is a known or schema-defined type.
        """
        return "type" in prop

    @staticmethod
    def handle_prop(prop: object, path_to_prop: list):
        """
        Description: Parses the property based on its 'type' or '$ref' attribute and fills dictionary.
        """
        type = prop["type"] if "type" in prop else prop["$ref"]

        if type == TYPE_STRING_STR:
            SchemaParser.create_dict_entry(prop, path_to_prop)
        elif type == TYPE_ARRAY_STR:
            SchemaParser.parse_array(prop, path_to_prop)
        else:
            print(path_to_prop, "unhandled")

    @staticmethod
    def parse_array(array_prop: object, path: list):
        """
        Description: Handles an array type, extracting its restrictions and initiating further parsing (if required).
        """
        array_items = array_prop["items"]

        if "properties" in array_items:
            path.extend(ARRAY_PATH_EXTENSION)

            properties = array_items["properties"]
            for prop_name, prop_def in zip(properties.keys(), properties.values()):
                SchemaParser.handle_prop(prop_def, path + [prop_name])

            path[:] = [p for p in path if p not in ARRAY_PATH_EXTENSION]  # reverse path extension
        else:
            SchemaParser.handle_prop(array_items, path)

        SchemaParser.create_dict_entry(array_prop, path)

    @staticmethod
    def parse_object(object_prop, path):
        for prop_key, prop_val in object_prop["properties"].items():
            SchemaParser.handle_prop(prop_val, prop_key)

    @staticmethod
    def create_dict_entry(prop, path):
        restriction_dict = {}
        prop_type = prop["type"]

        for type_restriction in type_dict[prop_type]:
            if type_restriction in prop:
                print(f"{type_restriction} fits with {prop_type}")
                restriction_dict[type_restriction] = prop[type_restriction]
                restriction_dict["path"] = path

        if restriction_dict != {}:
            test_dict[prop_type].append({f"{path[len(path) - 1]}": restriction_dict})


parser = SchemaParser()
