import sys

from rest_framework import status
from elixir.serializers import *
from elixirapp.tests.test_baseobject import BaseTestObject
from elixirapp.tests.param_config import query_param_dict as qpd


class TestPage(BaseTestObject):
    def test_page_valid(self):
        """
        Description: Test the 'page' endpoint parameter with valid values.
        Info: Tested on query on all tools.
        Expected: Successful GET Request (200 OK)
        """
        for url in self.base_urls:
            for page_nr in qpd["page"]["valid"]:
                with self.subTest(url=url, page=page_nr):
                    # query tools using page parameter
                    self.ensure_tools(url)
                    response = self.get_all_tools(url, {"page": f"{page_nr}"})
                    self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_page_invalid(self):
        """
        Description: Test the 'page' endpoint parameter with invalid values.
        Info: Tested on query on all tools.
        Expected: Successful GET Request (200 OK)
        """
        for url in self.base_urls:
            for page_nr in qpd["page"]["invalid"]:
                with self.subTest(url=url, page=page_nr):
                    self.ensure_tools(url)
                    # query tools using page parameter
                    with self.assertRaises(Exception):
                        self.get_all_tools(url, {"page": f"{page_nr}"})