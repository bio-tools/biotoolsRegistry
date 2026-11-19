from django.conf import settings


def is_production():
    return str(settings.DEPLOYMENT).strip().lower() in ('production', 'prod')


def notice(request):
    return {'show_environment_notice': not is_production()}
