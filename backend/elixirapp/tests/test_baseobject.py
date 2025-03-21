from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from elixir.views import Ontology, User


class BaseTestObject(APITestCase):

    # TOKENS -----------------------------------------------------------------------------------------------------------
    tokens = {}

    # SETUP DATA -------------------------------------------------------------------------------------------------------
    superuser_registration_data = {
        "username": "test_superuser",
        "password1": "test_superuser_password",
        "password2": "test_superuser_password",
        "email": "test@superuser.com"
    }
    superuser_login_data = {
        "username": superuser_registration_data['username'],
        "password": superuser_registration_data['password1']
    }

    # DATA -------------------------------------------------------------------------------------------------------------
    valid_user_registration_data = {
        "username": "test_user",
        "password1": "test_user_password",
        "password2": "test_user_password",
        "email": "test@user.com"
    }
    user_registration_data_invalid_p2 = {
        "username": "test_user",
        "password1": "test_user_password",
        "password2": "not_test_user_password",
        "email": "test@user.com"
    }
    user_registration_data_missing_email = {
        "username": "test_user",
        "password1": "test_user_password",
        "password2": "test_user_password"
    }
    user_registration_data_missing_username = {
        "password1": "test_user_password",
        "password2": "test_user_password",
        "email": "test@user.com"
    }
    user_registration_data_missing_p1 = {
        "username": "test_user",
        "password2": "test_user_password",
        "email": "test@user.com"
    }
    user_registration_data_missing_p2 = {
        "username": "test_user",
        "password1": "test_user_password",
        "email": "test@user.com"
    }
    valid_user_login_data = {
        "username": valid_user_registration_data['username'],
        "password": valid_user_registration_data['password1']
    }
    invalid_user_login_data = {
        "username": valid_user_registration_data['username'],
        "password": 'incorrectPassword'
    }
    other_valid_user_1_registration_data = {
        "username": "other_test_user_1",
        "password1": "other_test_user_1_password",
        "password2": "other_test_user_1_password",
        "email": "other.test@user1.com"
    }
    other_valid_user_1_login_data = {
        "username": other_valid_user_1_registration_data['username'],
        "password": other_valid_user_1_registration_data['password1']
    }
    other_valid_user_2_registration_data = {
        "username": "other_test_user_2",
        "password1": "other_test_user_2_password",
        "password2": "other_test_user_2_password",
        "email": "other.test@user2.com"
    }
    other_valid_user_2_login_data = {
        "username": other_valid_user_2_registration_data['username'],
        "password": other_valid_user_2_registration_data['password1']
    }


    # URLS -------------------------------------------------------------------------------------------------------------
    base_url = '/tool/'
    base_urls = ['/tool/']  # TODO should also work with '/t/' and ''
    validation_url_extension = 'validate/'
    user_list_url = '/user-list/'
    auth_url = '/rest-auth/'
    registration_url = f"{auth_url}registration/"
    login_url = f"{auth_url}login/"
    logout_url = f"{auth_url}logout/"
    user_info_url = f"{auth_url}user/"

    # BASE METHODS -----------------------------------------------------------------------------------------------------
    def post_tool(self, url, data):
        return self.client.post(url, data, format='json')

    def post_tool_checked(self, data):
        response = self.post_tool(self.base_url, data)
        if response.status_code != status.HTTP_201_CREATED:
            raise RuntimeError(
                f"Post did not succeed: attempt to post to {self.base_url} returned {response.status_code}.")
        return response

    def get_tool(self, url, id):
        return self.client.get(f"{url}{id}", format='json', HTTP_ACCEPT='application/json')

    def put_tool(self, url, updated_data):
        return self.client.put(f"{url}{updated_data['biotoolsID']}", updated_data,
                               format='json', HTTP_ACCEPT='application/json')

    def remove_tool(self, url, id):
        print(f"blub user {self.user.username}, is superuser: {self.user.is_superuser},is trying to delete.")
        return self.client.delete(f"{url}{id}", format='json',
                           HTTP_AUTHORIZATION=f"Token {self.tokens[self.user.username]}")

    def validate_tool_post(self, url, data):
        return self.client.post(f"{url}{self.validation_url_extension}", data, format='json')

    def validate_tool_put(self, id, data):
        return self.client.put(f"/{id}/{self.validation_url_extension}", data,
                               format='json', HTTP_ACCEPT='application/json')

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

    def switch_user(self, registration_data, login_data, isSuperuser=False):
        if registration_data['username'] not in [u.username for u in User.objects.all()]:
            assert isSuperuser is not None
            user = self.create_user(registration_data, isSuperuser)
            self.tokens[registration_data['username']] = (Token.objects.create(user=user)).key

        login_success = self.client.login(username=login_data['username'], password=login_data['password'])
        self.user = User.objects.get(username=login_data['username'])

        if not login_success:
            raise Exception(f"Login failed for user {login_data['username']}")

        user_token = self.tokens[self.user.username]
        if user_token:
            self.client.credentials(HTTP_AUTHORIZATION=f"Token {user_token}")
        else: raise Exception(f"Token not found for user {self.user.username}")

        return self.tokens[registration_data['username']]

    # SETUP ------------------------------------------------------------------------------------------------------------
    def setUp(self):
        self.client = APIClient()
        self.switch_user(self.superuser_registration_data, self.superuser_login_data, True)
