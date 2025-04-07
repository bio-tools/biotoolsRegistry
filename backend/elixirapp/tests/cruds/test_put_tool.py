from rest_framework import status
from elixir.tool_helper import ToolHelper as TH
from elixir.serializers import *
from backend.elixirapp.tests.test_baseobject import BaseTestObject


class TestPutTool(BaseTestObject):
    def test_put_tool_valid(self):
        for url in self.put_post_urls:
            # create tool
            data = TH.get_input_tool()
            self.post_tool_checked(data)

            # update tool
            new_name = "Updated Tool Name"
            data['name'] = new_name

            response = self.put_tool(url, data)

            # ensure update worked
            output_tool = response.json()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(output_tool['name'], new_name)  # ensure name was updated

    def test_put_tool_invalid(self):
        for url in self.put_post_urls:
            data = TH.get_input_tool()
            self.post_tool_checked(data)

            # update tool
            name_before = data['name']
            data.pop('name', None)

            response = self.put_tool(url, data)

            # ensure update did not work
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            get_response = self.get_tool(url, data['biotoolsID'])
            output_tool = get_response.json()
            self.assertEqual(output_tool['name'], name_before)  # ensure name is still the same

    def test_put_tool_unchanged(self):
        # post tool
        data = TH.get_input_tool()
        self.post_tool_checked(data)

        for url in self.put_post_urls:
            # update tool
            response = self.put_tool(url, data)
            # ensure update worked
            self.assertEqual(response.status_code, status.HTTP_200_OK)