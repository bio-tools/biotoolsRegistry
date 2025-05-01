import uuid
from copy import deepcopy
import json
import os

# path_data = "/elixir/application/backend/data"
# path_edam = path_data + "/edam/json/current"

elixir_dir = os.path.dirname(os.path.abspath(__file__))

class ToolHelper:
    input_tool = None
    output_tool = None
    invalid_input_tool = None
    tool_id = None

    @staticmethod
    def get_input_tool():
        tool = ToolHelper.get_tool_from_file("TestTool.json")
        ToolHelper.tool_id = uuid.uuid4().hex[:4]
        tool["biotoolsID"] += f"_{ToolHelper.tool_id}"
        return deepcopy(tool)

    @staticmethod
    def get_input_tool_invalid():
        return ToolHelper.get_tool_from_file("TestToolInvalid.json")

    # TODO check usages or else delete
    # @staticmethod
    # def get_output_tool():
    #     return ToolHelper.get_tool_from_file("/EDAM_Data_output.json")

    @staticmethod
    def get_tool_from_file(filename):
        test_dir = f"{elixir_dir}/../elixirapp/tests/data/"
        with open(os.path.join(test_dir, filename), 'r') as example:  # TODO used to be path_edam
            return json.load(example)

    # TODO check usages or else delete
    # @staticmethod
    # def tools_are_equal(lhs_tool, rhs_tool):
    #     """
    #     Description: Checks if all the keys and their values from lhs match with the ones in rhs.
    #     Returns:
    #         - True if the values for all keys from lhs that are also in rhs are equals.
    #         - False if there are keys that are part of both tools and do not have the same value associated with them.
    #     Caution: Note that this comparison does not consider keys that are only part of one of the tools. It also
    #              focuses on contents, not taking IDs into account.
    #     """
    #     for key in lhs_tool.keys():
    #         if key in rhs_tool.keys():
    #             if lhs_tool[key] != rhs_tool[key]:
    #                 return False
    #     return True
