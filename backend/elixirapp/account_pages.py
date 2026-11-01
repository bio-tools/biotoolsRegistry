"""Native account pages using the installed account forms and policy."""
from django import forms
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.views.decorators.cache import never_cache
from allauth.account import views as account_views
from allauth.account.forms import SignupForm
from allauth.decorators import rate_limit
from allauth.account.models import EmailAddress
from allauth.account.internal.flows.email_verification import send_verification_email_to_address
from allauth.socialaccount.adapter import get_adapter as social_adapter
from allauth.socialaccount.providers.orcid.views import oauth2_callback
from rest_framework.exceptions import ValidationError

from elixir.serializers import CustomUserDetailsSerializer, UserRegisterSerializer
from elixirapp.browser_auth import browser_login_required


class NativeSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['email'].label = 'Email'

    def clean_username(self):
        value = super().clean_username()
        try:
            return UserRegisterSerializer().validate_username(value)
        except ValidationError as exc:
            raise forms.ValidationError(exc.detail) from exc


class SignupView(account_views.SignupView):
    form_class = NativeSignupForm
    template_name = 'html/account_form.html'
    extra_context = {'heading': 'Create account', 'submit_label': 'Create account'}

    def get_default_success_url(self):
        return reverse('account_signup_success')


class EmailForm(forms.Form):
    email = forms.EmailField(label='New email', widget=forms.EmailInput(attrs={'autocomplete': 'email'}))


@browser_login_required
@require_GET
def profile(request):
    return render(request, 'html/profile.html', {
        'profile': CustomUserDetailsSerializer(request.user).data,
    })


@browser_login_required
@require_http_methods(['GET', 'POST'])
@rate_limit(action='manage_email')
def change_email(request):
    form = EmailForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        serializer = CustomUserDetailsSerializer(request.user, data=form.cleaned_data, partial=True)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    serializer.save()
            except (ValidationError, IntegrityError):
                pass
            else:
                messages.success(request, 'Email updated. Verify your new address from your profile.')
                return redirect('html:account')
        # Do not disclose whether a supplied address belongs to another account.
        form.add_error('email', 'This email address cannot be used.')
    return render(request, 'html/account_form.html', {
        'form': form, 'heading': 'Change email', 'submit_label': 'Change email',
    })


@browser_login_required
@require_POST
@rate_limit(action='manage_email')
def resend_email(request):
    address = EmailAddress.objects.filter(user=request.user, primary=True, verified=False).first()
    if address and not address.email.endswith('@biotools.local'):
        send_verification_email_to_address(request, address)
    messages.success(request, 'If your address needs verification, a verification email has been requested.')
    return redirect('html:account')


@never_cache
@require_GET
def legacy_reset_link(request):
    # dj-rest-auth uses allauth's base36 user IDs and token generator in this installation.
    uid, token = request.GET.get('uid', ''), request.GET.get('token', '')
    if not uid.isalnum() or not token or '/' in token or len(token) > 200:
        return render(request, 'html/account_message.html', {
            'heading': 'Invalid password reset link',
            'message': 'Request a new password reset email.',
        }, status=400)
    return redirect('account_reset_password_from_key', uidb36=uid, key=token)


def provider_error(request, status=400):
    return render(request, 'html/account_message.html', {
        'heading': 'ORCID sign-in unavailable',
        'message': 'The ORCID request could not be completed. Return to your account or sign in and try again.',
    }, status=status)


@never_cache
@require_POST
def orcid_start(request, connect=False):
    if connect and not request.user.is_authenticated:
        from elixirapp.browser_auth import authentication_required
        return authentication_required(request)
    provider = social_adapter(request).get_provider(request, 'orcid')
    if not provider.app.client_id or not provider.app.secret:
        return provider_error(request, 503)
    next_url = request.POST.get('next', '')
    if not url_has_allowed_host_and_scheme(next_url, {request.get_host()}, require_https=request.is_secure()):
        next_url = reverse('html:account')
    return provider.redirect(request, process='connect' if connect else 'login', next_url=next_url,
                             data={'account_user': str(request.user.pk) if connect else None})


@never_cache
@require_GET
def orcid_callback(request):
    provider = social_adapter(request).get_provider(request, 'orcid')
    if not provider.app.client_id or not provider.app.secret:
        return provider_error(request, 503)
    return oauth2_callback(request)
