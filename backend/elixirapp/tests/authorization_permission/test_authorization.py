from rest_framework import status
from elixir.serializers import *
from backend.elixirapp.tests.test_baseobject import BaseTestObject
from elixir.tool_helper import ToolHelper as TH
import re
from backend.elixirapp.tests.login_data import valid_user_registration_data, user_registration_data_invalid_p2, \
    user_registration_data_missing_email, user_registration_data_missing_username, user_registration_data_missing_p1, \
    user_registration_data_missing_p2, valid_user_login_data, invalid_user_login_data, \
    other_valid_user_1_registration_data, other_valid_user_1_login_data, other_valid_user_2_registration_data, \
    other_valid_user_2_login_data, superuser_registration_data, superuser_login_data, valid_change_password_change_data, \
    valid_user_registration_data_post_change


class TestAuthorization(BaseTestObject):

    # HELPERS ----------------------------------------------------------------------------------------------------------
    def check_user_exists(self):
        """
        Description: Checks that the user is registered.
        Info: Gets all users and check if the user is part of the list.
        Returns: Boolean value indicating whether the user is registered.
        """
        get_users = self.client.get(self.user_list_url, HTTP_ACCEPT='application/json')
        current_user_name = valid_user_registration_data['username']
        return any(user['username'] == current_user_name for user in get_users.json())

    def checked_registration(self):
        """
        Description: Safe registration with valid data (if not explicitly modified before).
        Info: Uses the valid registration data defined in the BaseObject to ensure successful validation.
        Returns: Token for the current user.
        Throws: RuntimeError if the user could not be successfully registered.
        """
        response = self.client.post(self.registration_url, valid_user_registration_data, format='json')
        if response.status_code != status.HTTP_201_CREATED:
            raise RuntimeError(
                f"Post did not succeed: attempt to post to {self.registration_url} returned {response.status_code}.")
        self.pop_email(valid_user_registration_data['email'], "[example.com] Please Confirm Your E-mail Address")
        return response.json()['key']  # return token

    def register_user(self, data):
        """
        Description: Registers a user with given data.
        """
        self.client.post(self.registration_url, data, format='json')

    def checked_login(self, data):
        """
        Description: Logs in a user with given data.
        Returns: Login token
        """
        return self.client.post(self.login_url, data, format='json', HTTP_ACCEPT='application/json')

    def logout_user(self, token):
        """
        Description: Logs out a user with given data.
        """
        return self.client.post(self.logout_url, HTTP_AUTHORIZATION=f"Token {token}")

    def get_user_info(self, token):
        """
        Description: Queries user information.
        """
        return self.client.get(self.user_info_url, HTTP_AUTHORIZATION=f'Token {token}', HTTP_ACCEPT='application/json')

    def change_password_user(self, token, data):
        """
        Description: Queries user information.
        """
        return self.client.post(self.change_password_url, data, format='json', HTTP_AUTHORIZATION=f'Token {token}')

    # TESTS ------------------------------------------------------------------------------------------------------------

    def test_user_authorization_valid(self):
        """
        Description: Test user registration with valid data (if not explicitly modified before).
        Info: Registers user and asserts the registration was successful.
        Expected: New user was successfully registered.
        """
        self.register_user(valid_user_registration_data)
        self.assertTrue(self.check_user_exists())
        self.pop_email(valid_user_registration_data['email'], "[example.com] Please Confirm Your E-mail Address")

    def test_user_authorization_invalid_p2(self):
        """
        Description: Test user registration with invalid registration data.
        Info: Registers user with invalid data. Passwords don't match.
        Expected: New user was not registered.
        """
        self.register_user(user_registration_data_invalid_p2)
        self.assertFalse(self.check_user_exists())

    def test_user_authorization_no_email(self):
        """
        Description: Test user registration with invalid registration data.
        Info: Registers user with invalid data. Email not given.
        Expected: New user was not registered.
        """
        self.register_user(user_registration_data_missing_email)
        self.assertFalse(self.check_user_exists())

    def test_user_authorization_no_username(self):
        """
        Description: Test user registration with invalid registration data.
        Info: Registers user with invalid data. Username not given.
        Expected: New user was not registered.
        """
        self.register_user(user_registration_data_missing_username)
        self.assertFalse(self.check_user_exists())

    def test_user_authorization_no_p1(self):
        """
        Description: Test user registration with invalid registration data.
        Info: Registers user with invalid data. Password1 not given.
        Expected: New user was not registered.
        """
        self.register_user(user_registration_data_missing_p1)
        self.assertFalse(self.check_user_exists())

    def test_user_authorization_no_p2(self):
        """
        Description: Test user registration with invalid registration data.
        Info: Registers user with invalid data. Password2 not given.
        Expected: New user was not registered.
        """
        self.register_user(user_registration_data_missing_p2)
        self.assertFalse(self.check_user_exists())

    def test_user_login_valid(self):
        """
        Description: Test user login with valid login data.
        Info: Registers and logs in user with valid login data.
        Expected: Login succeeds.
        """
        self.checked_registration()
        response = self.checked_login(valid_user_login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_login_invalid_password(self):
        """
        Description: Test user login with invalid login data.
        Info: Registers user with valid data, then tries to log in user with invalid login data. Password incorrect.
        Expected: Login fails.
        """
        self.checked_registration()
        response = self.checked_login(invalid_user_login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # TODO Fix
    # def test_user_change_password_valid(self):
    #     token = self.checked_registration()
    #     self.checked_login(valid_user_login_data)
    #
    #
    #     print(token, valid_change_password_change_data, self.change_password_url)
    #     response = self.change_password_user(token, valid_change_password_change_data)
    #     print(response.__dict__)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    #     response = self.logout_user(token)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    #     response = self.checked_login(valid_user_registration_data_post_change)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset(self):
        user_token = self.checked_registration()

        response = self.client.post(self.password_reset_url, {
            'email': valid_user_registration_data['email'],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        mail = self.pop_email("test@user.com", "Password reset on example.com")

        match = re.search("uid=([^&]+)&token=(\w+-\w+)", str(mail.message()))
        uid = match.group(1).strip()
        token = match.group(2).strip()

        print(uid, token)
        response = self.client.post(self.password_reset_confirm_url, {
            'uid': uid,
            'token': token,
            'new_password1': "NewSecurePassword",
            'new_password2': "NewSecurePassword",
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.logout_user(user_token)
        self.client.credentials() # Otherwise there is a dangling auth token in checked login request

        response = self.checked_login({
            "username": valid_user_registration_data['username'],
            "password": "NewSecurePassword",
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # todo others
    # todo find out what i meant to say with 'others'

    def test_user_logout_valid(self):
        """
        Description: Test user logout with valid logout data.
        Info: Registers and logs in user with valid data, then tries to log out user with valid logout data.
        Expected: Logout succeeds.
        """
        self.checked_registration()
        response = self.checked_login(valid_user_login_data)
        token = response.data['key']

        response = self.logout_user(token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_logout_invalid_token(self):  # NOTE: the token is not validated
        """
        Description: Test user logout with incorrect token.
        Info: Registers and logs in user with valid data, then tries to log out user with incorrect token.
        Expected: Logout does not fail as the token is not validated.
        """
        self.checked_registration()
        response = self.checked_login(valid_user_login_data)

        token = response.data['key']
        incorrect_token = 'incorrect_token'
        assert (incorrect_token != token)

        response = self.logout_user(incorrect_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_logout_empty_token(self):  # NOTE: token is not being validated
        """
        Description: Test user logout with empty token.
        Info: Registers and logs in user with valid data, then tries to log out user with empty token.
        Expected: Logout does not fail as the token is not validated.
        """
        self.checked_registration()
        self.checked_login(valid_user_login_data)

        response = self.logout_user("")
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # TODO check why not validated

    def test_get_superuser_info_no_resources(self):
        """
        Description: Test retrieval of superuser info for user who has not posted resources.
        Info: Logs in user with valid data, then queries the superuser information.
              The user has not posted tools before.
        Expected: Retrieved info aligns with current user state in terms of username, email and amount of resources (0).
        """
        token = self.checked_login(superuser_login_data).data['key']
        user_info = self.get_user_info(token).json()

        self.assertEqual(user_info['username'], superuser_registration_data['username'])
        self.assertEqual(user_info['email'], superuser_registration_data['email'])
        self.assertTrue(user_info['is_superuser'])
        self.assertEqual(len(user_info['resources']), 0)

    def test_get_superuser_info_with_resources(self):
        """
        Description: Test retrieval of superuser info for user who has posted a resource.
        Info: Logs in user with valid data, then queries the superuser information.
              The user has posted a tool before.
        Expected: Retrieved info aligns with current user state in terms of username, email and amount of resources (1).
        """
        token = self.checked_login(superuser_login_data).data['key']
        self.post_tool_checked(TH.get_input_tool())

        user_info = self.get_user_info(token).json()  # post tool

        self.assertEqual(user_info['username'], superuser_registration_data['username'])
        self.assertEqual(user_info['email'], superuser_registration_data['email'])
        self.assertTrue(user_info['is_superuser'])
        self.assertEqual(len(user_info['resources']), 1)

    def test_get_user_info_no_resources(self):
        """
        Description: Test retrieval of user info for user who has not posted resources.
        Info: Logs in user with valid data, then queries the user information.
              The user has not posted tools before.
        Expected: Retrieved info aligns with current user state in terms of username, email and amount of resources (0).
        """
        token_key = self.switch_user(valid_user_registration_data, False)
        user_info = self.get_user_info(token_key).json()

        self.assertEqual(user_info['username'], valid_user_registration_data['username'])
        self.assertEqual(user_info['email'], valid_user_registration_data['email'])
        self.assertFalse(user_info['is_superuser'])
        self.assertEqual(len(user_info['resources']), 0)

    def test_get_user_info_with_resources(self):
        """
        Description: Test retrieval of user info for user who has posted a resource.
        Info: Logs in user with valid data, then queries the user information.
              The user has posted a tool before.
        Expected: Retrieved info aligns with current user state in terms of username, email and amount of resources (1).
        """
        token_key = self.switch_user(valid_user_registration_data, False)
        self.post_tool_checked(TH.get_input_tool())  # post tool

        user_info = self.get_user_info(token_key).json()

        self.assertEqual(user_info['username'], valid_user_registration_data['username'])
        self.assertEqual(user_info['email'], valid_user_registration_data['email'])
        self.assertFalse(user_info['is_superuser'])
        self.assertEqual(len(user_info['resources']), 1)
