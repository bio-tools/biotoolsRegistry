from rest_framework import status
from elixir.tool_helper import ToolHelper as TH
from elixir.serializers import *
from elixirapp.tests.test_baseobject import BaseTestObject
from elixir.models import Resource


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

        url = self.put_post_urls[0]

        # update tool: stores fingerprint (version_hash was NULL after POST)
        response = self.put_tool(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("no_changes", response.json(), "First identical PUT should not be a no-op")

        # second put: same payload, should be a no-op
        # capture state
        visible_rows = Resource.objects.filter(biotoolsID=data['biotoolsID'], visibility=1)
        all_rows = Resource.objects.filter(biotoolsID=data['biotoolsID'])
        visible_rows_count = visible_rows.count()
        
        self.assertEqual(visible_rows_count, 1, "There should be one visible row for the resource")

        # capture the state of the resource before the second PUT
        row_count_before = all_rows.count()    
        last_update_before = visible_rows.first().lastUpdate
        version_hash_before = visible_rows.first().version_hash

        response = self.put_tool(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("no_changes", response.json(), "Second identical PUT should be a no-op")

        self.assertEqual(Resource.objects.filter(biotoolsID=data['biotoolsID'], visibility=1).count(), 1, "Visible row count should remain the same after no-op PUT")
        self.assertEqual(Resource.objects.filter(biotoolsID=data['biotoolsID']).count(), row_count_before, "Total row count should remain the same after no-op PUT")

        self.assertEqual(Resource.objects.get(biotoolsID=data['biotoolsID'], visibility=1).lastUpdate, last_update_before, "lastUpdate should remain the same after no-op PUT")

        self.assertEqual(Resource.objects.get(biotoolsID=data['biotoolsID'], visibility=1).version_hash, version_hash_before, "version_hash should remain the same after no-op PUT")

    def test_put_tool_changed_still_updates(self):
        data = TH.get_input_tool()
        self.post_tool_checked(data)

        # prime the fingerprint
        self.put_tool(url := self.put_post_urls[0], data)

        # make a real change
        data['description'] = 'A genuinely different description.'

        response = self.put_tool(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.json().get('no_changes'))
        self.assertEqual(
            Resource.objects.get(biotoolsID=data['biotoolsID'], visibility=1).description,
            'A genuinely different description.')

    def test_put_tool_reordered_lists_no_change(self):
        data = TH.get_input_tool()
        self.post_tool_checked(data)
        url = self.put_post_urls[0]

        # prime the fingerprint
        self.put_tool(url, data)

        # reverse every top-level list, content identical
        reordered = dict(data)
        for key, value in data.items():
            if isinstance(value, list):
                reordered[key] = list(reversed(value))

        response = self.put_tool(url, reordered)
        self.assertTrue(response.json().get('no_changes'),
                    'Reordered lists should be treated as unchanged')
