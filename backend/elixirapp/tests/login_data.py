superuser_registration_data = {
    "username": "test_superuser",
    "password1": "test_superuser_password",
    "password2": "test_superuser_password",
    "email": "test@superuser.com",
}
superuser_login_data = {
    "username": superuser_registration_data["username"],
    "password": superuser_registration_data["password1"],
}
valid_user_registration_data = {
    "username": "test_user",
    "password1": "test_user_password",
    "password2": "test_user_password",
    "email": "test@user.com",
}
user_registration_data_invalid_p2 = {
    "username": "test_user",
    "password1": "test_user_password",
    "password2": "not_test_user_password",
    "email": "test@user.com",
}
user_registration_data_missing_email = {
    "username": "test_user",
    "password1": "test_user_password",
    "password2": "test_user_password",
}
user_registration_data_missing_username = {
    "password1": "test_user_password",
    "password2": "test_user_password",
    "email": "test@user.com",
}
user_registration_data_missing_p1 = {
    "username": "test_user",
    "password2": "test_user_password",
    "email": "test@user.com",
}
user_registration_data_missing_p2 = {
    "username": "test_user",
    "password1": "test_user_password",
    "email": "test@user.com",
}
valid_user_login_data = {
    "username": valid_user_registration_data["username"],
    "password": valid_user_registration_data["password1"],
}
invalid_user_login_data = {
    "username": valid_user_registration_data["username"],
    "password": "incorrectPassword",
}
other_valid_user_1_registration_data = {
    "username": "other_test_user_1",
    "password1": "other_test_user_1_password",
    "password2": "other_test_user_1_password",
    "email": "other.test@user1.com",
}
other_valid_user_1_login_data = {
    "username": other_valid_user_1_registration_data["username"],
    "password": other_valid_user_1_registration_data["password1"],
}
other_valid_user_2_registration_data = {
    "username": "other_test_user_2",
    "password1": "other_test_user_2_password",
    "password2": "other_test_user_2_password",
    "email": "other.test@user2.com",
}
other_valid_user_2_login_data = {
    "username": other_valid_user_2_registration_data["username"],
    "password": other_valid_user_2_registration_data["password1"],
}
valid_change_password_change_data = {
    "old_password": valid_user_registration_data["password1"],
    "new_password1": "test_user_password2",
    "new_password2": "test_user_password2",
}
valid_user_registration_data_post_change = {
    "username": valid_user_registration_data["username"],
    "password": valid_change_password_change_data["new_password1"],
}
