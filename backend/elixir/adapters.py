from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings

class CustomDefaultAccountAdapter(DefaultAccountAdapter):

	def send_mail(self, template_prefix, email, context):
		key = context.get('key') or context.get('token')
		context['activate_url'] = settings.URL_FRONT + \
			'signup/verify-email/' + key
		msg = self.render_mail(template_prefix, email, context)
		msg.send()

