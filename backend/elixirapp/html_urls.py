from django.urls import include, path, re_path

from elixirapp import html, tool_detail, search_workspace, edam, browser_auth, resource_editor, resource_requests, record_preview
from elixirapp import browser_api, public_urls


page_patterns = [
        path('public/', include(public_urls)),
        path('', html.index, name='index'),
        path('auth/login/', browser_auth.BrowserLoginView.as_view(), name='login'),
        path('auth/logout/', browser_auth.logout, name='logout'),
        path('auth/session/', browser_auth.session, name='session'),
        path('auth/check/', browser_auth.check, name='session-check'),
        path('account/', browser_auth.account, name='account'),
        path('api/<path:api_path>', browser_api.dispatch, name='browser-api'),
        path('requests/', resource_requests.inbox, name='requests'),
        path('requests/conclude/', resource_requests.conclude, name='request-conclude'),
        re_path(r'^requests/tool/(?P<identifier>[A-Za-z0-9.~_-]{1,100})/$', resource_requests.create, name='request-create'),
        path('editor/new/', resource_editor.page, name='editor-new'),
        path('editor/new/validate/', resource_editor.save, {'validate_only': True}),
        path('editor/new/record-preview/', record_preview.preview),
        re_path(r'^editor/tool/(?P<identifier>[A-Za-z0-9.~_-]{1,100})/validate/$', resource_editor.save, {'validate_only': True}),
        re_path(r'^editor/tool/(?P<identifier>[A-Za-z0-9.~_-]{1,100})/record-preview/$', record_preview.preview),
        path('editor/new/save/', resource_editor.save, name='editor-create'),
        re_path(r'^editor/tool/(?P<identifier>[A-Za-z0-9.~_-]{1,100})/$', resource_editor.page, name='editor-edit'),
        re_path(r'^editor/tool/(?P<identifier>[A-Za-z0-9.~_-]{1,100})/save/$', resource_editor.save, name='editor-save'),
        path('preview/', html.preview, name='preview'),
        path('islands/', html.islands, name='islands'),
        path('search/', search_workspace.page, name='search'),
        path('search/data/', search_workspace.data, name='search-data'),
        path('search/options/', search_workspace.options, name='search-options'),
        path('edam/', edam.preview, name='edam-preview'),
        path('edam/terms/', edam.lookup, name='edam-lookup'),
        re_path(r'^tool/(?:biotools:)?(?P<identifier>[A-Za-z0-9.~_-]{1,100})/$',
                tool_detail.detail, name='tool-detail'),
]

urlpatterns = [path('', include((page_patterns, 'html')))]

handler404 = html.page_not_found
handler500 = html.server_error
