import sys

from rest_framework import status

from elixir.serializers import *
from elixir.tool_helper import ToolHelper as TH
from elixirapp.tests.param_config import query_param_dict as qpd
from elixirapp.tests.test_baseobject import BaseTestObject


class TestFormat(BaseTestObject):

    # FORMAT -----------------------------------------------------------------------------------------------------------
    def test_format_valid(self):
        """
        Description: Test the 'format' endpoint parameter with valid values.
        Info: Tested on query on a particular tool.
        Expected: Successful GET Request (200 OK)
        """
        for valid_format in qpd["format"]["valid"]:
            for url in self.base_urls:
                with self.subTest(url=url, format=valid_format):
                    data = TH.get_input_tool()
                    self.post_tool_checked(data)
                    response = self.get_tool(
                        url, data["biotoolsID"], {"format": valid_format}
                    )
                    self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_format_invalid(self):
        """
        Description: Test the 'format' endpoint parameter with invalid values.
        Info: Tested on query on a particular tool.
        Expected: Unsuccessful GET Request (404 NOT FOUND)
        """
        for invalid_format in qpd["format"]["invalid"]:
            for url in self.base_urls:
                with self.subTest(url=url, format=invalid_format):
                    data = TH.get_input_tool()
                    self.post_tool_checked(data)
                    tools_default = self.get_all_tools(url).json()[
                        "count"
                    ]  # TODO modify and outsource

                    response = self.get_tool(
                        url, data["biotoolsID"], {"format": invalid_format}
                    )

                    tools_after = self.get_all_tools(url).json()["count"]

                    if (
                        response.status_code != status.HTTP_404_NOT_FOUND
                        and tools_after != tools_default
                    ):
                        self.fail()
