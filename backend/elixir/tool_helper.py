import uuid
from copy import deepcopy
import json
import os

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

    @staticmethod
    def get_tool_from_file(filename):
        test_dir = f"{elixir_dir}/../elixirapp/tests/data/"
        with open(os.path.join(test_dir, filename), 'r') as example:
            return json.load(example)