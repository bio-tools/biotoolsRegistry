from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings


class CustomDefaultAccountAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix, email, context):
        # Add frontend URL to context for templates
        context["domain"] = settings.URL_FRONT
        context["site_name"] = settings.SITE_NAME

        # Fix email confirmations
        if "activate_url" in context:
            key = context.get("key")
            context["activate_url"] = f"{settings.URL_FRONT}signup/verify-email/{key}"

        # Let dj-rest-auth handle the URL construction based on settings
        msg = self.render_mail(template_prefix, email, context)
        msg.send()
