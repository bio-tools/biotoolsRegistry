from rest_framework import status
from elixir.test_datastructure_json import inputTool, inputToolInvalid
from elixir.serializers import *
from backend.elixirapp.tests.test_baseobject import BaseTestObject


class TestTool(BaseTestObject):

    # GET LIST ---------------------------------------------------------------------------------------------------------
    def test_get_all_tools(self):
        self.post_tool_checked(inputTool())
        response = self.client.get(self.base_url, HTTP_ACCEPT='application/json')
        self.assertGreater(response.json()['count'], 0)

    # POST -------------------------------------------------------------------------------------------------------------
    def test_post_tool_valid(self):
        for url in self.base_urls:
            response = self.post_tool(url, inputTool())
            # ensure post worked
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_tool_invalid(self):
        for url in self.base_urls:
            response = self.post_tool(url, inputToolInvalid())
            # ensure post did not work
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_tool_empty(self):
        for url in self.base_urls:
            response = self.post_tool(url, {})
            # ensure post did not work
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # GET --------------------------------------------------------------------------------------------------------------
    def test_get_tool_valid(self):
        for url in self.base_urls:
            data = inputTool()
            self.post_tool_checked(data)
            response = self.get_tool(url, data['biotoolsID'])
            # ensure get worked and correct resource was returned
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()['name'], data['name'])

    def test_get_tool_invalid(self):
        for url in self.base_urls:
            response = self.get_tool(url, 'invalid_id')
            # ensure get did not work
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # PUT --------------------------------------------------------------------------------------------------------------
    def test_put_tool_valid(self):
        for url in self.base_urls:
            # create tool
            data = inputTool()
            self.post_tool_checked(data)

            # update tool
            old_name = data['name']
            new_name = "Updated Tool Name"
            data['name'] = new_name

            response = self.put_tool(url, data)

            # ensure update worked
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()['name'], new_name)

    def test_put_tool_invalid(self):
        for url in self.base_urls:
            data = inputTool()
            self.post_tool_checked(data)

            # update tool
            name = data['name']
            data.pop('name', None)

            response = self.put_tool(url, data)

            # ensure update did not work
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            get_response = self.get_tool(url, data['biotoolsID'])
            self.assertEqual(get_response.json()['name'], name)

    def test_put_tool_unchanged(self):
        # post tool
        data = inputTool()
        self.post_tool_checked(data)
        
        for url in self.base_urls:
            # update tool
            response = self.put_tool(url, data)
            # ensure update worked
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    # DELETE -----------------------------------------------------------------------------------------------------------
    def test_delete_tool_valid(self):
        for url in self.base_urls:
            data = inputTool()
            self.post_tool_checked(data)

            response = self.remove_tool(url, data['biotoolsID'])

            # ensure delete worked
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            get_response = self.get_tool(url, data['biotoolsID'])
            self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_tool_invalid(self):
        for url in self.base_urls:
            invalid_id = 'invalid_tool'
            response = self.remove_tool(url, invalid_id)
            # ensure delete did not work
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            get_response = self.get_tool(url, invalid_id)
            self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

    # VALIDATE ---------------------------------------------------------------------------------------------------------
    def test_validate_tool_post_valid(self):
        data = inputTool()
        for url in self.base_urls:
            response = self.validate_tool_post(url, data)

            # ensure validation worked
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # ensure tool was not added to database
            get_response = self.get_tool(url, data['biotoolsID'])
            self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_validate_tool_post_invalid(self):
        data = inputToolInvalid()
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
        data = inputTool()
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
        data = inputTool()
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
        data = inputTool()
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

    # todo single attributes