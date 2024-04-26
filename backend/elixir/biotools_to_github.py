import logging
import logging.handlers
import json

from github import Github
from github import GithubException
from github import BadCredentialsException
from github import UnknownObjectException

import elixir.ecosystem.settings as ecosystem_settings
from elixir.ecosystem.ecosystem_exceptions import \
    BioToolsException, EcosystemException, EcosystemLoginException, \
    ToolCreationException, ToolUpdateException, ToolDeleteException
from elixir.ecosystem.biotools_handler import BioToolsData
from elixir.ecosystem.github_handler import GithubToolHandler
from django.core.mail import send_mail

def init_ecosystem_logger():
    if not(ecosystem_settings.ECO_LOG_ISSUE):
        return None
    if not(ecosystem_settings.ECO_LOGGER_NAME):
        return None
    if not (ecosystem_settings.ECO_LOG_FILE):
        return None
    try:
        logger = logging.getLogger(ecosystem_settings.ECO_LOGGER_NAME)
        # Perhaps the logger was already created by a previous operation
        if logger.handlers:
            return logger
        logger.setLevel(logging.DEBUG)
        
        # Format of logs
        formatter = logging.Formatter('%(levelname)s::%(asctime)s::%(name)s::%(message)s')
        
        # Log file handler
        file_handler = logging.FileHandler(ecosystem_settings.ECO_LOG_FILE)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger
    except Exception:
        # if there is any problem with the logger setup return None
        return None

def handle_ecosystem_error(logger, the_exception, bt = None, log_exception = False, post_issue = False):

    if ecosystem_settings.ECO_LOG_ISSUE and logger:
        # log the_exception at error level 
        if log_exception:
            logger.exception(str(the_exception))
        else:
            logger.error(str(the_exception))

    if ecosystem_settings.ECO_SEND_EMAIL:
        # send an email with the_exception 
        send_mail(
            subject="Error in ecosystem!",
            message=str(the_exception),
            from_email="support@bio.tools",
            recipient_list=ecosystem_settings.ECO_EMAIL_RECIPIENTS,
            fail_silently=True
        )

    # if we have issue posting enabled and if it's the case to post that issue
    if ecosystem_settings.ECO_POST_GITHUB_ISSUE and post_issue:
        # post the_exception as issue to GitHub
        gth = GithubToolHandler()
        gth.create_issue(bt, str(the_exception))

def get_pr_link(pr_number):
    return "https://github.com/{}/{}/pull/{}".format(
        ecosystem_settings.ECO_GITHUB_ORGANIZATION_NAME,
        ecosystem_settings.ECO_GITHUB_REPO_NAME,
        pr_number
    )


def ecosytem_handle_tool_operations(biotools_user, tool, operation):
    '''
    Makes a CREATE / UPDATE / DELETE (pull) request to the GitHub Ecosystem
    
    Parameters:
    biotools_user (string): The bio.tools username
    tool (dict): The tool annotation
    operation (string): one of 'CREATE', 'UPDATE', 'DELETE'
    '''
    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'



    logger = init_ecosystem_logger()
    
    if operation not in [CREATE, UPDATE, DELETE]:
        handle_ecosystem_error(logger, 'Incorrect operation:' + operation)
        return
            
    
    bt = None
    pr = None
    try:
        # Log attempt to create/update/delete tool
        if ecosystem_settings.ECO_LOG_ISSUE and logger: 
            logger.info('Starting tool {} ...'.format(operation))
        bt = BioToolsData(biotools_user, tool)
        gth = GithubToolHandler()
        if operation == CREATE:
            (_, pr) = gth.create_tool(bt)
        elif operation == UPDATE:
            (_, pr) = gth.update_tool(bt)
        elif operation == DELETE:
            (_, pr) = gth.delete_tool(bt)

        # Log sucessful creation
        if ecosystem_settings.ECO_LOG_ISSUE and logger:
            logger.info('Success! Tool {} PR: {} for tool with id: {} by bio.tools user: {}'.format(
                operation,
                get_pr_link(pr.number),
                bt.tool_id, 
                bt.username  
            ))
    except BioToolsException as e:
        # Log BioTools Exception
        # Send email with the issue
        handle_ecosystem_error(logger, e)
        return  
    except EcosystemLoginException as e:
        # Log EcosystemLoginException
        # Send email with the issue
        handle_ecosystem_error(logger, e, bt)
        return
    except (ToolCreationException, ToolUpdateException, ToolDeleteException, EcosystemException) as e:
        # Log ToolCreationException, ToolUpdateException, ToolDeleteException
        # Send email with the issue
        # create issue on GitHub
        handle_ecosystem_error(logger, e, bt, False, True)
        return
    except GithubException as e:
        # Log any generic GithubException
        # Send email with the issue
        # return from function
        handle_ecosystem_error(logger, e, bt)
        return
    except Exception as e:
        # Log any other Exception
        # check logger is a valid Logger object, perhaps Exception got triggered by the logger
        if logger and type(logger)==logging.Logger:
            handle_ecosystem_error(logger, e, None, True, False)
        else:
            handle_ecosystem_error(None, e)

    return
