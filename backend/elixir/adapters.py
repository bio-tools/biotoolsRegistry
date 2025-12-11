from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomDefaultAccountAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix, email, context):
        # Add frontend URL to context for templates
        context['domain'] = settings.URL_FRONT
        context['site_name'] = settings.SITE_NAME

        # Fix email confirmations
        if 'activate_url' in context:
            key = context.get('key')
            context['activate_url'] = f"{settings.URL_FRONT}signup/verify-email/{key}"

        # Let dj-rest-auth handle the URL construction based on settings
        msg = self.render_mail(template_prefix, email, context)
        msg.send()
    
    def clean_email(self, email):
        """
        Override email validation to handle empty emails for social accounts
        """
        if email:
            return super().clean_email(email)
        return email


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Handle the case when a user tries to login with social account
        but an account with that email already exists.
        """
        if sociallogin.is_existing:
            return
        
        # If user is already authenticated, this is a "connect" scenario
        if request.user.is_authenticated:
            if sociallogin.email_addresses:
                social_email = sociallogin.email_addresses[0].email
                user_email = request.user.email
            
                # Warn if emails don't match (but still allow connection for now)
                if social_email != user_email and not user_email.endswith('@biotools.local'):
                    print(f"WARNING: Email mismatch! User email ({user_email}) != Social account email ({social_email})")
                    # could raise an exception here to prevent connection
            
            # Connect the social account to the current logged-in user
            sociallogin.connect(request, request.user)
            return
            
        if not sociallogin.email_addresses:
            return
            
        email = sociallogin.email_addresses[0].email
        
        try:
            existing_user = User.objects.get(email=email)
            sociallogin.connect(request, existing_user)
            
        except User.DoesNotExist:
            pass
    
    def save_user(self, request, sociallogin, form=None):
        """
        Save the user account with additional handling for existing users.
        """
        email = sociallogin.email_addresses[0].email if sociallogin.email_addresses else 'No email provided'
        
        # If no email is provided, we need to handle this case
        if not sociallogin.email_addresses:
            print("Creating user without email address")
            
        user = super().save_user(request, sociallogin, form)
        return user
        
    def is_auto_signup_allowed(self, request, sociallogin):
        """
        Always allow auto signup for social accounts.
        """
        return True
    
    def populate_user(self, request, sociallogin, data):
        """
        Populate user information from social account data.
        """
        user = super().populate_user(request, sociallogin, data)
        
        # If no email was provided, generate a unique placeholder email
        if not data.get('email') and hasattr(user, 'email'):
            username = data.get('username', 'user')
            
            # Generate a unique placeholder email with timestamp to avoid conflicts
            import time
            timestamp = int(time.time())
            placeholder_email = f"{username}.{timestamp}@biotools.local"
            
            # Actually assign the placeholder email to the user
            user.email = placeholder_email

        return user
