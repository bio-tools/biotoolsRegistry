from datetime import timedelta
from unittest.mock import patch

from allauth.account.forms import default_token_generator
from allauth.account.models import EmailAddress
from allauth.account.utils import user_pk_to_url_str
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core import mail
from django.test import Client, TestCase, override_settings
from django.urls import get_script_prefix, resolve, set_script_prefix
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from elixirapp.test_html import HTML_REQUEST


PASSWORD = 'Browser-test-only-2026'


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'],
                   EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class BrowserAuthenticationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('browser-user', 'browser@example.org', PASSWORD)
        EmailAddress.objects.create(user=cls.user, email=cls.user.email, verified=True, primary=True)

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)

    def csrf(self):
        return self.client.cookies[settings.CSRF_COOKIE_NAME].value

    def login(self, **extra):
        self.client.get('/auth/login/', **HTML_REQUEST)
        return self.client.post('/auth/login/', {'username': self.user.username, 'password': PASSWORD,
                                'csrfmiddlewaretoken': self.csrf(), **extra}, **HTML_REQUEST)

    @override_settings(SESSION_COOKIE_SECURE=True, CSRF_COOKIE_SECURE=True)
    def test_secure_cookie_settings_are_applied_on_login(self):
        response = self.login()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.cookies[settings.SESSION_COOKIE_NAME]['secure'])
        self.assertTrue(response.cookies[settings.CSRF_COOKIE_NAME]['secure'])

    def test_login_invalid_valid_email_and_cookie_rotation(self):
        self.client.get('/auth/login/', **HTML_REQUEST)
        before = self.csrf()
        invalid = self.client.post('/auth/login/', {'username': self.user.username, 'password': 'wrong',
                                   'csrfmiddlewaretoken': before}, **HTML_REQUEST)
        self.assertContains(invalid, 'Unable to sign in')
        self.assertNotContains(invalid, 'value="wrong"')
        response = self.login(username=self.user.email)
        self.assertRedirects(response, '/account/', fetch_redirect_response=False)
        self.assertNotEqual(self.csrf(), before)
        self.assertTrue(response.cookies[settings.SESSION_COOKIE_NAME]['httponly'])
        self.assertEqual(response.cookies[settings.SESSION_COOKIE_NAME]['samesite'], 'Lax')
        self.assertFalse(Token.objects.filter(user=self.user).exists())
        page = self.client.get('/account/', **HTML_REQUEST)
        self.assertContains(page, self.user.email)
        self.assertIn('no-store', page['Cache-Control'])

    def test_login_requires_csrf_and_inactive_or_unverified_accounts_are_rejected(self):
        self.client.get('/auth/login/', **HTML_REQUEST)
        data = {'username': self.user.username, 'password': PASSWORD}
        self.assertEqual(self.client.post('/auth/login/', data, **HTML_REQUEST).status_code, 403)
        self.user.is_active = False
        self.user.save()
        self.assertContains(self.login(), 'Unable to sign in')
        self.user.is_active = True
        self.user.save()
        EmailAddress.objects.filter(user=self.user).update(verified=False)
        with override_settings(ACCOUNT_EMAIL_VERIFICATION='mandatory'):
            self.assertContains(self.login(), 'Unable to sign in')

    def test_next_redirect_is_same_origin_and_preserves_mount(self):
        for target in ('https://evil.invalid/', '//evil.invalid/', '/\\evil.invalid/', 'javascript:alert(1)'):
            with self.subTest(target=target):
                response = self.login(next=target)
                self.assertEqual(response['Location'], '/account/')
        self.assertEqual(self.login(next='/search/?q=retained')['Location'], '/search/?q=retained')
        self.addCleanup(set_script_prefix, get_script_prefix())
        set_script_prefix('/_migration/html')
        client = Client(enforce_csrf_checks=True)
        response = client.get('/account/', SCRIPT_NAME='/_migration/html', **HTML_REQUEST)
        self.assertEqual(response['Location'], '/_migration/html/auth/login/?next=%2F_migration%2Fhtml%2Faccount%2F')

    def test_unauthorized_page_fragment_json_and_spoofed_api_token(self):
        token = Token.objects.create(user=self.user)
        self.assertEqual(self.client.get('/account/', **HTML_REQUEST).status_code, 302)
        fragment = self.client.get('/account/', HTTP_HX_REQUEST='true', **HTML_REQUEST)
        self.assertEqual(fragment.status_code, 401)
        self.assertEqual(fragment.content, b'')
        self.assertIn('/auth/login/', fragment['X-Login-URL'])
        self.assertNotIn('HX-Redirect', fragment)
        json = self.client.get('/auth/session/', HTTP_ACCEPT='application/json',
                               HTTP_AUTHORIZATION=f'Token {token.key}', **HTML_REQUEST)
        self.assertEqual(json.status_code, 401)
        self.assertEqual(json.json()['error']['code'], 'authentication_required')
        self.assertNotContains(json, self.user.email, status_code=401)

    def test_native_htmx_vue_mutations_enforce_csrf_and_origin(self):
        self.login()
        for style in ({}, {'HTTP_HX_REQUEST': 'true'}, {'HTTP_ACCEPT': 'application/json'}):
            for token in (None, 'invalid'):
                headers = {'HTTP_X_CSRFTOKEN': token} if token else {}
                response = self.client.post('/auth/check/', **headers, **style, **HTML_REQUEST)
                self.assertEqual(response.status_code, 403)
                self.assertNotIn('browser_last_verified', self.client.session)
                if style.get('HTTP_ACCEPT'):
                    self.assertEqual(response.json(), {'error': {'code': 'csrf_failed'}})
            with override_settings(CSRF_TRUSTED_ORIGINS=[]):
                response = self.client.post('/auth/check/', HTTP_X_CSRFTOKEN=self.csrf(),
                    HTTP_ORIGIN='https://evil.invalid', **style, **HTML_REQUEST)
                self.assertEqual(response.status_code, 403)
        for style, expected in (({}, 302), ({'HTTP_HX_REQUEST': 'true'}, 302), ({'HTTP_ACCEPT': 'application/json'}, 200)):
            response = self.client.post('/auth/check/', HTTP_X_CSRFTOKEN=self.csrf(), **style, **HTML_REQUEST)
            self.assertEqual(response.status_code, expected)
            self.assertIn('browser_last_verified', self.client.session)

    def test_expired_session_is_recoverable_even_with_a_missing_csrf_cookie(self):
        self.login()
        Session.objects.filter(session_key=self.client.session.session_key).update(expire_date=timezone.now() - timedelta(seconds=1))
        for csrf in (self.csrf(), ''):
            for style in ({'HTTP_HX_REQUEST': 'true'}, {'HTTP_ACCEPT': 'application/json'}):
                response = self.client.post('/auth/check/', HTTP_X_CSRFTOKEN=csrf, **style, **HTML_REQUEST)
                self.assertEqual(response.status_code, 401)
                self.assertNotIn('browser_last_verified', self.client.session)
                self.assertNotContains(response, '<!doctype html>', status_code=401)

    def test_logout_is_post_csrf_only_and_does_not_revoke_external_api_tokens(self):
        token = Token.objects.create(user=self.user)
        self.login()
        self.assertEqual(self.client.get('/auth/logout/', **HTML_REQUEST).status_code, 405)
        self.assertEqual(self.client.post('/auth/logout/', **HTML_REQUEST).status_code, 403)
        response = self.client.post('/auth/logout/', HTTP_X_CSRFTOKEN=self.csrf(), HTTP_HX_REQUEST='true', **HTML_REQUEST)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['HX-Redirect'], '/auth/login/')
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertTrue(Token.objects.filter(key=token.key).exists())

    def test_reconnect_returns_only_csrf_and_identity_not_api_credentials(self):
        self.login()
        response = self.client.get('/auth/session/', HTTP_ACCEPT='application/json', **HTML_REQUEST)
        self.assertEqual(set(response.json()), {'csrfToken', 'userId'})
        self.assertEqual(response.json()['userId'], str(self.user.pk))
        self.assertEqual(len(response.json()['csrfToken']), 64)
        self.assertIn('no-store', response['Cache-Control'])
        self.assertEqual(self.client.post('/auth/check/', HTTP_X_CSRFTOKEN=response.json()['csrfToken'],
                                         HTTP_ACCEPT='application/json', **HTML_REQUEST).status_code, 200)


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'],
                   EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ExternalAuthenticationContracts(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('api-user', 'api@example.org', PASSWORD)
        cls.other = User.objects.create_user('api-other', 'other@example.org', PASSWORD)
        EmailAddress.objects.create(user=cls.user, email=cls.user.email, verified=True, primary=True)
        cls.token = Token.objects.create(user=cls.user)

    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)

    def test_api_login_token_cookie_and_no_session_only_or_jwt_api_auth(self):
        response = self.client.post('/rest-auth/login/', {'username': self.user.username, 'password': PASSWORD}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json()), {'key'})
        self.assertEqual(self.client.get('/rest-auth/user/').status_code, 401)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {response.json()["key"]}')
        self.assertEqual(self.client.get('/rest-auth/user/').json()['username'], self.user.username)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer unsupported-jwt')
        self.assertEqual(self.client.get('/rest-auth/user/').status_code, 401)
        self.client.credentials(HTTP_AUTHORIZATION='Token invalid')
        self.assertEqual(self.client.get('/rest-auth/user/').status_code, 401)

    def test_api_logout_revokes_token_and_registration_still_issues_one(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(self.client.post('/rest-auth/logout/').status_code, 200)
        self.assertFalse(Token.objects.filter(key=self.token.key).exists())
        self.client.credentials()
        response = self.client.post('/rest-auth/registration/', {
            'username': 'new-api-user', 'email': 'new@example.org', 'password1': PASSWORD, 'password2': PASSWORD,
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertIn('key', response.json())
        self.assertTrue(mail.outbox)

    def test_recovery_tokens_valid_invalid_expired_and_replay(self):
        uid = user_pk_to_url_str(self.user)
        token = default_token_generator.make_token(self.user)
        body = {'uid': uid, 'token': token, 'new_password1': PASSWORD + '-new', 'new_password2': PASSWORD + '-new'}
        url = f'/rest-auth/password/reset/confirm/{uid}/{token}/'
        self.assertEqual(resolve(url).func.view_class.__name__, 'PasswordResetConfirmView')
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertEqual(self.client.post(url, {**body, 'token': 'bad'}, format='json').status_code, 400)
        future = default_token_generator._now() + timedelta(days=4)
        with patch.object(default_token_generator, '_now', return_value=future):
            self.assertEqual(self.client.post(url, body, format='json').status_code, 400)
        self.assertEqual(self.client.post(url, body, format='json').status_code, 200)
        self.assertEqual(self.client.post(url, body, format='json').status_code, 400)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(PASSWORD + '-new'))
        response = self.client.post('/rest-auth/password/reset/', {'email': self.user.email}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(mail.outbox)

    def test_social_accounts_are_scoped_and_foreign_disconnect_is_rejected(self):
        own = SocialAccount.objects.create(user=self.user, provider='orcid', uid='0000-0001-1111-1111')
        other = SocialAccount.objects.create(user=self.other, provider='orcid', uid='0000-0002-2222-2222')
        self.assertEqual(self.client.get('/rest-auth/socialaccounts/').status_code, 401)
        self.assertEqual(self.client.post('/rest-auth/orcid/connect/', {'code': 'unused'}, format='json').status_code, 401)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get('/rest-auth/socialaccounts/')
        self.assertEqual([item['id'] for item in response.json()['results']], [own.pk])
        self.assertEqual(self.client.post(f'/rest-auth/socialaccounts/{other.pk}/disconnect/').status_code, 404)
        self.assertEqual(self.client.post(f'/rest-auth/socialaccounts/{own.pk}/disconnect/').status_code, 200)
        self.assertTrue(SocialAccount.objects.filter(pk=other.pk).exists())
        self.assertFalse(SocialAccount.objects.filter(pk=own.pk).exists())

    def test_orcid_routes_and_authenticated_connect_require_credentials(self):
        for route, name in (('/rest-auth/orcid/', 'OrcidLogin'), ('/rest-auth/orcid/connect/', 'OrcidConnect')):
            self.assertEqual(resolve(route).func.view_class.__name__, name)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        # Empty credentials fail locally; no configured ORCID app/network is needed.
        self.assertEqual(self.client.post('/rest-auth/orcid/connect/', {}, format='json').status_code, 400)
