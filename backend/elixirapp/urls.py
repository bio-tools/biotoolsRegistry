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
from dj_rest_auth.views import PasswordResetView, PasswordResetConfirmView
from dj_rest_auth.registration.views import SocialAccountListView, SocialAccountDisconnectView
from django.contrib import admin
from django.urls import include, path, re_path
from elixir import views

urlpatterns = [
	re_path(r'^admin/', admin.site.urls),
	# url(r'^', include('django.contrib.auth.urls')),
	# url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
	# url(r'^api-token-auth/', 'rest_framework_jwt.views.obtain_jwt_token'),
	path('rest-auth/', include('dj_rest_auth.urls')),
	path('rest-auth/registration/',
		 include('dj_rest_auth.registration.urls')),
	# Password reset
	path('rest-auth/password/reset/',
		 PasswordResetView.as_view(),
		 name='rest_password_reset'
		 ),
	path('rest-auth/password/reset/confirm/<uidb64>/<token>/',
		 PasswordResetConfirmView.as_view(),
		 name='password_reset_confirm'),
	path('accounts/', include('allauth.urls')),
	path('', include('elixir.urls')),
    
	# Social auth
    path('rest-auth/orcid/', views.OrcidLogin.as_view(), name='orcid_login'),
    path('rest-auth/orcid/connect/', views.OrcidConnect.as_view(), name='orcid_connect'),
    path('rest-auth/github/', views.GitHubLogin.as_view(), name='github_login'),
    path('rest-auth/github/connect/', views.GitHubConnect.as_view(), name='github_connect'),
    path('rest-auth/github/callback/', views.GitHubLoginCallback.as_view(), name='github_login_callback'),
    path('rest-auth/socialaccounts/', SocialAccountListView.as_view(), name='social_account_list'),
    path('rest-auth/socialaccounts/<int:pk>/disconnect/', SocialAccountDisconnectView.as_view(), name='social_account_disconnect'),
]
