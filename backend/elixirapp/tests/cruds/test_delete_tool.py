from rest_framework import status

from elixir.serializers import *
from elixir.tool_helper import ToolHelper as TH
from elixirapp.tests.test_baseobject import BaseTestObject


class TestDeleteTool(BaseTestObject):
    def test_delete_tool_valid(self):
        for url in self.base_urls:
            data = TH.get_input_tool()
            self.post_tool_checked(data)

            response = self.remove_tool(url, data["biotoolsID"])

            # ensure delete worked
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            get_response = self.get_tool(url, data["biotoolsID"])
            self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_tool_invalid(self):
        for url in self.base_urls:
            invalid_id = "invalid_tool"
            response = self.remove_tool(url, invalid_id)
            # ensure delete did not work
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            get_response = self.get_tool(url, invalid_id)
            self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)
