"""Canonical editor/request names with the remaining HTML helpers at their preview mount."""
from django.urls import include, path, re_path
from elixirapp import edam, html, html_urls, resource_editor, resource_requests, search_workspace, tool_detail, public_urls, management_urls, workflow_matching, workflow_drafts
from elixirapp.github_bridge import import_repository


editor_patterns = [
        re_path(r'^register/?$', resource_editor.page, name='editor-new'),
        path('register/save/', resource_editor.save, name='editor-create'),
        path('register/validate/', resource_editor.save, {'validate_only': True}),
        re_path(r'^(?P<identifier>[A-Za-z0-9.~_-]{1,100})/edit/?$', resource_editor.page, name='editor-edit'),
        re_path(r'^(?P<identifier>[A-Za-z0-9.~_-]{1,100})/edit/save/$', resource_editor.save, name='editor-save'),
        re_path(r'^(?P<identifier>[A-Za-z0-9.~_-]{1,100})/edit/validate/$', resource_editor.save, {'validate_only': True}),
        re_path(r'^requests/?$', resource_requests.inbox, name='requests'),
        path('requests/conclude/', resource_requests.conclude, name='request-conclude'),
        re_path(r'^requests/tool/(?P<identifier>[A-Za-z0-9.~_-]{1,100})/$', resource_requests.create, name='request-create'),
        re_path(r'^(?P<identifier>[A-Za-z0-9.~_-]{1,100})/?$',
                tool_detail.detail, name='tool-detail'),
        re_path(r'^(?:(?:tool|t)/)?(?:biotools:)?(?P<identifier>[A-Za-z0-9.~_-]{1,100})/?$', tool_detail.detail),
]

urlpatterns = [
    path('github-to-biotools', import_repository),
    *management_urls.urlpatterns,
    *public_urls.urlpatterns,
    path('t', search_workspace.canonical_page, name='canonical-search'),
    path('t/', search_workspace.canonical_page),
    path('_search/data/', search_workspace.data, name='canonical-search-data'),
    path('_edam/terms/', edam.lookup, name='canonical-edam-lookup'),
    path('_workflow/matches/', workflow_matching.candidates, name='workflow-matches'),
    path('_workflow/function/', workflow_matching.function, name='workflow-function'),
    path('_workflow/compare/', workflow_matching.compare, name='workflow-compare'),
    path('_workflow/designs/', workflow_drafts.collection, name='workflow-designs'),
    path('_workflow/designs/<uuid:identifier>/', workflow_drafts.detail, name='workflow-design'),
    path('_workflow/designs/<uuid:identifier>/share/', workflow_drafts.share, name='workflow-design-share'),
    path('_workflow/shared/', workflow_drafts.shared, name='workflow-shared'),
    path('', include(([path('_migration/html/', include(html_urls.page_patterns)), *editor_patterns], 'html'))),
]

handler404 = html.page_not_found
handler500 = html.server_error
