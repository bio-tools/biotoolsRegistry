from .ecosystem_exceptions import BioToolsException
import json
# We can maybe add here a delete flag
#   Because we don't technically need the bio.tools JSON data when we delete the tool
#   But we still need the tool id
#   We could pass the tool id in a different way, but technically we can still obtain the full tool JSON
#       even if we delete the tool
# 
class BioToolsData(object):
    __ID_KEY = 'biotoolsID'
    def __init__(self, username, tool_json_string, delete = False, tool_id = None):

        # We can look in bio.tools for this username if we really want to make sure
        #   but since this code is for now called from bio.tools backend we don't really have to
        if not(username):
            raise BioToolsException(username, tool_json_string, 'No valid bio.tools username was provided.')

        # TODO decide if we use the @delete parameter. If we use it we need to maybe also add a delete @property
        # TODO decide if we use the @tool_id parameter
        
        self.__username = username

        if not(tool_json_string):
            raise BioToolsException(username, tool_json_string, 'Missing tool JSON data.')

        try:
            self.__tool = json.loads(tool_json_string)
        except ValueError as v:
            raise BioToolsException(username, tool_json_string, 'Invalid tool JSON structure. ' + str(v))
        
        self.__tool_json_string = tool_json_string
        
        if not(self.validate_tool()):
            raise BioToolsException(username, tool_json_string, 'Invalid tool data.')

        self.__tool_id = self.__tool.get(self.__ID_KEY)

    def validate_tool(self):
        # TODO validation
        # This should already be valid since it gets called
        #   from bio.tools after validation has been done
        
        if self.__tool.get(self.__ID_KEY) == None:
            raise BioToolsException(self.__username, self.__tool_json_string, 'Missing tool id.')

        return True
    
    @property
    def username(self):
        return self.__username

    @property
    def tool_json(self):
        return self.__tool_json_string

    @property
    def tool_id(self):
        return self.__tool.get(self.__ID_KEY)

    # @property
    # def delete(self):
    #     return self.__delete
