from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from elixir.views import Ontology, User
from django.core import mail
from django.test import TestCase, override_settings
from elasticsearch import Elasticsearch
from elasticsearch import exceptions as ESExceptions
from django.conf import settings
from elixir.tool_helper import ToolHelper as TH
from elixirapp.tests.login_data import superuser_registration_data
from elixir.management.commands.parse_edam import Command


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class BaseTestObject(TestCase):
    # TOKENS -----------------------------------------------------------------------------------------------------------
    tokens = {}

    # URLS -------------------------------------------------------------------------------------------------------------
    base_url = '/tool/'
    put_post_urls = ['/tool/']
    base_urls = ['/tool/']
    validation_url_extension = 'validate/'
    user_list_url = '/user-list/'
    auth_url = '/rest-auth/'
    registration_url = f"{auth_url}registration/"
    login_url = f"{auth_url}login/"
    logout_url = f"{auth_url}logout/"
    user_info_url = f"{auth_url}user/"
    change_password_url = f"{auth_url}password/change/"
    password_reset_url = f"{auth_url}password/reset/"
    password_reset_confirm_url = f"{auth_url}password/reset/confirm/"

    # BASE METHODS -----------------------------------------------------------------------------------------------------

    def pop_email(self, email_recipient, email_subject):
        # Pop (and return) email from queue if it has the expected recipient and subject
        self.assertNotEquals(len(mail.outbox), 0, f"Mail queue should not be empty")
        self.assertEqual(mail.outbox[0].to, [email_recipient],
                         f"Mail with recipient {email_recipient} was not found in mail queue. Current content: {self._mail_to_str()}")
        self.assertEqual(mail.outbox[0].subject, email_subject,
                         f"Mail with subject {email_subject} was not found in mail queue. Current content: {self._mail_to_str()}")
        return mail.outbox.pop(0)

    def assert_mail_empty(self):
        # Make sure the mail queue is empty
        self.assertEqual(len(mail.outbox), 0, f"Mail queue should have been empty. Current contents: {self._mail_to_str()}")

    def post_tool(self, url, data):
        return self.client.post(url, data, format='json', HTTP_ACCEPT='application/json')

    def post_tool_checked(self, data):
        """
        Description: Checked POST request for given data.
        Returns:    The response for the POST request.
        Throws:     RuntimeError if the tool could not be created.
        """
        response = self.post_tool(self.base_url, data)
        if response.status_code != status.HTTP_201_CREATED:
            raise RuntimeError(
                f"Post did not succeed: attempt to post tool to {self.base_url} returned {response.status_code}.")
        return response

    def get_tool(self, url, id, query_kvp_dict=None):
        get_url = f"{url}{id}"
        response_format = 'json'

        if query_kvp_dict:
            query_params = "&".join(f"{k}={v}" for k, v in query_kvp_dict.items())
            get_url += f"?{query_params}"
            if 'format' in query_kvp_dict and query_kvp_dict['format'].strip():
                response_format = query_kvp_dict['format']

        return self.client.get(get_url, HTTP_ACCEPT=f'application/{response_format}')

    def get_all_tools(self, url, filter_kvp_dict=None):
        response_format = 'json'  # json is default

        if filter_kvp_dict:
            query_params = "&".join(f"{k}={v}" for k, v in filter_kvp_dict.items())
            url += f"?{query_params}"
            if 'format' in filter_kvp_dict and filter_kvp_dict['format'].strip():
                response_format = filter_kvp_dict['format']
        try:
            return self.client.get(url, HTTP_ACCEPT=f"application/{response_format}")
        except ESExceptions.NotFoundError as e:
            raise e

    def put_tool(self, url, updated_data):
        return self.client.put(f"{url}{updated_data['biotoolsID']}", updated_data,
                               format='json', HTTP_ACCEPT='application/json')

    def remove_tool(self, url, id):
        return self.client.delete(f"{url}{id}", format='json',
                                  HTTP_AUTHORIZATION=f"Token {self.tokens[self.user.username]}")

    def remove_all_tools(self, id_list):
        for id in id_list:
            self.remove_tool(self.base_url, id)

    def validate_tool_post(self, url, data):
        return self.client.post(f"{url}{self.validation_url_extension}", data, format='json')

    def validate_tool_put(self, id, data):
        return self.client.put(f"/{id}/{self.validation_url_extension}", data,
                               format='json', HTTP_ACCEPT='application/json')

    def ensure_tools(self, url):
        """
        Description: Post tool to ensure there is at least one tool on the server.
        Info: Post is executed in a loop including a 1ms sleep before querying due to race condition issues.
        """
        import time
        number_tools = self.get_all_tools(url).json()['count']

        while number_tools == 0:
            self._try_post(url)
            time.sleep(1)
            number_tools = self.get_all_tools(url).json()['count']

    def _try_post(self, url):
        data = TH.get_input_tool()
        self.post_tool_checked(data)

    def _mail_to_str(self):
        # Helper for debugging
        return [f"`{message.to[0]}`: `{message.subject}`" for message in mail.outbox]

    # USER MANAGEMENT --------------------------------------------------------------------------------------------------

    def create_user(self, registration_data, isSuperuser):
        if isSuperuser:
            return User.objects.create_superuser(registration_data['username'],
                                                 password=registration_data['password1'],
                                                 email=registration_data['email']
                                                 )
        else:
            return User.objects.create_user(registration_data['username'],
                                            password=registration_data['password1'],
                                            email=registration_data['email']
                                            )

    def switch_user(self, registration_data, isSuperuser=False):
        username = registration_data['username']
        password = registration_data['password1']

        if username not in [u.username for u in User.objects.all()]:
            assert isSuperuser is not None
            user = self.create_user(registration_data, isSuperuser)
            self.tokens[username] = (Token.objects.create(user=user)).key

        self.login_user(username, password)

        return self.tokens[registration_data['username']]

    def login_user(self, username, password):
        login_success = self.client.login(username=username, password=password)
        self.user = User.objects.get(username=username)

        if not login_success:
            raise Exception(f"Login failed for user {username}")

        user_token = self.tokens[self.user.username]
        if user_token:
            self.client.credentials(HTTP_AUTHORIZATION=f"Token {user_token}")
        else:
            raise Exception(f"Token not found for user {self.user.username}")

    # SETUP ------------------------------------------------------------------------------------------------------------
    @classmethod
    def setUpTestData(cls):
        # Ran once to set up non-modified data
        # This should be run once globally not once per BaseTestObject, but it does double the speed of tests
        es = BaseTestObject._initialize_ES()
        es.indices.create(settings.ELASTIC_SEARCH_INDEX)
        mapping = BaseTestObject.read_schema()
        es.indices.put_mapping(index=settings.ELASTIC_SEARCH_INDEX, body=mapping)

    def setUp(self):
        self.tokens = {}
        self.client = APIClient()
        self.client.credentials()
        self.switch_user(superuser_registration_data, True)
        self.assert_mail_empty() # Make sure mail queue is empty before every test

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cmd = Command()
        cmd.handle()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    @staticmethod
    def read_schema():
        import json
        with open("elixirapp/tests/Mapping.json", 'r') as schema_file:
            return json.load(schema_file)

    def tearDown(self):
        self.assert_mail_empty()  # Make sure mail queue is empty after every test.
        # This also means every test needs to empty its mail queue
        BaseTestObject._reset_ES()

    @staticmethod
    def _initialize_ES():
        settings.ELASTIC_SEARCH_INDEX = 'test'
        es = Elasticsearch(settings.ELASTIC_SEARCH_URLS)
        try:
            es.indices.delete(index=settings.ELASTIC_SEARCH_INDEX)
        except ESExceptions.TransportError as TE:
            if not TE.status_code == 404:
                raise TE
        return es

    @staticmethod
    def _reset_ES():
        es = Elasticsearch(settings.ELASTIC_SEARCH_URLS)
        try:
            es.indices.delete(index='test')
        except ESExceptions.TransportError as TE:
            if not TE.status_code == 404:
                raise TE
        settings.ELASTIC_SEARCH_INDEX = 'elixir'
        return es
