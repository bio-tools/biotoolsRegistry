from rest_framework import status
from elixir.serializers import *
from elixirapp.tests.test_baseobject import BaseTestObject
from elixir.tool_helper import ToolHelper as TH
import time
from elixirapp.tests.parameters.test_query_parameters import TestQueryParameters
from elixirapp.tests.param_config import query_param_dict as qpd


class TestSort(TestQueryParameters):
    """
    Description: Class to test 'sort' endpoint parameter
    Info: Tool 1 is designed to occur before tool_pushed_front by default and second  after sorting.
    """

    def test_sort_valid(self):
        """
        Description: Test the 'sort' endpoint parameter.
        Info: Tested on query on all tools.
        Expected: Successful GET Request (200 OK)
        """
        tool_pushed_back = TH.get_input_tool()
        tool_pushed_front = TH.get_input_tool()

        tool_pushed_back["name"] = f'Alphabetically later {tool_pushed_back["name"]}'
        tool_pushed_front["name"] = f'Alphabetically before {tool_pushed_front["name"]}'

        tool_pushed_back_id = self.post_tool_checked(tool_pushed_back).json()['biotoolsID']
        tool_pushed_front_id = self.post_tool_checked(tool_pushed_front).json()['biotoolsID']

        # TODO ensure correct order concerning every attribute

        time.sleep(1)

        for url in self.base_urls:
            for valid_sort_option in qpd["sort"]["valid"]:  # TODO make option specific or remove for loop
                with self.subTest(sort_option=valid_sort_option):
                    if valid_sort_option == "lastUpdate":
                        self._test_sort_lastUpdate(url, tool_pushed_back_id, tool_pushed_front_id)
                    elif valid_sort_option == "name":
                        self._test_sort_name(url, tool_pushed_back_id, tool_pushed_front_id)
                    elif valid_sort_option == "additionDate":
                        self._test_sort_additionDate(url, tool_pushed_back_id, tool_pushed_front_id)
            for invalid_sort_option in qpd["sort"]["invalid"]:
                with self.subTest(sort_option=invalid_sort_option):
                    self._test_invalid_sort_option(url, invalid_sort_option)

    # HELPERS ----------------------------------------------------------------------------------------------------------
    def __sort_with_option(self, url, sort_option, expected_response_code=status.HTTP_200_OK):
        """
        Description: Helper method to test sorting.
        Returns: Sorted list of tools.
        """
        response = self.get_all_tools(url, {"sort": sort_option})
        self.assertEqual(response.status_code, expected_response_code)
        return response

    def __get_tool_index(self, tool_list, tool_id):
        ids = [tool["biotoolsID"] for tool in tool_list]
        return ids.index(tool_id)

    def __get_tool_attributes(self, url, tool_pushed_back_id, tool_pushed_front_id, attribute_name):
        tool_pushed_back_value = self.get_tool(url, tool_pushed_back_id).json()[attribute_name]
        tool_pushed_front_value = self.get_tool(url, tool_pushed_front_id).json()[attribute_name]
        return tool_pushed_back_value, tool_pushed_front_value

    # TESTING ----------------------------------------------------------------------------------------------------------
    def _test_sort_lastUpdate(self, url, tool_pushed_back_id, tool_pushed_front_id):
        """
        Description: Helper method to test sorting by lastUpdate.
        """
        response = self.get_all_tools(url).json()
        t1_index_before = self.__get_tool_index(response['list'], tool_pushed_back_id)
        t2_index_before = self.__get_tool_index(response['list'], tool_pushed_front_id)

        # get lastUpdate values
        tool_pushed_back_update, tool_pushed_front_update = self.__get_tool_attributes(url, tool_pushed_back_id,
                                                                                       tool_pushed_front_id,
                                                                                       "lastUpdate")

        # sort and get tool indices
        response = self.__sort_with_option(url, 'lastUpdate').json()
        t1_index_after = self.__get_tool_index(response['list'], tool_pushed_back_id)
        t2_index_after = self.__get_tool_index(response['list'], tool_pushed_front_id)

        if tool_pushed_back_update < tool_pushed_front_update:  # tool 1 is older -> expected to have a bigger idx
            self.assertGreater(t1_index_after, t2_index_after)
        else:
            self.assertLess(t1_index_after, t2_index_after)

    def _test_sort_additionDate(self, url, tool_pushed_back_id, tool_pushed_front_id):
        """
        Description: Helper method to test sorting by additionDate.
        """
        # get additionDate values
        tool_pushed_back_update, tool_pushed_front_update = self.__get_tool_attributes(url, tool_pushed_back_id, tool_pushed_front_id, "additionDate")

        # sort and get tool indices
        response = self.__sort_with_option(url, "additionDate").json()
        t1_index = self.__get_tool_index(response["list"], tool_pushed_back_id)
        t2_index = self.__get_tool_index(response["list"], tool_pushed_front_id)

        if tool_pushed_back_update < tool_pushed_front_update:  # tool 1 is older -> expected to have a bigger idx
            self.assertGreater(t1_index, t2_index)
        else:
            self.assertLess(t1_index, t2_index)

    def _test_sort_name(self, url, tool_pushed_back_id, tool_pushed_front_id):
        """
        Description: Helper method to test sorting by name.
        """
        # ensure tools are in incorrect order before sorting
        tool_pushed_back_name, tool_pushed_front_name = self.__get_tool_attributes(url, tool_pushed_back_id, tool_pushed_front_id, "name")

        # sort and get tool indices
        response = self.__sort_with_option(url, "name.raw").json()
        t1_index = self.__get_tool_index(response["list"], tool_pushed_back_id)
        t2_index = self.__get_tool_index(response["list"], tool_pushed_front_id)

        # name of tool 1 is alphabetically smaller -> expected to have a smaller idx after sorting
        self.assertLess(t2_index, t1_index)

    # TODO affiliation and score

    # INVALID ----------------------------------------------------------------------------------------------------------
    def _test_invalid_sort_option(self, sorting_option, url):
        """
        Description: Helper method to test sorting using invalid options.
        """
        response = self.__sort_with_option(url, sorting_option, status.HTTP_404_NOT_FOUND)
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
