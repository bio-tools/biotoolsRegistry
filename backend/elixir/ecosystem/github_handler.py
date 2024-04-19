import json
import os
from datetime import datetime
from github import Github
from github import GithubException
from github import BadCredentialsException
from github import UnknownObjectException
import elixir.ecosystem.settings as ecosystem_settings
from .biotools_handler import BioToolsData
from .ecosystem_exceptions import \
    BioToolsException, EcosystemException, EcosystemLoginException, \
    ToolCreationException, ToolUpdateException, ToolDeleteException


class GithubToolHandler:
    """
    Main GitHub operations handler class
    """
    # Maybe these constants can also be read from outside, like a settings file
    MASTER_BRANCH = ecosystem_settings.ECO_MASTER_BRANCH
    ROOT_GITHUB_FOLDER = ecosystem_settings.ECO_ROOT_GITHUB_FOLDER
    BIOTOOLS_EXTENSION = ecosystem_settings.ECO_BIOTOOLS_EXTENSION
    DELETED_BRANCH_SUFFIX = ecosystem_settings.ECO_DELETED_BRANCH_SUFFIX
    

    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'
    

    # Soon this will need to change as the login will be done with a token
    # For now we use one main GitHub account, e.g. biotools-bot for working
    #   with all the files
    # Later there will be individual github users for which we will
    #   have access by using social auth
    def __init__(self):
        """
        Creates a central handler object from which the main GitHub operations are called. 
        """

        try:
            self.__g = Github(ecosystem_settings.ECO_PERSONAL_TOKEN)
            self.__username = self.__g.get_user().login
            self.__logged_in = True
            self.__repo_name = ecosystem_settings.ECO_GITHUB_REPO_NAME
            self.__repo = self.__g.get_repo(
                ecosystem_settings.ECO_GITHUB_ORGANIZATION_NAME + '/' + self.__repo_name
            )
        except BadCredentialsException as bce:
            self.__logged_in = False
            self.__repo_name = None
            self.__repo = None
            raise EcosystemLoginException(self.__username, ecosystem_settings.ECO_GITHUB_REPO_NAME, str(bce))
        except UnknownObjectException as uoe:
            self.__logged_in = False
            self.__repo_name = None
            self.__repo = None
            raise EcosystemLoginException(self.__username, ecosystem_settings.ECO_GITHUB_REPO_NAME, str(uoe))
        
    def is_logged_in(self):
        return self.__logged_in

    @property
    def repo(self):
        return self.__repo

    def __get_filename(self,tool_id):
        return ".".join([tool_id, self.BIOTOOLS_EXTENSION])

    def __get_branch_name(self, username, tool_id, delete = False):
        return '{u}__{t}{d}'. format(
            u = username,
            t = tool_id,
            d = self.DELETED_BRANCH_SUFFIX if delete else ''
        )
    def __branch_exists(self, branch_name):
        return branch_name in [b.name for b in self.__repo.get_branches()]

    def __pull_request_exists(self, branch_name):
        return branch_name in [pr.head.ref for pr in self.__repo.get_pulls()]

    def __get_pull(self, branch_name):
        return [pr for pr in self.__repo.get_pulls() if pr.head.ref == branch_name]

    def __get_filepath(self, tool_id):
        return os.path.join(self.ROOT_GITHUB_FOLDER, tool_id, self.__get_filename(tool_id))
    
    # Maybe in commit message at a timestamp from the tool
    def __create_commit_message(self, method, username, tool_id):
        return '{m} tool with id: {id} by user: {u} at: {at}'.format(
            m = method, 
            id = tool_id, 
            u = username,
            at = datetime.utcnow().strftime('UTC time: %Y-%m-%d %H:%M:%S')
        )

    def __file_exists(self, filepath, branch_name):
        try:
            self.__repo.get_contents(filepath, ref=branch_name)
            return True
        except GithubException:
            return False
    
    def __get_sha(self, file_path, branch_name):
        """
        Get commit SHA for a file on a branch.
        Raises generic EcosystemException on failure
        """
        try:
            return self.__repo.get_contents(file_path, ref=branch_name).sha
        except GithubException as e:
            raise EcosystemException(
                'Could not update tool, either filepath or branch do not exist.' + str(e),
                branch = branch_name,
                filepath = file_path,
                sha = None,
                username = self.__bt.username,
                tool_id = self.__bt.tool_id
            )
        # Exception missing file , can't find SHA
        # Exception missing file: filepath

    def __create_branch(self, branch_name, from_branch=None):
        """
        Create branch from master.
        Raises generic EcosystemException on failure
        """
        if from_branch:
            from_where = from_branch
        else:
            from_where = self.MASTER_BRANCH

        try:
            mb = self.__repo.get_branch(from_where)
            self.__repo.create_git_ref(ref='refs/heads/' + branch_name, sha=mb.commit.sha)
        except GithubException as e:
            raise EcosystemException(
                'Could not create branch from master branch.' + str(e),
                branch = branch_name,
                filepath = self.__filepath,
                sha = mb.commit.sha,
                username = self.__bt.username,
                tool_id = self.__bt.tool_id
            )
            
    def __create_data(self, branch_name, new_file_path, custom_message = None, custom_content = None): 
        """
        Creates file on branch.
        Raises ToolCreationException if file cannot be created
        """
        

        # Create file on that branch

        # allow for custom messages for the special case of the flagged delete file
        if custom_message:
            commit_message = custom_message
        else:
            commit_message = self.__create_commit_message(
                self.CREATE, 
                self.__bt.username, 
                self.__bt.tool_id
            )

        # This operation may also raise GithubException
        # We deal with it outside by catching GithubException
        #   or we deal with it here and raise generic EcosystemException

        try:
            c = self.__repo.create_file(
                path = new_file_path,
                message = commit_message,
                
                # allow for custom content in case of creating files 
                #   on GitHub from other files on GitHub
                content = custom_content if custom_content else self.__bt.tool_json,
                branch=branch_name
            )
        except GithubException as e:
            raise ToolCreationException(
                'Could not create file.' + str(e),
                branch = branch_name,
                filepath = self.__filepath,
                sha = None,
                username = self.__bt.username,
                tool_id = self.__bt.tool_id
            )

        return c
        # Log repo creation of file above

    def __update_data(self, update_branch_name, update_file_path, file_sha):        
        """
        Update file on branch.
        Raises ToolUpdateException on update fail.
        """
        commit_message = self.__create_commit_message(
            self.UPDATE, 
            self.__bt.username, 
            self.__bt.tool_id
        )
        try:
            u = self.__repo.update_file(
                path = update_file_path,
                message = commit_message,
                content = self.__bt.tool_json,
                branch=update_branch_name,
                sha=file_sha
            )
        except GithubException as e:
            raise ToolUpdateException(
                'Could not update file.' + str(e),
                branch = update_branch_name,
                filepath = update_file_path,
                sha = file_sha,
                username = self.__bt.username,
                tool_id = self.__bt.tool_id
            )
        
        return u
        
    def __delete_data(self, delete_branch_name, delete_file_path, file_sha):

        commit_message = self.__create_commit_message(
            self.DELETE, 
            self.__bt.username, 
            self.__bt.tool_id
        )

        try:
            d = self.__repo.delete_file(
                path = delete_file_path,
                message = commit_message,
                sha = file_sha,
                branch = delete_branch_name
            )
        except GithubException as e:  
            raise ToolDeleteException(
                'Could not delete file.' + str(e),
                branch = delete_branch_name,
                filepath = delete_file_path,
                sha = file_sha,
                username = self.__bt.username,
                tool_id = self.__bt.tool_id
            )
        
        return d

    def __create_pull_request(self, pr_type, username, tool_id, branch_name):
        """
        Creates a pull request for one of the: CREATE, UPDATE, DELETE tool operations.
        Raises one of: 
        ToolCreationException, ToolUpdateException, ToolDeleteException, EcosystemException on fail
        """
        pr_title = '{type} tool with id: {id}'.format(type=pr_type, id=tool_id)
        pr_body = """
        {type} tool with id: {id}
        by user: {user}
        at: {at}
        """.format(
            type=pr_type, 
            id=tool_id, 
            user=username, 
            at = datetime.utcnow().strftime('UTC time: %Y-%m-%d %H:%M:%S')
        )
        try: 
            pr = self.__repo.create_pull(
                title=pr_title, 
                body=pr_body,
                head=branch_name, 
                base=self.MASTER_BRANCH
            )
        except GithubException as e:
            if pr_type == self.CREATE:
                raise ToolCreationException(
                        'Pull request creation failed for tool CREATE operation.'.format(type=pr_type) + str(e),
                        branch = branch_name,
                        filepath = self.__filepath,
                        sha = None,
                        username = username,
                        tool_id = tool_id
                )
            elif pr_type == self.UPDATE:
                raise ToolUpdateException(
                        'Pull request creation failed for tool UPDATE operation.'.format(type=pr_type) + str(e),
                        branch = branch_name,
                        filepath = self.__filepath,
                        sha = None,
                        username = username,
                        tool_id = tool_id
                )
            elif pr_type == self.DELETE:
                raise ToolDeleteException(
                        'Pull request creation failed for tool DELETE operation.'.format(type=pr_type) + str(e),
                        branch = branch_name,
                        filepath = self.__filepath,
                        sha = None,
                        username = username,
                        tool_id = tool_id
                )
            else:
                raise EcosystemException(
                        'Pull request creation failed.'.format(type=pr_type) + str(e),
                        branch = branch_name,
                        filepath = self.__filepath,
                        sha = None,
                        username = username,
                        tool_id = tool_id
                )

        return pr
   
    def __load_data(self, bt, delete = False):
        self.__bt = bt
        self.__branch = self.__get_branch_name(bt.username, bt.tool_id, delete)
        self.__filepath = self.__get_filepath(bt.tool_id)
        self.__time = datetime.utcnow().strftime('UTC time: %Y-%m-%d %H:%M:%S')

    def create_tool(self, biotools_data):
        if not(self.__logged_in):
            raise EcosystemLoginException(
                self.__username, 
                self.__repo_name, 
                'Bad Github user credetials at tool create time.'
            )

        # Load some class level variables for convenience in Exception handling
        self.__load_data(biotools_data)

        new_branch_name = self.__branch
        new_file_path  = self.__filepath

        # Exception brach already exists on tool creation time
        if self.__branch_exists(new_branch_name):
            raise ToolCreationException(
                'Branch already exists at tool creation time.',
                branch = new_branch_name,
                filepath = new_file_path,
                sha = None,
                username = self.__bt.username,
                tool_id = self.__bt.tool_id
            )
            
        # Exception that there is already a PR with this branch name on tool creation time
        if self.__pull_request_exists(new_branch_name):
            raise ToolCreationException(
                'There is already a PR with for the branch name at tool creation time.',
                branch = new_branch_name,
                filepath = new_file_path,
                sha = None,
                username = self.__bt.username,
                tool_id = self.__bt.tool_id
            )
        
        if self.__file_exists(new_file_path, new_branch_name):
            raise ToolCreationException(
                'The file already exists on branch: {b} at tool creation time.'.format(b=new_branch_name),
                branch = new_branch_name,
                filepath = new_file_path,
                sha = None,
                username = self.__bt.username,
                tool_id = self.__bt.tool_id
            )

        if self.__file_exists(new_file_path, self.MASTER_BRANCH):
            raise ToolCreationException(
                'The file already exists on master branch: {b} at tool creation time.'.format(b=self.MASTER_BRANCH),
                branch = new_branch_name,
                filepath = new_file_path,
                sha = None,
                username = self.__bt.username,
                tool_id = self.__bt.tool_id
            )
        
        # Create branch from master
        # Raises EcosystemException
        self.__create_branch(new_branch_name)

        if not self.__branch_exists(new_branch_name):
            raise ToolCreationException(
                'The branch could not be created.',
                branch = new_branch_name,
                filepath = new_file_path,
                sha = None,
                username = self.__bt.username,
                tool_id = self.__bt.tool_id
            )

        # This already creates the file and commits changes to the new branch
        c = self.__create_data(new_branch_name, new_file_path)
        
        if not self.__file_exists(new_file_path, new_branch_name):
            raise ToolCreationException(
                'The file could not be created.',
                branch = new_branch_name,
                filepath = new_file_path,
                sha = None,
                username = self.__bt.username,
                tool_id = self.__bt.tool_id
            )
        
        pr = self.__create_pull_request(
            pr_type=self.CREATE, 
            username=self.__bt.username, 
            tool_id=self.__bt.tool_id, 
            branch_name=new_branch_name
        )

        return (c, pr)

    def update_tool(self, biotools_data):
        if not(self.__logged_in):
            raise EcosystemLoginException(
                self.__username, 
                self.__repo_name, 
                'Bad Github user credetials at tool update time.'
            )
        
        # Load some class level variables for convenience in Exception handling
        self.__load_data(biotools_data)
    
        update_branch_name = self.__branch
        update_file_path  = self.__filepath


        # If branch doesn't exist and file is not on master then we fail
        if not self.__branch_exists(update_branch_name) and not self.__file_exists(update_file_path, self.MASTER_BRANCH):
            raise ToolUpdateException(
                'Branch does not exist on branch {b} and file is not on master branch.'.format(
                    b = update_branch_name
                ),
                branch = update_branch_name,
                filepath = update_file_path,
                sha = None,
                username = self.__bt.username,
                tool_id = self.__bt.tool_id
            )

        # If branch exists but the file doesn't exist then 
        #   we could check if the file is on master branch and if it is then we branch from master
        #   BUT this may be hard to do and it should not happen so we fail and create an issue for now
        #   if the file not on master then it's very weird
        #   we need to create the file rather than updating it... but we should fail and create an issue
        #       In this case we need to create a GitHub issue to report on this
        if self.__branch_exists(update_branch_name) and not self.__file_exists(update_file_path, update_branch_name):
            raise ToolUpdateException(
                'File does not exist on the branch.',
                branch = update_branch_name,
                filepath = update_file_path,
                sha = None,
                username = self.__bt.username,
                tool_id = self.__bt.tool_id
            )

        # if branch doesn't exist (the normal case is that it was merged and deleted)
        #   then recreate the branch from master
        if not self.__branch_exists(update_branch_name):
            # Create branch from master
            self.__create_branch(update_branch_name)

        # This raises EcosystemException on failure
        #   We either deal with it outside or
        #   we catch it here and raise ToolUpdateException
        #  Don't know if we need to be that specific for now
        file_sha = self.__get_sha(update_file_path, update_branch_name)
    
        u = self.__update_data(
            update_branch_name = update_branch_name,
            update_file_path = update_file_path,
            file_sha = file_sha
        )
        
        pr = None

        if not self.__pull_request_exists(update_branch_name):
            pr = self.__create_pull_request(
                pr_type=self.UPDATE, 
                username=self.__bt.username, 
                tool_id=self.__bt.tool_id, 
                branch_name=update_branch_name
            )
        else:
            pr_list = self.__get_pull(update_branch_name)
            if len(pr_list) > 0:
                pr = pr_list[0]
        
        return (u, pr)    

    # Same as update , need to check for existence of branches
    # One difference is that the branch name should contain the word 'delete'
    #   so that we draw more attention to the fact that a tool is being deleted
    #   In this way we also separate the deletion operations from create and update
    def delete_tool(self, biotools_data):
        """
        Delete the tool from the GitHub ecosytem
        """

        if not(self.__logged_in):
            raise EcosystemLoginException(
                self.__username, 
                self.__repo_name, 
                'Bad Github user credetials at tool delete time.'
            )

        # Load some class level variables for convenience in Exception handling
        self.__load_data(biotools_data, delete = True)

        # this is the branch for the whole operations
        delete_branch_name = self.__branch
        delete_file_path = self.__filepath
        
        # Exception brach already exists on tool delete time
        if self.__branch_exists(delete_branch_name):
            raise ToolDeleteException(
                'Branch already exists at tool delete time.',
                branch = delete_branch_name,
                filepath = delete_file_path,
                sha = None,
                username = self.__bt.username,
                tool_id = self.__bt.tool_id
            )
            
        # Exception that there is already a PR with this branch name on tool creation time
        if self.__pull_request_exists(delete_branch_name):
            raise ToolDeleteException(
                'There is already a PR with for the branch name at tool delete time.',
                branch = delete_branch_name,
                filepath = delete_file_path,
                sha = None,
                username = self.__bt.username,
                tool_id = self.__bt.tool_id
            )
        
        
        # Rare case of when user creates the tool and immediately deletes it
        # (This won't happen unless we allow users to delete the tool)
        # if the file doesn't exist on master it could be that it hasn't been merged yet
        #   at creation / update time (most likely fast create + delete or create + update + delete)
        # if it hasn't been merged on GitHub, but there is a PR with maybe we can allow it to go
        file_not_on_master_branch_but_on_update_branch = False
        regular_non_delete_branch = None

        # if the file to delete doesn't exist on master branch
        #   we can look in an "create/update" (non delete) branch to see if it's there
        if not self.__file_exists(delete_file_path, self.MASTER_BRANCH):
            regular_non_delete_branch = self.__get_branch_name(
                self.__bt.username, 
                self.__bt.tool_id 
            )
            
            # We need to have an open pull request with the non delete branch
            #   and of course the actual branch, otherwise we fail
            if not self.__branch_exists(regular_non_delete_branch) or \
                not self.__pull_request_exists(regular_non_delete_branch):
                   raise ToolDeleteException(
                        'The file does not exist on master branch: {b} or on any other user-related branch at tool delete time.'.format(b=self.MASTER_BRANCH),
                        branch = regular_non_delete_branch,
                        filepath = delete_file_path,
                        sha = None,
                        username = self.__bt.username,
                        tool_id = self.__bt.tool_id
                    ) 


            # maybe the file is on the create/update (non delete) branch, then we use that one
            if self.__file_exists(delete_file_path, regular_non_delete_branch):
                file_not_on_master_branch_but_on_update_branch = True
            
            # the file is not on master and also not on a regular CREATE/UPDATE (non delete) branch
            else:
                raise ToolDeleteException(
                    'The file does not exist on any valid branches: {b} at tool delete time.'.format(b=self.MASTER_BRANCH),
                    branch = ", ".join([self.MASTER_BRANCH, regular_non_delete_branch]),
                    filepath = delete_file_path,
                    sha = None,
                    username = self.__bt.username,
                    tool_id = self.__bt.tool_id
                )
        
        # Create the delete branch
        # If the file is not on master, but in a regular create/update (non delete)
        #   then we create delete branch from that non delete branch
        if file_not_on_master_branch_but_on_update_branch:
            self.__create_branch(delete_branch_name, from_branch=regular_non_delete_branch)
        
        # otherwise we branch from master as usual
        else:
            self.__create_branch(delete_branch_name)
            
        # if the file doesn't exist on the newly created delete branch then fail
        if not self.__file_exists(delete_file_path, delete_branch_name):
            raise ToolDeleteException(
                'The file does not exist on branch: {b} at tool delete time.'.format(b=delete_branch_name),
                branch = delete_branch_name,
                filepath = delete_file_path,
                sha = None,
                username = self.__bt.username,
                tool_id = self.__bt.tool_id
            )
        
        # get the SHA of the file to be deleted
        file_sha = self.__get_sha(delete_file_path, delete_branch_name)
        
        d = self.__delete_data(
            delete_branch_name, 
            delete_file_path, 
            file_sha
        )

        # file still exists on delete branch after delete then fail
        if self.__file_exists(delete_file_path, delete_branch_name):
            raise ToolDeleteException(
                'The file was not deleted on branch: {b} at tool delete time.'.format(b=delete_branch_name),
                branch = delete_branch_name,
                filepath = delete_file_path,
                sha = file_sha,
                username = self.__bt.username,
                tool_id = self.__bt.tool_id
            )
        
        pr = self.__create_pull_request(
            pr_type=self.DELETE, 
            username=self.__bt.username, 
            tool_id=self.__bt.tool_id, 
            branch_name=delete_branch_name
        )

        return (d, pr)

    # This function should run once in a while and clean branches
    #   that are not associated with any PRs
    # Note that it could be the case that we have some other branches
    #   that are not used for handling tools and those we can't delete
    # We can have either a naming convention for branches that are 
    #   associated with tools and those we delete if the branch has the 'right' name
    #   or we have a list of branches we ignore from deletion (in addition to master)
    #   but this way seems very tedious to maintain
    # This operation should be run somewhere outside of this class as a separate script
    def clean_branches(self):
        pass
    
    # create an issue if some exception occurs
    # don't know if we should do this here
    # we can return the repo object and allow for issue creation in some other place
    def create_issue(self, biotools_data = None, error_message = None):
        self.__repo.create_issue(
            title = 'Error in ecosystem from bio.tools; tool id: {}'.format(biotools_data.tool_id),
            body = '''
Error in ecosystem from bio.tools:
{}
{}
'''.format(error_message, biotools_data.tool_json)
        )