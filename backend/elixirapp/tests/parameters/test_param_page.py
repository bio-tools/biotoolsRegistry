import sys

from rest_framework import status
from elixir.serializers import *
from elixirapp.tests.test_baseobject import BaseTestObject
from elixir.tool_helper import ToolHelper as TH
import time
from elixirapp.tests.parameters.test_query_parameters import TestQueryParameters
from elixirapp.tests.param_config import query_param_dict as qpd
from backend.elixirapp.tests.login_data import valid_user_registration_data, user_registration_data_invalid_p2, \
    user_registration_data_missing_email, user_registration_data_missing_username, user_registration_data_missing_p1, \
    user_registration_data_missing_p2, valid_user_login_data, invalid_user_login_data, \
    other_valid_user_1_registration_data, other_valid_user_1_login_data, other_valid_user_2_registration_data, \
    other_valid_user_2_login_data, superuser_registration_data, superuser_login_data

class TestPage(TestQueryParameters):
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