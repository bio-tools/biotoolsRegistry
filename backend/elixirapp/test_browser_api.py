from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings
from rest_framework.authtoken.models import Token

from elixirapp.test_html import HTML_REQUEST


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
                   PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class BrowserSessionBridgeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('bridge-user', 'bridge@example.org', 'Bridge-test-2026')
        EmailAddress.objects.create(user=cls.user, email=cls.user.email, verified=True, primary=True)

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        config = self.client.get('/browser-session/')
        self.assertEqual(config.json(), {'enabled': True, 'accountsEnabled': True})
        self.assertIn('no-store', config['Cache-Control'])

    def post(self, path, data=None):
        return self.client.post('/api/rest-auth/' + path, data or {}, content_type='application/json',
                                HTTP_X_CSRFTOKEN=self.client.cookies['csrftoken'].value, **HTML_REQUEST)

    def test_browser_login_profile_modern_editor_and_logout_share_session_not_token(self):
        data = {'username': self.user.username, 'password': 'Bridge-test-2026'}
        self.assertEqual(self.client.post('/api/rest-auth/login/', data, content_type='application/json',
                                         **HTML_REQUEST).status_code, 403)
        response = self.post('login/', data)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertNotIn('key', response.json())
        self.assertFalse(Token.objects.filter(user=self.user).exists())
        self.assertEqual(self.client.get('/api/rest-auth/user/', **HTML_REQUEST).json()['username'], self.user.username)
        self.assertEqual(self.client.get('/editor/new/', **HTML_REQUEST).status_code, 200)
        # The external API remains token-only despite this browser session.
        self.assertEqual(self.client.get('/rest-auth/user/').status_code, 401)
        token = Token.objects.create(user=self.user)
        self.assertEqual(self.post('logout/').status_code, 200)
        self.assertTrue(Token.objects.filter(pk=token.pk).exists())
        self.assertEqual(self.client.get('/editor/new/', **HTML_REQUEST).status_code, 302)
        self.assertEqual(self.client.get('/api/rest-auth/user/', **HTML_REQUEST).status_code, 403)

    def test_modern_login_is_recognized_by_retained_profile_and_mutations_require_csrf(self):
        self.client.get('/auth/login/', **HTML_REQUEST)
        self.client.post('/auth/login/', {'username': self.user.username, 'password': 'Bridge-test-2026'},
                         HTTP_X_CSRFTOKEN=self.client.cookies['csrftoken'].value, **HTML_REQUEST)
        url = '/api/rest-auth/user/'
        self.assertEqual(self.client.get(url, **HTML_REQUEST).status_code, 200)
        self.assertEqual(self.client.patch(url, {'first_name': 'No'}, content_type='application/json',
                                          **HTML_REQUEST).status_code, 403)
        response = self.client.patch(url, {'email': 'bridge-changed@example.org'}, content_type='application/json',
                                     HTTP_X_CSRFTOKEN=self.client.cookies['csrftoken'].value, **HTML_REQUEST)
        self.assertEqual(response.status_code, 200, response.content)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'bridge-changed@example.org')
        self.assertEqual(self.client.post('/api/request/conclude', {}, content_type='application/json',
                         HTTP_ORIGIN='https://evil.invalid', HTTP_X_CSRFTOKEN=self.client.cookies['csrftoken'].value,
                         **HTML_REQUEST).status_code, 403)

    def test_mixed_credentials_rejected_and_disabled_bridge_fails_closed(self):
        self.client.force_login(self.user)
        token = Token.objects.create(user=self.user)
        self.assertEqual(self.client.get('/api/rest-auth/user/', HTTP_AUTHORIZATION='Token ' + token.key,
                                         **HTML_REQUEST).status_code, 400)
        self.assertEqual(self.client.get('/api/admin/', **HTML_REQUEST).status_code, 404)

    def test_signup_recovery_and_social_routes_reuse_policy_without_browser_tokens(self):
        response = self.post('registration/', {'username': 'bridge-new', 'email': 'bridge-new@example.org',
                                              'password1': 'Bridge-test-2026', 'password2': 'Bridge-test-2026'})
        self.assertEqual(response.status_code, 201, response.content)
        self.assertNotIn('key', response.json())
        self.assertFalse(Token.objects.filter(user__username='bridge-new').exists())
        self.assertEqual(self.post('password/reset/', {'email': self.user.email}).status_code, 200)
        self.client.force_login(self.user)
        self.assertEqual(self.client.get('/api/rest-auth/socialaccounts/', **HTML_REQUEST).status_code, 200)
        self.assertEqual(self.post('orcid/connect/').status_code, 400)
        self.assertEqual(self.post('orcid/').status_code, 400)
        self.assertFalse(Token.objects.filter(user=self.user).exists())
