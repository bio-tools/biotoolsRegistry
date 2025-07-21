"""elixirapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
	1. Add an import:  from my_app import views
	2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
	1. Add an import:  from other_app.views import Home
	2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
	1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView

urlpatterns = [
	re_path(r'^password-reset/$', TemplateView.as_view(template_name="password_reset.html"), name='password-reset'),
    
	# this url is used to generate email content
	re_path(r'^password-reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$', TemplateView.as_view(template_name="password_reset_confirm.html"), name='password_reset_confirm'),

	re_path(r'^admin/', admin.site.urls),
	path('rest-auth/', include('dj_rest_auth.urls')),
	path('rest-auth/registration/',
		 include('dj_rest_auth.registration.urls')),
	path('accounts/', include('allauth.urls')),
	path('', include('elixir.urls')),
]
