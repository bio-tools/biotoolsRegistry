from rest_framework import status
from elixir.tool_helper import ToolHelper as TH
from elixir.serializers import *
from backend.elixirapp.tests.test_baseobject import BaseTestObject


class TestPostTool(BaseTestObject):

    def test_post_tool_valid(self):
        for url in self.put_post_urls:
            response = self.post_tool(url, TH.get_input_tool())
            output_tool = response.json()
            # ensure post worked
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertTrue(TH.tools_are_equal(output_tool, TH.get_output_tool()))

    def test_post_tool_invalid(self):
        for url in self.put_post_urls:
            response = self.post_tool(url, TH.invalid_input_tool)
            # ensure post did not work
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_tool_empty(self):
        for url in self.put_post_urls:
            response = self.post_tool(url, {})
            # ensure post did not work
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)