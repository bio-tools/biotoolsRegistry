import sys

from rest_framework import status
from elixir.serializers import *
from backend.elixirapp.tests.test_baseobject import BaseTestObject
from elixir.tool_helper import ToolHelper as TH


class TestQueryParameters(BaseTestObject):
    query_param_dict = {
        "page": {"valid": [1, sys.maxsize], "invalid": ["invalid", ""]},
        "format": {"valid": ["json", "xml", "yaml", ""], "invalid": ["invalid"]},
        # TODO api returns 406, empty shouldn't work i guess
        "sort": {"valid": ["lastUpdate", "additionDate", "name", "affiliation", "score"], "invalid": ["invalid", ""]},
        # TODO empty shouldn't work i guess
        "biotoolsID": {"valid": [], "invalid": ["invalid", ""]}
    }

    # HELPERS ----------------------------------------------------------------------------------------------------------
    def ensure_tools(self, url):
        """
        Description: Post tool to ensure there is at least one tool on the server.
        Throws: RuntimeError if there are no tools on the server.
        """
        number_tools = self.get_all_tools(url).json()['count']
        if number_tools > 0: return
        # create tool
        data = TH.get_input_tool()
        self.post_tool_checked(data)
        number_tools = self.get_all_tools(url).json()['count']
        if number_tools < 1:
            raise RuntimeError("No tools on the test server.")

    def compare_dates(self, date1, date2):
        """
        Description: Compare 2 dates using dateutil.parser.
        Throws: ValueError if one of the dates cannot be parsed.
        Returns:
            - 1 if date1 is after date2
            - 0 if the dates are the same
            - -1 if date1 is before date2
        """
        from dateutil import parser

        try:
            date1_obj = parser.parse(date1)
            date2_obj = parser.parse(date2)

            if date1_obj > date2_obj:
                return 1
            elif date1_obj < date2_obj:
                return -1
            else:
                return 0
        except ValueError:
            return "Invalid date format."

    # PAGE -------------------------------------------------------------------------------------------------------------

    def test_page_valid(self):
        """
        Description: Test the 'page' endpoint parameter with valid values.
        Info: Tested on query on all tools.
        Expected: Successful GET Request (200 OK)
        """
        for url in self.base_urls:
            for page_nr in self.query_param_dict["page"]["valid"]:
                with self.subTest(url=url, page=page_nr):
                    # query tools using page parameter
                    self.ensure_tools(url)
                    response = self.get_all_tools(url, {"page": f"{page_nr}"})
                    self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_page_invalid(self):  # TODO recheck result; else refactor dictionary and delete this method
        """
        Description: Test the 'page' endpoint parameter with invalid values.
        Info: Tested on query on all tools.
        Expected: Successful GET Request (200 OK)
        """
        for url in self.base_urls:
            for page_nr in self.query_param_dict["page"]["invalid"]:
                with self.subTest(url=url, page=page_nr):
                    self.ensure_tools(url)
                    # query tools using page parameter
                    response = self.get_all_tools(url, {"page": f"{page_nr}"})
                    self.assertEqual(response.status_code, status.HTTP_200_OK)

    # FORMAT -----------------------------------------------------------------------------------------------------------
    def test_format_valid(self):
        """
        Description: Test the 'format' endpoint parameter with valid values.
        Info: Tested on query on a particular tool.
        Expected: Successful GET Request (200 OK)
        """
        for valid_format in self.query_param_dict["format"]["valid"]:
            for url in self.base_urls:
                with self.subTest(url=url, format=valid_format):
                    data = TH.get_input_tool()
                    self.post_tool_checked(data)
                    response = self.get_tool(url, data['biotoolsID'], {"format": valid_format})
                    self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_format_invalid(self):
        """
        Description: Test the 'format' endpoint parameter with invalid values.
        Info: Tested on query on a particular tool.
        Expected: Unsuccessful GET Request (404 NOT FOUND)
        """
        for invalid_format in self.query_param_dict["format"]["invalid"]:
            for url in self.base_urls:
                with self.subTest(url=url, format=invalid_format):
                    data = TH.get_input_tool()
                    self.post_tool_checked(data)
                    response = self.get_tool(url, data['biotoolsID'], {"format": invalid_format})
                    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Q ----------------------------------------------------------------------------------------------------------------
    def test_q(self):
        # TODO test substrings and all that
        return None

    # SORT -------------------------------------------------------------------------------------------------------------
    def test_sort_valid(self):
        """
        Description: Test the 'sort' endpoint parameter with valid values.
        Info: Tested on query on all tools.
        Expected: Successful GET Request (200 OK)
        """
        for url in self.base_urls:
            for sort_option in self.query_param_dict["sort"]["valid"]:
                self._test_sort_lastUpdate(url)

    def _test_sort_lastUpdate(self, url):
        """
        Description: Helper method to test sorting by lastUpdate.
        """
        all_tools = self.get_all_tools(self.base_url).json()['list']
        self.remove_all_tools([t['biotoolsID'] for t in all_tools])
        # post tool and save id
        tool1_id = self.post_tool_checked(TH.get_input_tool()).json()['biotoolsID']
        tool2_id = self.post_tool_checked(TH.get_input_tool()).json()['biotoolsID']

        # get lastUpdate values
        tool1_update = self.get_tool(url, tool1_id).json()['lastUpdate']
        tool2_update = self.get_tool(url, tool2_id).json()['lastUpdate']

        # check which tool was updated more recently
        is_tool1_older = self.compare_dates(tool1_update, tool2_update) == 1
        response = self._sort_with_option(url, 'lastUpdate').json()

        matches = response['count']
        max_page = matches % 50 + 1

        print(f"matches: {matches} || pages: {max_page}")

        # get tool indices
        t1_index = self.__get_tool_index(response['list'], tool1_id)
        t2_index = self.__get_tool_index(response['list'], tool2_id)

        print(f"blub {t1_index}, {t2_index}")

        if is_tool1_older:  # older -> date is smaller -> should be later in list (bigger index)
            self.assertGreater(t1_index, t2_index)
        else: self.assertLessEqual(t1_index, t2_index)

    def _sort_with_option(self, url, sort_option):
        """
        Description: Helper method to test sorting.
        Returns: Sorted list of tools.
        """
        response = self.get_all_tools(url, {"sort": sort_option})
        self.assertEqual(response.status_code, 200, f"Failed for sort={sort_option}")

        return response

    def __get_tool_index(self, tool_list, tool_id):
        ids = [tool["biotoolsID"] for tool in tool_list]
        print(f"BLUB || IDs: {ids} ({len(ids)}) || ID_LATER: {tool_id} || IS IN LIST: {tool_id in ids}")
        print(f"IDX: {ids.index(tool_id)}")
        return ids.index(tool_id)

    def test_sort_additional_filter_valid(self):
        """
        Description: Test the 'sort' endpoint parameter with valid values and the Name.
        Info: Tested on query on all tools.
        Expected: Unsuccessful GET Request (404 NOT FOUND)
        """

    # ORD --------------------------------------------------------------------------------------------------------------
    def test_ord(self):
        return None

    # ATTRIBUTES -------------------------------------------------------------------------------------------------------

    def test_parameter_biotoolsID_valid(self):
        """
        Description: Test the 'biotoolsID' parameter with a valid value.
        """
        posted_tool = self.post_tool_checked(TH.get_input_tool()).json()
        tool_id = posted_tool["biotoolsID"]

        for url in self.base_urls:
            tool = self.get_tool(url, tool_id, {"biotoolsID": tool_id}).json()
            self.assertEqual(posted_tool, tool)

    def test_parameter_biotoolsID_invalid(self):
        """
        Description: Test the 'biotoolsID' parameter with an invalid value.
        """


    def test_parameter_name(self):
        return None

    def test_parameter_homepage(self):
        return None

    def test_parameter_description(self):
        return None

    def test_parameter_version(self):
        return None

    def test_parameter_topic(self):
        return None

    def test_parameter_topicID(self):
        return None

    def test_parameter_function(self):
        return None

    def test_parameter_operation(self):
        return None

    def test_parameter_operationID(self):
        return None

    def test_parameter_dataType(self):
        return None

    def test_parameter_dataTypeID(self):
        return None

    def test_parameter_dataFormat(self):
        return None

    def test_parameter_dataFormatID(self):
        return None

    def test_parameter_input(self):
        return None

    def test_parameter_inputID(self):
        return None

    def test_parameter_inputDataType(self):
        return None

    def test_parameter_inputDataTypeID(self):
        return None

    def test_parameter_inputDataFormat(self):
        return None

    def test_parameter_inputDataFormatID(self):
        return None

    def test_parameter_output(self):
        return None

    def test_parameter_outputID(self):
        return None

    def test_parameter_outputDataType(self):
        return None

    def test_parameter_outputDataTypeID(self):
        return None

    def test_parameter_outputDataFormat(self):
        return None

    def test_parameter_outputDataFormatID(self):
        return None

    def test_parameter_toolType(self):
        return None

    def test_parameter_collectionID(self):
        return None

    def test_parameter_maturity(self):
        return None

    def test_parameter_operatingSystem(self):
        return None

    def test_parameter_language(self):
        return None

    def test_parameter_cost(self):
        return None

    def test_parameter_license(self):
        return None

    def test_parameter_accessibility(self):
        return None

    def test_parameter_credit(self):
        return None

    def test_parameter_creditName(self):
        return None

    def test_parameter_creditTypeRole(self):
        return None

    def test_parameter_creditTypeEntity(self):
        return None

    def test_parameter_creditOrcidID(self):
        return None

    def test_parameter_publication(self):
        return None

    def test_parameter_publicationID(self):
        return None

    def test_parameter_publicationType(self):
        return None

    def test_parameter_publicationVersion(self):
        return None

    def test_parameter_link(self):
        return None

    def test_parameter_linkType(self):
        return None

    def test_parameter_documentation(self):
        return None

    def test_parameter_documentationType(self):
        return None

    def test_parameter_download(self):
        return None

    def test_parameter_downloadType(self):
        return None

    def test_parameter_downloadVersion(self):
        return None

    def test_parameter_otherID(self):
        return None

    def test_parameter_otherIDValue(self):
        return None

    def test_parameter_otherIDType(self):
        return None

    def test_parameter_otherIDVersion(self):
        return None

# TODO conditions in https://biotools.readthedocs.io/en/latest/api_usage_guide.html
