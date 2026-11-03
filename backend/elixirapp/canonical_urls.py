from django.urls import include, path, re_path
from elixirapp import edam, html, search_workspace, tool_detail, public_urls, github_bridge, management_urls, workflow_matching, workflow_drafts

urlpatterns = [
    path('_migration/html/', include('elixirapp.html_urls')),
    path('github-to-biotools', github_bridge.import_repository),
    *management_urls.urlpatterns,
    *public_urls.urlpatterns,
    path('t', search_workspace.canonical_page, name='canonical-search'),
    path('t/', search_workspace.canonical_page),
    path('_search/data/', search_workspace.data, name='canonical-search-data'),
    path('_search/options/', search_workspace.options, name='canonical-search-options'),
    path('_edam/terms/', edam.lookup, name='canonical-edam-lookup'),
    path('_workflow/matches/', workflow_matching.candidates, name='workflow-matches'),
    path('_workflow/function/', workflow_matching.function, name='workflow-function'),
    path('_workflow/compare/', workflow_matching.compare, name='workflow-compare'),
    path('_workflow/designs/', workflow_drafts.collection, name='workflow-designs'),
    path('_workflow/designs/<uuid:identifier>/', workflow_drafts.detail, name='workflow-design'),
    path('_workflow/designs/<uuid:identifier>/share/', workflow_drafts.share, name='workflow-design-share'),
    path('_workflow/shared/', workflow_drafts.shared, name='workflow-shared'),
    re_path(r'^(?:(?:tool|t)/)?(?:biotools:)?(?P<identifier>[A-Za-z0-9.~_-]{1,100})/?$',
            tool_detail.detail, name='canonical-detail'),
]

handler404 = html.page_not_found
handler500 = html.server_error
