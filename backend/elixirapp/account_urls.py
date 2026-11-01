from django.urls import include, path, re_path
from django.views.generic import TemplateView
from allauth.account import views as account_views
from allauth.socialaccount import views as social_views
from allauth.decorators import rate_limit

from elixirapp import account_pages, browser_auth, canonical_urls, canonical_editor_urls, html_urls


def form(view, heading, submit, protected=False):
    handler = view.as_view(template_name='html/account_form.html',
                           extra_context={'heading': heading, 'submit_label': submit})
    return browser_auth.browser_login_required(handler) if protected else handler


def message(heading, text):
    return TemplateView.as_view(template_name='html/account_message.html',
                                extra_context={'heading': heading, 'message': text})


login = rate_limit(action='login')(browser_auth.BrowserLoginView.as_view())
account_patterns = [
    re_path(r'^login/?$', login, name='account_login'),
    path('auth/logout/', browser_auth.logout, name='account_logout'),
    re_path(r'^signup/?$', account_pages.SignupView.as_view(), name='account_signup'),
    path('signup/success', message('Account created', 'Your account has been created.'), name='account_signup_success'),
    path('signup/verify-email/success', message('Email verified', 'Your email address has been verified.'), name='account_email_verified'),
    path('signup/verify-email/', message('Check your email', 'Follow the verification link sent to your email address.'), name='account_email_verification_sent'),
    re_path(r'^signup/verify-email/(?P<key>[-:\w]+)/?$', account_views.ConfirmEmailView.as_view(template_name='html/email_confirm.html'), name='account_confirm_email'),
    re_path(r'^reset-password/?$', form(account_views.PasswordResetView, 'Reset password', 'Send reset link'), name='account_reset_password'),
    path('reset-password/sent/', message('Check your email', 'If an account matches this address, password reset instructions have been requested.'), name='account_reset_password_done'),
    path('reset-password/confirm', account_pages.legacy_reset_link),
    path('reset-password/confirm/', account_pages.legacy_reset_link),
    path('reset-password/confirm/success', message('Password changed', 'You can sign in with your new password.'), name='account_reset_password_from_key_done'),
    re_path(r'^reset-password/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>[^/]+)/$', form(account_views.PasswordResetFromKeyView, 'Choose a new password', 'Change password'), name='account_reset_password_from_key'),
    path('profile/password/', form(account_views.PasswordChangeView, 'Change password', 'Change password', True), name='account_change_password'),
    path('profile/password/set/', form(account_views.PasswordSetView, 'Set password', 'Set password', True), name='account_set_password'),
    path('profile/email/', account_pages.change_email, name='account_email'),
    path('profile/email/resend/', account_pages.resend_email, name='account_resend_email'),
    path('profile/connections/', form(social_views.ConnectionsView, 'Connected accounts', 'Disconnect selected account', True), name='socialaccount_connections'),
    path('auth/inactive/', message('Account unavailable', 'This account cannot sign in.'), name='account_inactive'),
    path('auth/reauthenticate/', form(account_views.ReauthenticateView, 'Confirm your password', 'Continue', True), name='account_reauthenticate'),
    path('auth/orcid/login/', account_pages.orcid_start, name='orcid_login'),
    path('auth/orcid/connect/', account_pages.orcid_start, {'connect': True}, name='orcid_connect'),
    path('orcid/callback/', account_pages.orcid_callback, name='orcid_callback'),
    path('auth/orcid/signup/', form(social_views.SignupView, 'Complete your account', 'Create account'), name='socialaccount_signup'),
    path('auth/orcid/cancelled/', message('ORCID request cancelled', 'No account connection was changed.'), name='socialaccount_login_cancelled'),
    path('auth/orcid/error/', account_pages.provider_error, name='socialaccount_login_error'),
]

html_account_patterns = [
    re_path(r'^login/?$', login, name='login'),
    re_path(r'^profile/?$', account_pages.profile, name='account'),
    path('auth/logout/', browser_auth.logout, name='logout'),
    path('auth/session/', browser_auth.session, name='session'),
    path('auth/check/', browser_auth.check, name='session-check'),
]


def patterns():
    # Literal search paths must precede the editor namespace's tool-ID matcher.
    return [*account_patterns, *canonical_urls.urlpatterns[1:-1], path('', include(([
        path('_migration/html/', include(html_urls.page_patterns)),
        *html_account_patterns,
        *canonical_editor_urls.editor_patterns,
    ], 'html'))), canonical_urls.urlpatterns[-1]]
