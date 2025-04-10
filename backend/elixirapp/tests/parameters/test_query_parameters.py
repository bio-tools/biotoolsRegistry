from rest_framework import status
from elixir.serializers import *
from elixirapp.tests.test_baseobject import BaseTestObject
from elixir.tool_helper import ToolHelper as TH
import time


class TestQueryParameters(BaseTestObject):

    # HELPERS ----------------------------------------------------------------------------------------------------------

    def compare_dates(self, date1, date2):
        return None  # TODO delete

    # # Q ----------------------------------------------------------------------------------------------------------------
    # def test_q(self):
    #     # TODO test substrings and all that
    #     return None
#
#     # ORD --------------------------------------------------------------------------------------------------------------
#     def test_ord(self):
#         return None
#
#     # ATTRIBUTES -------------------------------------------------------------------------------------------------------
#
#     def test_parameter_biotoolsID_valid(self):
#         """
#         Description: Test the 'biotoolsID' parameter with a valid value.
#         """
#         posted_tool = self.post_tool_checked(TH.get_input_tool()).json()
#         tool_id = posted_tool["biotoolsID"]
#
#         for url in self.base_urls:
#             tool = self.get_tool(url, tool_id, {"biotoolsID": tool_id}).json()
#             self.assertEqual(posted_tool, tool)
#
#     def test_parameter_biotoolsID_invalid(self):
#         """
#         Description: Test the 'biotoolsID' parameter with an invalid value.
#         """
#
#
#     def test_parameter_name(self):
#         return None
#
#     def test_parameter_homepage(self):
#         return None
#
#     def test_parameter_description(self):
#         return None
#
#     def test_parameter_version(self):
#         return None
#
#     def test_parameter_topic(self):
#         return None
#
#     def test_parameter_topicID(self):
#         return None
#
#     def test_parameter_function(self):
#         return None
#
#     def test_parameter_operation(self):
#         return None
#
#     def test_parameter_operationID(self):
#         return None
#
#     def test_parameter_dataType(self):
#         return None
#
#     def test_parameter_dataTypeID(self):
#         return None
#
#     def test_parameter_dataFormat(self):
#         return None
#
#     def test_parameter_dataFormatID(self):
#         return None
#
#     def test_parameter_input(self):
#         return None
#
#     def test_parameter_inputID(self):
#         return None
#
#     def test_parameter_inputDataType(self):
#         return None
#
#     def test_parameter_inputDataTypeID(self):
#         return None
#
#     def test_parameter_inputDataFormat(self):
#         return None
#
#     def test_parameter_inputDataFormatID(self):
#         return None
#
#     def test_parameter_output(self):
#         return None
#
#     def test_parameter_outputID(self):
#         return None
#
#     def test_parameter_outputDataType(self):
#         return None
#
#     def test_parameter_outputDataTypeID(self):
#         return None
#
#     def test_parameter_outputDataFormat(self):
#         return None
#
#     def test_parameter_outputDataFormatID(self):
#         return None
#
#     def test_parameter_toolType(self):
#         return None
#
#     def test_parameter_collectionID(self):
#         return None
#
#     def test_parameter_maturity(self):
#         return None
#
#     def test_parameter_operatingSystem(self):
#         return None
#
#     def test_parameter_language(self):
#         return None
#
#     def test_parameter_cost(self):
#         return None
#
#     def test_parameter_license(self):
#         return None
#
#     def test_parameter_accessibility(self):
#         return None
#
#     def test_parameter_credit(self):
#         return None
#
#     def test_parameter_creditName(self):
#         return None
#
#     def test_parameter_creditTypeRole(self):
#         return None
#
#     def test_parameter_creditTypeEntity(self):
#         return None
#
#     def test_parameter_creditOrcidID(self):
#         return None
#
#     def test_parameter_publication(self):
#         return None
#
#     def test_parameter_publicationID(self):
#         return None
#
#     def test_parameter_publicationType(self):
#         return None
#
#     def test_parameter_publicationVersion(self):
#         return None
#
#     def test_parameter_link(self):
#         return None
#
#     def test_parameter_linkType(self):
#         return None
#
#     def test_parameter_documentation(self):
#         return None
#
#     def test_parameter_documentationType(self):
#         return None
#
#     def test_parameter_download(self):
#         return None
#
#     def test_parameter_downloadType(self):
#         return None
#
#     def test_parameter_downloadVersion(self):
#         return None
#
#     def test_parameter_otherID(self):
#         return None
#
#     def test_parameter_otherIDValue(self):
#         return None
#
#     def test_parameter_otherIDType(self):
#         return None
#
#     def test_parameter_otherIDVersion(self):
#         return None
#
# # TODO conditions in https://biotools.readthedocs.io/en/latest/api_usage_guide.html
