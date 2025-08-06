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

urlpatterns = [
	re_path(r'^admin/', admin.site.urls),
	# url(r'^', include('django.contrib.auth.urls')),
	# url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
	# url(r'^api-token-auth/', 'rest_framework_jwt.views.obtain_jwt_token'),
	path('rest-auth/', include('dj_rest_auth.urls')),
	path('rest-auth/registration/',
		 include('dj_rest_auth.registration.urls')),
	path('accounts/', include('allauth.urls')),
	path('', include('elixir.urls')),
]
