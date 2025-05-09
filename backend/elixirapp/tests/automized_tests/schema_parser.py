import os
import json

schema_dir = os.path.dirname(os.path.abspath(__file__))
schema_filename = "biotoolsj.json"

TYPE_STRING_STR = "string"
TYPE_OBJECT_STR = "object"
TYPE_ARRAY_STR = "array"

ARRAY_PATH_EXTENSION = ["items", "properties"]


# specifies constraints for data types; can/should be extended (e.g. numbers, different restrictions)
type_dict = {  # data types and constraints (e.g. "string": ["minLength", "pattern"]
    TYPE_STRING_STR: ["minLength", "maxLength", "enum", "pattern", "anyOf"],
    TYPE_ARRAY_STR: ["minItems", "maxItems"]
}


class SchemaParser:
    def __init__(self):
        self.schema = SchemaParser.read_schema()
        self.type_definitions = self.schema["definitions"]
        self.tool_properties = self.type_definitions.pop("tool")["properties"]  # extract tool type into own variable
        self.test_dict = {
            TYPE_STRING_STR: [],
            TYPE_OBJECT_STR: [],
            TYPE_ARRAY_STR: []
        }

    def create_test_dict(self):
        self.build_dict()
        return self.test_dict

    @staticmethod
    def read_schema():
        with open(f"{schema_dir}/{schema_filename}", 'r', encoding='utf-8') as schema_file:
            return json.load(schema_file)

    def build_dict(self):
        """
        Description: Iterates dictionary items to build type-based test dictionary.
        """
        for prop in self.tool_properties.keys():
            prop_def = self.tool_properties[prop]  # extract definition of current property
            self.handle_prop(prop_def, [prop])  # parse the prop

    @staticmethod
    def is_predefined_type(prop: object):
        """
        Description: Checks whether the current property is a known type.
        """
        return "type" in prop

    @staticmethod
    def is_ref_type(prop: object):
        """
        Description: Checks whether the current property is a schema-defined type.
        """
        return "$ref" in prop

    def handle_ref_type(self, reference: str, path_to_prop: list):
        reference_name = reference.split('/')[-1]
        reference_definition = self.type_definitions[reference_name]
        self.handle_prop(reference_definition, path_to_prop)

    def handle_prop(self, prop: object, path_to_prop: list):
        """
        Description: Parses the property based on its 'type' or '$ref' attribute and fills dictionary.
        """
        if SchemaParser.is_predefined_type(prop):  # known type
            prop_type = prop["type"]
            if prop_type == TYPE_STRING_STR:
                SchemaParser.create_dict_entry(self, prop, path_to_prop)
            elif prop_type == TYPE_ARRAY_STR:
                self.parse_array(prop, path_to_prop)
            elif prop_type == TYPE_OBJECT_STR:
                self.parse_object(prop, path_to_prop)
            else:
                raise RuntimeWarning(f"[WARNING]: Type '{prop_type}' is currently not being handled.")
        elif SchemaParser.is_ref_type(prop):  # schema-defined type
            self.handle_ref_type(prop["$ref"], path_to_prop)

    def parse_array(self, array_prop: object, path: list):
        """
        Description: Handles an 'array' type, extracting its restrictions and initiating further parsing (if required).
        """
        array_items = array_prop["items"]

        if "properties" in array_items:
            properties = array_items["properties"]
            for prop_name, prop_def in zip(properties.keys(), properties.values()):
                self.handle_prop(prop_def, path + [prop_name])
        else:
            self.handle_prop(array_items, path)

        SchemaParser.create_dict_entry(self, array_prop, path)

    def parse_object(self, object_prop: object, path: list):
        """
        Description: Handles an 'object' type.
        """
        properties = object_prop["properties"]

        for prop in properties:
            path.append(prop)
            self.handle_prop(object_prop["properties"][prop], path)
            path.remove(prop)

    def create_dict_entry(self, prop, path):
        restriction_dict = {}
        prop_type = prop["type"]

        for type_restriction in type_dict[prop_type]:
            if type_restriction in prop:
                restriction_dict[type_restriction] = prop[type_restriction]
                restriction_dict["path"] = path

        if restriction_dict != {}:
            self.test_dict[prop_type].append({f"{path[len(path) - 1]}": restriction_dict})


parser = SchemaParser()
