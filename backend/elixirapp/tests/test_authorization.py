from rest_framework import status
from elixir.serializers import *
from backend.elixirapp.tests.test_baseobject import BaseTestObject
from rest_framework.test import APIRequestFactory, APIClient, APITestCase
from rest_framework.authtoken.models import Token
from elixir.views import Ontology, User

class TestAuthorization(BaseTestObject):
    auth_url = '/rest-auth/'
    registration_url = f"{auth_url}registration/"
    login_url = f"{auth_url}login/"
    logout_url = f"{auth_url}logout/"
    user_list_url = '/user-list/'

    valid_registration_data = {
        "username": "test_user",
        "password1": "test_user_password",
        "password2": "test_user_password",
        "email": "test@user.com"
    }
    registration_data_invalid_p2 = {
        "username": "test_user",
        "password1": "test_user_password",
        "password2": "not_test_user_password",
        "email": "test@user.com"
    }
    registration_data_missing_email = {
        "username": "test_user",
        "password1": "test_user_password",
        "password2": "test_user_password"
    }
    registration_data_missing_username = {
        "password1": "test_user_password",
        "password2": "test_user_password",
        "email": "test@user.com"
    }
    registration_data_missing_p1 = {
        "username": "test_user",
        "password2": "test_user_password",
        "email": "test@user.com"
    }
    registration_data_missing_p2 = {
        "username": "test_user",
        "password1": "test_user_password",
        "email": "test@user.com"
    }

    valid_login_data = {
        "username": valid_registration_data['username'],
        "password": valid_registration_data['password1']
    }
    invalid_login_data = {
        "username": valid_registration_data['username'],
        "password": 'incorrectPassword'
    }
    
    def check_user_exists(self):
        resp = self.client.get(self.user_list_url)
        return self.valid_registration_data['username'] in resp.content.decode('utf-8')

    def checked_registration(self):
        response = self.client.post(self.registration_url, self.valid_registration_data, format='json')
        if response.status_code != status.HTTP_201_CREATED:
            raise RuntimeError(f"Post did not succeed: attempt to post to {self.registration_url} returned {response.status_code}.")

    def register_user(self, data):
        self.client.post(self.registration_url, data, format='json')

    def login_user(self, data):
        return self.client.post(self.login_url, data, format='json')

    def logout_user(self, token):
        return self.client.post(self.logout_url, HTTP_AUTHORIZATION=f"Token {token}")

    def test_user_authorization_valid(self):
        self.register_user(self.valid_registration_data)
        self.assertTrue(self.check_user_exists())

    def test_user_authorization_invalid_p2(self):
        self.register_user(self.registration_data_invalid_p2)
        self.assertFalse(self.check_user_exists())

    def test_user_authorization_no_email(self):
        self.register_user(self.registration_data_missing_email)
        self.assertFalse(self.check_user_exists())

    def test_user_authorization_no_username(self):
        self.register_user(self.registration_data_missing_username)
        self.assertFalse(self.check_user_exists())

    def test_user_authorization_no_p1(self):
        self.register_user(self.registration_data_missing_p1)
        self.assertFalse(self.check_user_exists())

    def test_user_authorization_no_p2(self):
        self.register_user(self.registration_data_missing_p2)
        self.assertFalse(self.check_user_exists())

    def test_user_login_valid(self):
        self.checked_registration()
        response = self.login_user(self.valid_login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_login_invalid_password(self):
        self.checked_registration()
        response = self.login_user(self.invalid_login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # todo others

    def test_user_logout_valid(self):
        self.checked_registration()
        response = self.login_user(self.valid_login_data)
        token = response.data['key']

        response = self.logout_user(token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_logout_invalid_token(self): # NOTE: the token is not validated
        self.checked_registration()
        response = self.login_user(self.valid_login_data)

        token = response.data['key']
        incorrect_token = 'incorrect_token'
        assert(incorrect_token != token)

        response = self.logout_user(incorrect_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_logout_empty_token(self):  # NOTE: the token is not validated
        self.checked_registration()
        self.login_user(self.valid_login_data)

        response = self.logout_user("")
        self.assertEqual(response.status_code, status.HTTP_200_OK) # TODO

    # def test_get_user_info(self):

    # todo get user information
    # todo get tool access (editing permissions)



