from rest_framework import status
from elixir.serializers import *
from elixir.tool_helper import ToolHelper as th
import time
from elixirapp.tests.test_baseobject import BaseTestObject
from elixirapp.tests.param_config import query_param_dict as qpd
from elasticsearch import exceptions as ESExceptions


class TestSort(BaseTestObject):
    """
    Description: Class to test 'sort' and 'ord' endpoint parameters.
    Info: Tool 1 is designed to occur after tool1 by default and second after sorting.
    Note: Note that this test class uses timeouts to ensure the correct order of operations. Tests may fail due to the
          sleeping times being too short, which would not indicate incorrect behaviour of the registry.
    """

    def setup_resources(self):
        tool2 = th.get_input_tool()
        tool1 = th.get_input_tool()

        tool2["name"] = f'Second {tool2["name"]}'
        tool1["name"] = f'First {tool1["name"]}'

        tool2_id = self.post_tool_checked(tool2).json()['biotoolsID']
        time.sleep(1)  # sleep to let server process post

        tool1_id = self.post_tool_checked(tool1).json()['biotoolsID']
        time.sleep(1)  # sleep to let server process post

        # TODO ensure correct order concerning every attribute

        return tool1_id, tool2_id

    def test_sort_valid_order(self):
        """
        Description: Test the 'sort' endpoint parameter with valid values for 'ord'.
        Info: Tested on query on all tools.
        """
        tool1_id, tool2_id = self.setup_resources()

        for url in self.base_urls:
            for valid_order in qpd["ord"]["valid"]:
                if valid_order:
                    self._test_sorting(url, tool1_id, tool2_id, valid_order)
                else:
                    with self.assertRaises(ESExceptions.RequestError):
                        self._test_sorting(url, tool1_id, tool2_id, valid_order)

    def test_sort_invalid_order(self):
        """
        Description: Test the 'sort' endpoint parameter with invalid values for 'ord'.
        Info: Tested on query on all tools.
        """
        tool1_id, tool2_id = self.setup_resources()

        for url in self.base_urls:
            for invalid_order in qpd["ord"]["invalid"]:
                if invalid_order:
                    self._test_sorting(url, tool1_id, tool2_id, invalid_order)
                else:
                    with self.assertRaises(ESExceptions.RequestError):
                        self._test_sorting(url, tool1_id, tool2_id, invalid_order)

    def _test_sorting(self, url, tool1_id, tool2_id, order):
        for valid_sort_option in qpd["sort"]["valid"]:  # TODO make option specific or remove for loop
            with self.subTest(sort_option=valid_sort_option, order=order):
                if valid_sort_option == "lastUpdate":
                    self._test_sort_lastUpdate(url, tool1_id, tool2_id, order)
                elif valid_sort_option == "name":
                    self._test_sort_name(url, tool1_id, tool2_id, order)
                elif valid_sort_option == "additionDate":
                    self._test_sort_additionDate(url, tool1_id, tool2_id, order)
        for invalid_sort_option in qpd["sort"]["invalid"]:
            with self.subTest(url=url, sort_option=invalid_sort_option, order=order):
                self._test_invalid_sort_option(url=url, sorting_option=invalid_sort_option, order=order)

    # HELPERS ----------------------------------------------------------------------------------------------------------
    def __sort_with_option(self, url, sort_option, order="desc"):
        """
        Description: Helper method to test sorting.
        Returns: Sorted list of tools.
        """
        response = self.get_all_tools(url, {"sort": sort_option, "ord": order})
        time.sleep(1)
        return response

    @staticmethod
    def __get_tool_index(tool_list, tool_id):
        ids = [tool["biotoolsID"] for tool in tool_list]
        return ids.index(tool_id)

    def __get_tool_attributes(self, url, tool1_id, tool2_id, attribute_name):
        tool2_value = self.get_tool(url, tool2_id).json()[attribute_name]
        tool1_value = self.get_tool(url, tool1_id).json()[attribute_name]
        return tool1_value, tool2_value

    # TESTING ----------------------------------------------------------------------------------------------------------
    def _test_sort_lastUpdate(self, url, tool1_id, tool2_id, order):
        """
        Description: Helper method to test sorting by lastUpdate.
        """
        response = self.get_all_tools(url).json()
        t1_index_before = TestSort.__get_tool_index(response['list'], tool2_id)
        t2_index_before = TestSort.__get_tool_index(response['list'], tool1_id)

        if t2_index_before > t1_index_before:
            raise RuntimeWarning("[WARNING] Test for sorting with 'lastUpdate' is not sufficient as tools were in"
                                 "correct order before sorting.")  # TODO delegate to message file

        # get lastUpdate values
        tool1_update, tool2_update = self.__get_tool_attributes(url, tool1_id, tool2_id, "lastUpdate")
        t1_update_is_more_recent = tool1_update > tool2_update

        # sort and get tool indices
        response = self.__sort_with_option(url=url, sort_option='lastUpdate', order=order)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_json = response.json()
        t1_index_after = TestSort.__get_tool_index(response_json['list'], tool2_id)
        t2_index_after = TestSort.__get_tool_index(response_json['list'], tool1_id)

        try:
            if (t1_update_is_more_recent and order == 'desc') or (not t1_update_is_more_recent and order == 'asc'):
                self.assertGreater(t1_index_after, t2_index_after,
                                   f"'{tool1_update}' was listed before '{tool2_update}'"
                                   f" when ordering by lastUpdate (order='{order}')")
            elif (t1_update_is_more_recent and order == 'asc') or (not t1_update_is_more_recent and order == 'desc'):
                self.assertLess(t1_index_after, t2_index_after, f"'{tool1_update}' was listed after '{tool2_update}'"
                                                                f" when ordering by lastUpdate (order='{order}')")
        except ESExceptions.RequestError:
            raise


    def _test_sort_additionDate(self, url, tool1_id, tool2_id, order):
        """
        Description: Helper method to test sorting by additionDate.
        """
        # get additionDate values
        tool1_update, tool2_update = self.__get_tool_attributes(url, tool1_id, tool2_id, "additionDate")
        t2_is_older = tool2_update < tool1_update

        # sort and get tool indices
        response = self.__sort_with_option(url=url, sort_option="additionDate", order=order)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        t1_index = TestSort.__get_tool_index(response_json["list"], tool2_id)
        t2_index = TestSort.__get_tool_index(response_json["list"], tool1_id)

        try:
            if (order == 'asc' and t2_is_older) or (order == 'desc' and not t2_is_older):
                self.assertLess(t1_index, t2_index, f"{tool1_update} was listed after {tool2_update}"
                                                                   f" when ordering by additionDate (order='{order}')")
            elif (order == 'desc' and t2_is_older) or (order == 'asc' and not t2_is_older):
                self.assertGreater(t1_index, t2_index, f"{tool1_update} was listed before {tool2_update}"
                                                                   f" when ordering by additionDate (order='{order}')")
        except ESExceptions.RequestError:
            raise

    def _test_sort_name(self, url, tool1_id, tool2_id, order):
        """
        Description: Helper method to test sorting by name.
        """
        tool1_name, tool2_name = self.__get_tool_attributes(url, tool1_id, tool2_id, "name")
        t1_is_alphabetically_smaller = tool1_name < tool2_name

        # sort and get tool indices
        response = self.__sort_with_option(url=url, sort_option="name.raw", order=order)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        t1_index = TestSort.__get_tool_index(response_json["list"], tool1_id)
        t2_index = TestSort.__get_tool_index(response_json["list"], tool2_id)

        if (order == "asc" and t1_is_alphabetically_smaller) or (order == "desc" and not t1_is_alphabetically_smaller):
            self.assertLess(t1_index, t2_index, f"'{tool1_name}' was listed after '{tool2_name}'"
                                                               f" when ordering by name (order='{order}')")
        elif (order == "desc" and t1_is_alphabetically_smaller) or (order == "asc" and not t1_is_alphabetically_smaller):
            self.assertGreater(t1_index, t2_index, f"'{tool1_name}' was listed before '{tool2_name}'"
                                                               f" when ordering by name (order='{order}')")
        # TODO refer to error message file

    # INVALID ----------------------------------------------------------------------------------------------------------
    def _test_invalid_sort_option(self, url, sorting_option, order):
        """
        Description: Helper method to test sorting using invalid options.
        Info: Invalid options do not necessarily result in a 404 or 400 error, which is why there is a fallback for
              200 returns, where the test function ensures that the data is not changed.
        """
        tools_default = self.get_all_tools(url).json()['count']  # TODO handle differently
        self.__sort_with_option(url=url, sort_option=sorting_option, order=order)
        tools_after = self.get_all_tools(url).json()['count']
        self.assertEqual(tools_after, tools_default)
