from rest_framework import status
from elixir.serializers import *
from backend.elixirapp.tests.test_baseobject import BaseTestObject
from elixir.test_datastructure_json import inputTool, inputToolInvalid


class TestAuthorization(BaseTestObject):

    def check_user_exists(self):
        resp = self.client.get(self.user_list_url)
        return self.valid_user_registration_data['username'] in resp.content.decode('utf-8')

    def checked_registration(self):
        response = self.client.post(self.registration_url, self.valid_user_registration_data, format='json')
        if response.status_code != status.HTTP_201_CREATED:
            raise RuntimeError(
                f"Post did not succeed: attempt to post to {self.registration_url} returned {response.status_code}.")
        return response.json()['key']  # return token

    def register_user(self, data):
        self.client.post(self.registration_url, data, format='json')

    def login_user(self, data):
        return self.client.post(self.login_url, data, format='json')

    def logout_user(self, token):
        return self.client.post(self.logout_url, HTTP_AUTHORIZATION=f"Token {token}")

    def get_user_info(self, token):
        return self.client.get(self.user_info_url, HTTP_ACCEPT='application/json')

    def test_user_authorization_valid(self):
        self.register_user(self.valid_user_registration_data)
        self.assertTrue(self.check_user_exists())

    def test_user_authorization_invalid_p2(self):
        self.register_user(self.user_registration_data_invalid_p2)
        self.assertFalse(self.check_user_exists())

    def test_user_authorization_no_email(self):
        self.register_user(self.user_registration_data_missing_email)
        self.assertFalse(self.check_user_exists())

    def test_user_authorization_no_username(self):
        self.register_user(self.user_registration_data_missing_username)
        self.assertFalse(self.check_user_exists())

    def test_user_authorization_no_p1(self):
        self.register_user(self.user_registration_data_missing_p1)
        self.assertFalse(self.check_user_exists())

    def test_user_authorization_no_p2(self):
        self.register_user(self.user_registration_data_missing_p2)
        self.assertFalse(self.check_user_exists())

    def test_user_login_valid(self):
        self.checked_registration()
        response = self.login_user(self.valid_user_login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_login_invalid_password(self):
        self.checked_registration()
        response = self.login_user(self.invalid_user_login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # todo others

    def test_user_logout_valid(self):
        self.checked_registration()
        response = self.login_user(self.valid_user_login_data)
        token = response.data['key']

        response = self.logout_user(token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_logout_invalid_token(self):  # NOTE: the token is not validated
        self.checked_registration()
        response = self.login_user(self.valid_user_login_data)

        token = response.data['key']
        incorrect_token = 'incorrect_token'
        assert (incorrect_token != token)

        response = self.logout_user(incorrect_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_logout_empty_token(self):  # NOTE: token is not being validated
        self.checked_registration()
        self.login_user(self.valid_user_login_data)

        response = self.logout_user("")
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # TODO

    def test_get_superuser_info_no_resources(self):
        token = self.login_user(self.superuser_login_data).data['key']
        user_info = self.get_user_info(token).json()

        self.assertEqual(user_info['username'], self.superuser_registration_data['username'])
        self.assertEqual(user_info['email'], self.superuser_registration_data['email'])
        self.assertTrue(user_info['is_superuser'])
        self.assertEqual(len(user_info['resources']), 0)

    def test_get_superuser_info_with_resources(self):
        token = self.login_user(self.superuser_login_data).data['key']
        self.post_tool_checked(inputTool())

        user_info = self.get_user_info(token).json()

        self.assertEqual(user_info['username'], self.superuser_registration_data['username'])
        self.assertEqual(user_info['email'], self.superuser_registration_data['email'])
        self.assertTrue(user_info['is_superuser'])
        self.assertEqual(len(user_info['resources']), 1)

    def test_get_user_info_no_resources(self):
        token_key = self.switch_user(self.valid_user_registration_data, self.valid_user_login_data)
        user_info = self.get_user_info(token_key).json()

        self.assertEqual(user_info['username'], self.valid_user_registration_data['username'])
        self.assertEqual(user_info['email'], self.valid_user_registration_data['email'])
        self.assertFalse(user_info['is_superuser'])
        self.assertEqual(len(user_info['resources']), 0)

    def test_get_user_info_with_resources(self):
        token_key = self.switch_user(self.superuser_registration_data, True)
        self.post_tool_checked(inputTool())

        user_info = self.get_user_info(token_key).json()

        self.assertEqual(user_info['username'], self.valid_user_registration_data['username'])
        self.assertEqual(user_info['email'], self.valid_user_registration_data['email'])
        self.assertFalse(user_info['is_superuser'])
        self.assertEqual(len(user_info['resources']), 1)

    # todo test tool access (editing permissions)
