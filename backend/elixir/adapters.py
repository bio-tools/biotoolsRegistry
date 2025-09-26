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
        print(f"pre_social_login called, sociallogin.is_existing: {sociallogin.is_existing}")
        print(f"User authenticated: {request.user.is_authenticated}")
        
        if sociallogin.is_existing:
            print("Social login is existing, returning early")
            return
        
        # If user is already authenticated, this is a "connect" scenario
        if request.user.is_authenticated:
            print(f"Connect scenario: Current user {request.user.username} wants to connect GitHub account")
            
            # Check if GitHub provides an email
            if sociallogin.email_addresses:
                github_email = sociallogin.email_addresses[0].email
                user_email = request.user.email
                
                print(f"GitHub email: {github_email}")
                print(f"User email: {user_email}")
                
                # Warn if emails don't match (but still allow connection for now)
                if github_email != user_email and not user_email.endswith('@github.local') and not user_email.endswith('@biotools.local'):
                    print(f"WARNING: Email mismatch! User email ({user_email}) != GitHub email ({github_email})")
                    # could raise an exception here to prevent connection
                    # raise forms.ValidationError("GitHub email doesn't match your account email. Please use a GitHub account with the same email address.")
            
            # Connect the social account to the current logged-in user
            print(f"Connecting GitHub account to current user: {request.user.username}")
            sociallogin.connect(request, request.user)
            print("Successfully connected GitHub account to current user")
            return
            
        if not sociallogin.email_addresses:
            print("No email addresses found in social login - this is normal for GitHub users with private emails")
            return
            
        # Get the email from the social account
        email = sociallogin.email_addresses[0].email
        print(f"Checking for existing user with email: {email}")
        
        try:
            # Check if a user with this email already exists
            existing_user = User.objects.get(email=email)
            print(f"Found existing user: {existing_user.username} with email: {existing_user.email}")
            
            # Connect the social account to the existing user
            sociallogin.connect(request, existing_user)
            print("Successfully connected social account to existing user")
            
        except User.DoesNotExist:
            # No existing user, let the normal flow continue
            print("No existing user found, continuing with normal flow")
            pass
    
    def save_user(self, request, sociallogin, form=None):
        """
        Save the user account with additional handling for existing users.
        """
        email = sociallogin.email_addresses[0].email if sociallogin.email_addresses else 'No email provided'
        print(f"save_user called for sociallogin with email: {email}")
        
        # If no email is provided, we need to handle this case
        if not sociallogin.email_addresses:
            print("Creating user without email address (GitHub private email)")
            
        user = super().save_user(request, sociallogin, form)
        print(f"User saved: {user.username} with email: {user.email}")
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
        print(f"populate_user called with data: {data}")
        user = super().populate_user(request, sociallogin, data)
        
        # If no email was provided, generate a unique placeholder email
        if not data.get('email') and hasattr(user, 'email'):
            username = data.get('username', 'user')
            # Generate a unique placeholder email with timestamp to avoid conflicts
            import time
            timestamp = int(time.time())
            placeholder_email = f"{username}.{timestamp}@github.local"
            print(f"No email provided by GitHub, setting unique placeholder email: {placeholder_email}")

        print(f"populate_user result: {user.username} with email: {user.email}")
        return user
