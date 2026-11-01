from rest_framework.exceptions import APIException


class ManagementUnavailable(APIException):
    status_code = 503
    default_detail = 'The index update could not be confirmed. Reload the current record before retrying; an administrator may need to repair the index.'
