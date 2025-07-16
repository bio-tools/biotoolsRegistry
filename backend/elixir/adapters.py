from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.utils.safestring import mark_safe

class CustomDefaultAccountAdapter(DefaultAccountAdapter):

	def send_mail(self, template_prefix, email, context):
		context['activate_url'] = settings.URL_FRONT + \
			'signup/verify-email/' + context.get('key', 'token')
		
		if 'uid' in context and 'token' in context:
			context['password_reset_url'] = mark_safe(settings.URL_FRONT + 'reset-password/confirm?uid=' + context.get('uid') + '&token=' + context.get('token'))

		msg = self.render_mail(template_prefix, email, context)
		msg.send()