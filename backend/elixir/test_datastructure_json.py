from copy import deepcopy
import json

# empty minimal data structure that passes the validation
path_data = '/elixir/application/backend/data'
path_edam = path_data + '/edam/json/current'


def inputTool():
    with open(path_edam + '/EDAM_Data.json', "r") as example:
        input_base_struct = json.load(example)
    return deepcopy(input_base_struct)

def inputToolInvalid():
    with open(path_edam + '/EDAM_Data_invalid.json', "r") as example:
        invalid_input_base_struct = json.load(example)
    return deepcopy(invalid_input_base_struct)


# def emptyOutputTool():
#     return deepcopy(output_base_struct)
