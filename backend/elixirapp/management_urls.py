from django.urls import re_path
from elixirapp import management_pages, workflows

urlpatterns = [
    re_path(r'^(?:domain-manager|subdomain)/?$', management_pages.domains),
    re_path(r'^(?:edit-domain|edit-subdomain)/?$', management_pages.domain),
    re_path(r'^(?:edit-domain|edit-subdomain)/(?P<identifier>[A-Za-z0-9-]{2,40})/?$', management_pages.domain),
    re_path(r'^(?P<identifier>[A-Za-z0-9.~_-]{1,100})/manage/?$', management_pages.record),
    re_path(r'^workflows/?$', workflows.page),
    re_path(r'^workflows/design/?$', workflows.designer),
]
