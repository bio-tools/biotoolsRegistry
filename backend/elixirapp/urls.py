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
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
	url(r'^admin/', admin.site.urls)	,
	# url(r'^', include('django.contrib.auth.urls')),
	# url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
	# url(r'^api-token-auth/', 'rest_framework_jwt.views.obtain_jwt_token'),
	url(r'^rest-auth/', include('rest_auth.urls')),
	url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
	url(r'^accounts/', include('allauth.urls')),
	url(r'^', include('elixir.urls')),
]
