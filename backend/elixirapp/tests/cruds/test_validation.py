from rest_framework import status
from elixir.tool_helper import ToolHelper as TH
from elixir.serializers import *
from elixirapp.tests.test_baseobject import BaseTestObject


class TestValidation(BaseTestObject):
    def test_validate_tool_post_valid(self):
        data = TH.get_input_tool()
        for url in self.base_urls:
            response = self.validate_tool_post(url, data)

            # ensure validation worked
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # ensure tool was not added to database
            get_response = self.get_tool(url, data['biotoolsID'])
            self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_validate_tool_post_invalid(self):
        data = TH.get_input_tool_invalid()
        for url in self.base_urls:
            response = self.validate_tool_post(url, data)

            # ensure validation worked
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            # ensure tool was not added to database
            get_response = self.get_tool(url, data['biotoolsID'])
            self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_validate_tool_post_empty(self):
        for url in self.base_urls:
            response = self.validate_tool_post(url, {})
            # ensure validation worked
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validate_tool_put_valid(self):
        data = TH.get_input_tool()
        self.post_tool_checked(data)

        for url in self.base_urls:
            old_name = data['name']
            new_name = "Updated Tool Name"
            data['name'] = new_name
            response = self.validate_tool_put(data['biotoolsID'], data)

            # ensure validation worked
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # ensure update was not executed on database
            get_response = self.get_tool(url, data['biotoolsID'])
            self.assertEqual(get_response.json()['name'], old_name)

    def test_validate_tool_put_invalid(self):
        data = TH.get_input_tool()
        self.post_tool_checked(data)

        for url in self.base_urls:
            name = data['name']  # remove attribute from data
            data.pop('name', None)

            response = self.validate_tool_put(data['biotoolsID'], data)

            # ensure validation worked
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            # ensure update was not executed on database
            get_response = self.get_tool(url, data['biotoolsID'])
            self.assertEqual(get_response.json()['name'], name)

    def test_validate_tool_put_empty(self):
        data = TH.get_input_tool()
        self.post_tool_checked(data)

        for url in self.base_urls:
            name = data['name']
            tool_id = data['biotoolsID']
            data = {'biotoolsID': tool_id}

            response = self.validate_tool_put(data['biotoolsID'], data)

            # ensure validation worked
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            # ensure update was not executed on database
            get_response = self.get_tool(url, data['biotoolsID'])
            self.assertEqual(get_response.json()['name'], name)