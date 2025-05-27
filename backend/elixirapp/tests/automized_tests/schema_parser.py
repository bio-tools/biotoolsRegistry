import os
import json
from .constants import STRING, ARRAY, OBJECT, DEFINITIONS, TOOL, PROPERTIES, ITEMS, TYPE, REF, TYPE_DICT

schema_dir = os.path.dirname(os.path.abspath(__file__))
schema_filename = "biotoolsj.json"


class SchemaParser:
    def __init__(self):
        self.schema = SchemaParser.read_schema()
        self.type_definitions = self.schema[DEFINITIONS]
        self.tool_properties = self.type_definitions.pop(TOOL)[PROPERTIES]  # extract tool type into own variable
        self.restriction_dict = {
            STRING: {},
            OBJECT: {},
            ARRAY: {}
        }

    def create_restriction_dict(self):
        self.build_dict()
        return self.restriction_dict

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
        return TYPE in prop

    @staticmethod
    def is_ref_type(prop: object):
        """
        Description: Checks whether the current property is a schema-defined type.
        """
        return REF in prop

    def handle_ref_type(self, reference: str, path_to_prop: list):
        reference_name = reference.split('/')[-1]
        reference_definition = self.type_definitions[reference_name]
        self.handle_prop(reference_definition, path_to_prop)

    def handle_prop(self, prop: object, path_to_prop: list):
        """
        Description: Parses the property based on its 'type' or '$ref' attribute and fills dictionary.
        """
        if SchemaParser.is_predefined_type(prop):  # known type
            prop_type = prop[TYPE]
            if prop_type == STRING:
                SchemaParser.create_dict_entry(self, prop, path_to_prop)
            elif prop_type == ARRAY:
                self.parse_array(prop, path_to_prop)
            elif prop_type == OBJECT:
                self.parse_object(prop, path_to_prop)
            else:
                raise RuntimeWarning(f"[WARNING]: Type '{prop_type}' is currently not being handled.")
        elif SchemaParser.is_ref_type(prop):  # schema-defined type
            self.handle_ref_type(prop[REF], path_to_prop)

    def parse_array(self, array_prop: object, path: list):
        """
        Description: Handles an 'array' type, extracting its restrictions and initiating further parsing (if required).
        """
        array_items = array_prop[ITEMS]

        item_type = array_items[TYPE] if self.is_predefined_type(array_items) else array_items[REF]

        if item_type == OBJECT:
            self.parse_object(array_items, path)
        else:
            self.handle_prop(array_items, path)  # save info on strings

        self.create_dict_entry(array_prop, path)

    def parse_object(self, object_prop: object, path: list):
        """
        Description: Handles an 'object' type.
        """
        if PROPERTIES in object_prop:
            properties = object_prop[PROPERTIES]

            for prop in properties:
                path.append(prop)
                self.handle_prop(object_prop[PROPERTIES][prop], path)
                path.remove(prop)
            self.create_object_entry(path, object_prop)

    def create_object_entry(self, path: list, prop):
        object_restrictions = {}
        property_names = list(prop[PROPERTIES].keys())

        for type_restriction in TYPE_DICT[OBJECT]:
            if type_restriction in prop:
                object_restrictions[type_restriction] = prop[type_restriction]

        object_restrictions[PROPERTIES] = property_names
        self.restriction_dict[OBJECT]['/'.join(path)] = object_restrictions

    def create_dict_entry(self, prop, path):
        """
        Description: Adds an entry to the restriction_dict.
        """

        restriction_dict = {}
        prop_type = prop[TYPE]

        for type_restriction in TYPE_DICT[prop_type]:
            if type_restriction in prop:
                restriction_dict[type_restriction] = prop[type_restriction]

        self.restriction_dict[prop_type]['/'.join(path)] = restriction_dict
