# Settings variables
# Read these from environment as well

import os
import json

def getenv(key, default=None, castf=str):
    """
    Helper function to retrieve environment variables.
    """
    value = os.environ.get(key, None)
    return castf(value) if value is not None else default


# Need to give value for these variables from one of the sources:
#   - Environment variables
#   - Secret settings: override variables below in __secret_settings.py file
#   - Replace values in this file: Not recommended because this is git tracked and may be unsafe

# Github organization name is the first part of the github.com/{github_organization_name/{github_repo_name}
ECO_GITHUB_ORGANIZATION_NAME = getenv('ECO_GITHUB_ORGANIZATION_NAME', None)
ECO_GITHUB_TOKEN = getenv('ECO_GITHUB_TOKEN', None)
ECO_GITHUB_REPO_NAME = getenv('ECO_GITHUB_REPO_NAME', None)


# Default values, can be replaced from one of the sources:
#   - Environment variables
#   - Secret settings: override variables below in __secret_settings.py file
#   - Replace values in this file: Not recommended because values might not work in other peoples copies
ECO_MASTER_BRANCH = getenv('ECO_MASTER_BRANCH', 'master')
ECO_ROOT_GITHUB_FOLDER = getenv('ECO_ROOT_GITHUB_FOLDER', 'data')
ECO_BIOTOOLS_EXTENSION =  getenv('ECO_BIOTOOLS_EXTENSION', 'biotools.json')
ECO_DELETED_BRANCH_SUFFIX = getenv('ECO_DELETED_BRANCH_SUFFIX', '__delete')
# recommended to have loggin on by default, saves a lot of hassle
ECO_LOG_ISSUE  = getenv('ECO_LOG_ISSUE', True, castf=bool)
# For the log file we can have a specific bio.tools backend filepath like:
#   /elixir/application/backend/log/ecosytem.log
ECO_LOG_FILE = getenv('ECO_LOG_FILE', 'ecosystem.log')
ECO_LOGGER_NAME = getenv('ECO_LOGGER_NAME', 'ecosystem_logger')
ECO_POST_GITHUB_ISSUE = getenv('ECO_POST_GITHUB_ISSUE', False, castf=bool)
ECO_SEND_EMAIL = getenv('ECO_SEND_EMAIL', False, castf=bool)
ECO_EMAIL_RECIPIENTS = getenv('ECO_EMAIL_RECIPIENTS', [], castf=json.loads)

# not set by default, needs to be set in __secret_settings__.py
ECO_PERSONAL_TOKEN = getenv('ECO_LOGGER_NAME', '')

# Secret settings from "__secret_settings__.py" file that can overide the ones above
# Can also leave the "__secret_settings__.py" file empty if you use environment variables
try:
    from .__secret_settings__ import *
except ImportError:
    pass
