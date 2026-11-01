from rest_framework import status
from elixir.tool_helper import ToolHelper as TH
from elixir.serializers import *
from elixirapp.tests.test_baseobject import BaseTestObject


class TestGetTool(BaseTestObject):
    def test_get_all_tools(self):
        for url in self.base_urls:
            self.ensure_tools(url)
            response = self.get_all_tools(url)
        return response

    def test_get_tool_valid(self):
        for url in self.base_urls:
            data = TH.get_input_tool()
            self.post_tool_checked(data)
            response = self.get_tool(url, data['biotoolsID'])
            # ensure get worked and that the correct resource was returned
            output_tool = response.json()
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            self.assertEqual(response.json()['name'], data['name'])

    def test_get_tool_invalid(self):
        for url in self.base_urls:
            response = self.get_tool(url, 'invalid_id')
            # ensure get did not work
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)