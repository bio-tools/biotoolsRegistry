from django.urls import path, re_path
from elixirapp import public_pages

urlpatterns = [path('', public_pages.page, name='public-home')]
urlpatterns += [re_path(r'^' + name + r'/?$', public_pages.page, {'name': name}, name='public-' + name)
                for name in sorted(public_pages.PAGES - {''})]
urlpatterns += [re_path(r'^(?:' + '|'.join(sorted(public_pages.PAGES - {''})) + r')/.+$',
                        public_pages.page, {'name': '404'})]
