from rest_framework import status
from elixir.serializers import *
from elixirapp.tests.test_baseobject import BaseTestObject
from elixir.tool_helper import ToolHelper as TH
import time
from elixirapp.tests.parameters.test_query_parameters import TestQueryParameters
from elixirapp.tests.param_config import query_param_dict as qpd


class TestSort(TestQueryParameters):
    def test_sort_valid(self):
        """
        Description: Test the 'sort' endpoint parameter with valid values.
        Info: Tested on query on all tools.
        Expected: Successful GET Request (200 OK)
        """
        for url in self.base_urls:
            for sort_option in qpd["sort"]["valid"]:  # TODO make option specific
                tool1_id = self.post_tool_checked(TH.get_input_tool()).json()['biotoolsID']
                tool2_id = self.post_tool_checked(TH.get_input_tool()).json()['biotoolsID']
                time.sleep(1)
                self._test_sort_lastUpdate(url, tool1_id, tool2_id)
                self._test_sort_name(url, tool1_id, tool2_id)
                self._test_sort_additionDate(url, tool1_id, tool2_id)

    # HELPERS ----------------------------------------------------------------------------------------------------------
    def __sort_with_option(self, url, sort_option):
        """
        Description: Helper method to test sorting.
        Returns: Sorted list of tools.
        """
        response = self.get_all_tools(url, {"sort": sort_option})
        self.assertEqual(response.status_code, 200, f"Failed for sort={sort_option}")
        return response

    def __get_tool_index(self, tool_list, tool_id):
        ids = [tool["biotoolsID"] for tool in tool_list]
        return ids.index(tool_id)

    def __get_tool_attributes(self, url, tool1_id, tool2_id, attribute_name):
        tool1_value = self.get_tool(url, tool1_id).json()[attribute_name]
        tool2_value = self.get_tool(url, tool2_id).json()[attribute_name]
        return tool1_value, tool2_value

    # TESTING ----------------------------------------------------------------------------------------------------------
    def _test_sort_lastUpdate(self, url, tool1_id, tool2_id):
        """
        Description: Helper method to test sorting by lastUpdate.
        """
        # get lastUpdate values
        tool1_update, tool2_update = self.__get_tool_attributes(url, tool1_id, tool2_id, "lastUpdate")

        # sort and get tool indices
        response = self.__sort_with_option(url, 'lastUpdate').json()
        t1_index = self.__get_tool_index(response['list'], tool1_id)
        t2_index = self.__get_tool_index(response['list'], tool2_id)

        if self.compare_dates(tool1_update, tool2_update) == -1:  # tool 1 is older -> expected to have a bigger idx
            self.assertGreater(t1_index, t2_index)
        else:
            self.assertLess(t1_index, t2_index)

    def _test_sort_additionDate(self, url, tool1_id, tool2_id):
        """
        Description: Helper method to test sorting by additionDate.
        """
        # get additionDate values
        tool1_update, tool2_update = self.__get_tool_attributes(url, tool1_id, tool2_id, "additionDate")

        # sort and get tool indices
        response = self.__sort_with_option(url, "additionDate").json()
        t1_index = self.__get_tool_index(response["list"], tool1_id)
        t2_index = self.__get_tool_index(response["list"], tool2_id)

        if self.compare_dates(tool1_update, tool2_update) == -1:  # tool 1 is older -> expected to have a bigger idx
            self.assertGreater(t1_index, t2_index)
        else:
            self.assertLess(t1_index, t2_index)

    def _test_sort_name(self, url, tool1_id, tool2_id):
        """
        Description: Helper method to test sorting by name.
        """
        # get name values
        tool1_name, tool2_name = self.__get_tool_attributes(url, tool1_id, tool2_id, "name")

        # sort and get tool indices
        response = self.__sort_with_option(url, "name.raw").json()
        t1_index = self.__get_tool_index(response["list"], tool1_id)
        t2_index = self.__get_tool_index(response["list"], tool2_id)

        if tool1_name < tool2_name:  # tool 1 is alphabetically smaller -> expected to have a smaller idx
            self.assertLess(t1_index, t2_index)
        else:
            self.assertGreater(t1_index, t2_index)
