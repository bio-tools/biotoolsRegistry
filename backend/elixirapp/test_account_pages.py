from datetime import timedelta
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from allauth.account.forms import default_token_generator
from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from allauth.account.utils import user_pk_to_url_str
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialLogin
from allauth.socialaccount.providers.orcid.provider import OrcidProvider
from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.test import Client, TestCase, override_settings
from rest_framework.authtoken.models import Token

from elixir.queries import ToolSearchResult
from elixirapp.html import canonical_family


CANONICAL = {'biotools.canonical': True}
PASSWORD = 'Native-account-only-2026'
PROVIDER = {'orcid': {'BASE_DOMAIN': 'sandbox.orcid.org',
                     'APP': {'client_id': 'test-client', 'secret': 'test-secret'}}}


@override_settings(ACCOUNT_RATE_LIMITS=False,
                   PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'],
                   EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class NativeAccountTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('native-user', 'native@example.org', PASSWORD)
        cls.other = User.objects.create_user('native-other', 'other@example.org', PASSWORD)
        EmailAddress.objects.create(user=cls.user, email=cls.user.email, primary=True, verified=True)

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)

    def get(self, path, **kwargs):
        return self.client.get(path, **CANONICAL, **kwargs)

    def post(self, path, data=None, **kwargs):
        return self.client.post(path, data or {}, HTTP_X_CSRFTOKEN=self.client.cookies[settings.CSRF_COOKIE_NAME].value,
                                **CANONICAL, **kwargs)

    def login(self):
        self.get('/login')
        return self.post('/login', {'username': self.user.username, 'password': PASSWORD})

    def test_native_login_profile_helpers_and_external_token_isolation(self):
        token = Token.objects.create(user=self.user)
        self.assertEqual(self.login()['Location'], '/profile')
        page = self.get('/profile')
        self.assertContains(page, 'My profile')
        self.assertContains(page, self.user.email)
        self.assertContains(page, 'content="/auth/session/"')
        self.assertNotContains(page, '/dist/')
        self.assertEqual(page['X-Biotools-Route'], 'django-accounts')
        self.assertEqual(page['Referrer-Policy'], 'same-origin')
        self.assertIn('no-store', page['Cache-Control'])
        self.assertEqual(self.get('/auth/session/').json()['userId'], str(self.user.pk))
        self.assertEqual(self.client.get('/rest-auth/user/').status_code, 401)
        self.assertEqual(self.get('/auth/logout/').status_code, 405)
        self.assertEqual(self.post('/auth/logout/')['Location'], '/login')
        self.assertTrue(Token.objects.filter(key=token.key).exists())

    def test_csrf_expiry_safe_next_and_unrelated_route_boundaries(self):
        self.get('/login')
        self.assertEqual(self.client.post('/login', {'username': self.user.username, 'password': PASSWORD}, **CANONICAL).status_code, 403)
        self.assertEqual(self.post('/login', {'username': self.user.username, 'password': PASSWORD, 'next': '//evil.invalid'})['Location'], '/profile')
        self.post('/auth/logout/')
        expired = self.post('/auth/check/', HTTP_ACCEPT='application/json')
        self.assertEqual(expired.status_code, 401)
        self.assertIn('/login', expired.json()['error']['loginUrl'])
        for path in ('/api/rest-auth/login/', '/static/test.js'):
            self.assertIsNone(canonical_family(path))
        self.assertEqual(canonical_family('/domains'), 'public')
        self.assertEqual(self.get('/login').status_code, 200)

    def test_signup_policy_and_no_browser_token(self):
        self.assertNotContains(self.get('/signup'), 'Email (optional)')
        data = {'username': 'new-native', 'email': 'new-native@example.org', 'password1': PASSWORD, 'password2': PASSWORD}
        self.assertContains(self.post('/signup', {**data, 'email': ''}), 'This field is required')
        self.assertContains(self.post('/signup', {**data, 'username': 'bad username'}), 'errorlist')
        response = self.post('/signup', data)
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='new-native')
        self.assertFalse(Token.objects.filter(user=user).exists())
        self.assertTrue(mail.outbox)
        self.assertIn('http://testserver/signup/verify-email/', mail.outbox[-1].body)

    def test_verification_valid_invalid_and_consumed(self):
        address = EmailAddress.objects.get(user=self.user)
        address.verified = False
        address.save()
        key = EmailConfirmationHMAC(address).key
        result = self.get('/signup/verify-email/' + key)
        self.assertEqual(result.status_code, 302)
        address.refresh_from_db()
        self.assertTrue(address.verified)
        self.assertContains(self.get('/signup/verify-email/' + key), 'invalid, expired or already used')
        self.assertContains(self.get('/signup/verify-email/bad-key'), 'invalid, expired or already used')

    def test_reset_native_and_old_query_links_expiry_and_replay(self):
        self.get('/reset-password')
        response = self.post('/reset-password', {'email': self.user.email})
        self.assertEqual(response['Location'], '/reset-password/sent/')
        self.assertIn('http://testserver/reset-password/confirm?uid=', mail.outbox[-1].body)
        self.assertIn('&token=', mail.outbox[-1].body)
        self.assertEqual(self.post('/reset-password', {'email': 'unknown@example.org'})['Location'], response['Location'])
        uid, token = user_pk_to_url_str(self.user), default_token_generator.make_token(self.user)
        link = '/reset-password/confirm?uid=' + uid + '&token=' + token
        first = self.get(link)
        clean = self.get(first['Location'])
        self.assertIn('set-password', clean['Location'])
        self.get(clean['Location'])
        saved = self.post(clean['Location'], {'password1': PASSWORD + '-new', 'password2': PASSWORD + '-new'})
        self.assertEqual(saved.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(PASSWORD + '-new'))
        self.assertContains(self.get(first['Location']), 'invalid or has expired')
        future = default_token_generator._now() + timedelta(days=4)
        token = default_token_generator.make_token(self.user)
        with patch.object(default_token_generator, '_now', return_value=future):
            self.assertContains(self.get(f'/reset-password/key/{uid}-{token}/'), 'invalid or has expired')

    def test_profile_email_password_and_resend_are_protected(self):
        self.assertEqual(self.get('/profile/email/').status_code, 302)
        self.login()
        self.assertEqual(self.client.post('/profile/email/', {'email': 'changed@example.org'}, **CANONICAL).status_code, 403)
        self.assertEqual(self.post('/profile/email/', {'email': 'changed@example.org'})['Location'], '/profile')
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'changed@example.org')
        self.assertFalse(EmailAddress.objects.get(user=self.user, primary=True).verified)
        self.post('/profile/email/resend/')
        self.assertTrue(mail.outbox)
        self.assertEqual(self.get('/profile/email/resend/').status_code, 405)
        self.assertEqual(self.post('/profile/password/', {'oldpassword': PASSWORD, 'password1': PASSWORD + '-new', 'password2': PASSWORD + '-new'}).status_code, 302)
        self.assertEqual(self.get('/profile').status_code, 200)

    def test_disconnect_is_scoped_and_last_login_method_is_retained(self):
        own = SocialAccount.objects.create(user=self.user, provider='orcid', uid='0000-0001')
        foreign = SocialAccount.objects.create(user=self.other, provider='orcid', uid='0000-0002')
        self.login()
        self.assertContains(self.post('/profile/connections/', {'account': foreign.pk}), 'Select a valid choice')
        self.user.set_unusable_password()
        self.user.save()
        self.client.force_login(self.user)
        result = self.post('/profile/connections/', {'account': own.pk})
        self.assertEqual(result.status_code, 200)
        self.assertTrue(SocialAccount.objects.filter(pk=own.pk).exists())

    def test_email_conflicts_do_not_change_either_account(self):
        EmailAddress.objects.create(user=self.other, email=self.other.email, primary=True, verified=True)
        self.login()
        for email in (self.user.email, self.other.email):
            self.assertContains(self.post('/profile/email/', {'email': email}), 'This email address cannot be used.')
            self.user.refresh_from_db()
            self.assertEqual(self.user.email, 'native@example.org')
        self.assertTrue(EmailAddress.objects.get(user=self.user).verified)

    @patch('elixirapp.search_workspace.search_tools', return_value=ToolSearchResult([], 0, 1, 50, 1, 1))
    def test_search_and_editor_routes_keep_their_owners_with_accounts_enabled(self, search):
        self.assertContains(self.get('/t?q=sequence'), '/_search/data/')
        self.assertEqual(self.get('/t/?q=sequence')['Location'], '/t?q=sequence')
        self.assertEqual(self.get('/t?domain=proteomics').status_code, 200)
        self.assertEqual(self.get('/_search/data/?unsupported=1').status_code, 400)
        self.login()
        self.assertContains(self.get('/profile'), 'My profile')
        self.post('/auth/logout/')

    @override_settings(SOCIALACCOUNT_PROVIDERS=PROVIDER)
    def test_orcid_state_cancel_and_safe_callback(self):
        self.get('/login')
        self.assertEqual(self.get('/auth/orcid/login/').status_code, 405)
        response = self.post('/auth/orcid/login/', {'next': '//evil.invalid/'})
        query = parse_qs(urlsplit(response['Location']).query)
        self.assertEqual(query['redirect_uri'], ['http://testserver/orcid/callback/'])
        state = query['state'][0]
        with patch('allauth.socialaccount.providers.orcid.views.OrcidOAuth2Adapter.get_access_token_data') as exchange:
            self.assertEqual(self.get('/orcid/callback/?state=bad&code=unused').status_code, 400)
            self.assertEqual(self.get('/orcid/callback/?state=' + state + '&error=access_denied').status_code, 400)
            exchange.assert_not_called()
        self.assertNotIn('_auth_user_id', self.client.session)

    @override_settings(SOCIALACCOUNT_PROVIDERS=PROVIDER)
    def test_orcid_existing_login_and_state_replay(self):
        SocialAccount.objects.create(user=self.user, provider='orcid', uid='0000-0001')
        self.get('/login')
        start = self.post('/auth/orcid/login/')
        state = parse_qs(urlsplit(start['Location']).query)['state'][0]
        social = SocialLogin(user=User(), account=SocialAccount(provider='orcid', uid='0000-0001'))
        with patch('allauth.socialaccount.providers.orcid.views.OrcidOAuth2Adapter.get_access_token_data', return_value={'access_token': 'test-token'}), patch('allauth.socialaccount.providers.orcid.views.OrcidOAuth2Adapter.complete_login', return_value=social):
            result = self.get('/orcid/callback/?state=' + state + '&code=test-code')
        self.assertEqual(result.status_code, 302)
        self.assertEqual(self.client.session['_auth_user_id'], str(self.user.pk))
        self.assertFalse(Token.objects.filter(user=self.user).exists())
        self.assertEqual(self.get('/orcid/callback/?state=' + state + '&code=test-code').status_code, 400)

    @override_settings(SOCIALACCOUNT_PROVIDERS=PROVIDER)
    def test_orcid_connect_bound_to_initiator_and_foreign_account_rejected(self):
        self.login()
        foreign = SocialAccount.objects.create(user=self.other, provider='orcid', uid='foreign-orcid')
        for changed_user in (False, True):
            self.client.force_login(self.user)
            start = self.post('/auth/orcid/connect/')
            state = parse_qs(urlsplit(start['Location']).query)['state'][0]
            if changed_user:
                session = self.client.session
                pending = session.get('socialaccount_states')
                self.client.force_login(self.other)
                session = self.client.session
                session['socialaccount_states'] = pending
                session.save()
            social = SocialLogin(user=User(), account=SocialAccount(provider='orcid', uid='foreign-orcid'))
            with patch('allauth.socialaccount.providers.orcid.views.OrcidOAuth2Adapter.get_access_token_data', return_value={'access_token': 'test-token'}), patch('allauth.socialaccount.providers.orcid.views.OrcidOAuth2Adapter.complete_login', return_value=social):
                response = self.get('/orcid/callback/?state=' + state + '&code=test-code')
            self.assertEqual(response.status_code, 400 if changed_user else 302)
            foreign.refresh_from_db()
            self.assertEqual(foreign.user_id, self.other.pk)
            self.assertFalse(SocialAccount.objects.filter(user=self.user).exists())

    @override_settings(SOCIALACCOUNT_PROVIDERS=PROVIDER)
    def test_orcid_successful_connect_and_disconnect(self):
        self.login()
        start = self.post('/auth/orcid/connect/')
        state = parse_qs(urlsplit(start['Location']).query)['state'][0]
        social = SocialLogin(user=User(), account=SocialAccount(provider='orcid', uid='new-orcid'))
        with patch('allauth.socialaccount.providers.orcid.views.OrcidOAuth2Adapter.get_access_token_data', return_value={'access_token': 'test-token'}), patch('allauth.socialaccount.providers.orcid.views.OrcidOAuth2Adapter.complete_login', return_value=social):
            response = self.get('/orcid/callback/?state=' + state + '&code=test-code')
        self.assertEqual(response.status_code, 302)
        account = SocialAccount.objects.get(user=self.user, uid='new-orcid')
        self.assertEqual(self.post('/profile/connections/', {'account': account.pk}).status_code, 302)
        self.assertFalse(SocialAccount.objects.filter(pk=account.pk).exists())

    @override_settings(SOCIALACCOUNT_PROVIDERS=PROVIDER)
    def test_orcid_email_collision_cannot_sign_in_as_existing_user(self):
        self.get('/login')
        start = self.post('/auth/orcid/login/')
        state = parse_qs(urlsplit(start['Location']).query)['state'][0]
        social = SocialLogin(user=User(username='orcid-collision', email=self.user.email),
                             provider=OrcidProvider(None, app=SocialApp(provider='orcid', client_id='test-client', secret='test-secret')),
                             account=SocialAccount(provider='orcid', uid='email-collision'),
                             email_addresses=[EmailAddress(email=self.user.email, verified=True, primary=True)])
        with patch('allauth.socialaccount.providers.orcid.views.OrcidOAuth2Adapter.get_access_token_data', return_value={'access_token': 'test-token'}), patch('allauth.socialaccount.providers.orcid.views.OrcidOAuth2Adapter.complete_login', return_value=social):
            response = self.get('/orcid/callback/?state=' + state + '&code=test-code')
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertFalse(SocialAccount.objects.filter(uid='email-collision').exists())

    def test_unconfigured_provider_fails_locally_and_preview_alias_still_works(self):
        self.get('/login')
        self.assertEqual(self.post('/auth/orcid/login/').status_code, 503)
        self.assertEqual(self.client.get('/auth/login/', **{'biotools.html': True}).status_code, 200)
