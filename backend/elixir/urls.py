# patterns is no longer supported, to achieve the same effect use re_path
from django.conf.urls import url,re_path # patterns
from django.conf.urls.static import static
from django.views.static import serve
from django.conf import settings
from rest_framework.urlpatterns import format_suffix_patterns
from elixir import views, sitemap
from elixir import edit_permissions

urlpatterns = [
	url(r'^user-list/?$', views.UserList.as_view()),
	url(r'^edit-permissions/?$', edit_permissions.EditPermissions.as_view()),
	url(r'^edit-permissions/(?P<pk>[0-9]+)/?$', edit_permissions.EditPermissions.as_view()),
	url(r'^t(ool)?/?$', views.ResourceList.as_view()),
	url(r'^t(ool)?/validate/?$', views.ResourceCreateValidator.as_view()),
	url(r'^t(ool)?/(biotools\:)?(?P<biotoolsID>[a-zA-Z0-9.~_-]+)/?$', views.ResourceDetail.as_view()),
	url(r'^t(ool)?/(biotools\:)?(?P<biotoolsID>[a-zA-Z0-9.~_-]+)/validate/?$', views.ResourceUpdateValidator.as_view()),
	# url(r'^t(ool)?/(biotools\:)?(?P<biotoolsID>[a-zA-Z0-9.~_-]+)/i(ssues)?/(?P<issueId>[a-zA-Z0-9.~_-]+)?$', views.IssueView.as_view()),
	url(r'^t(ool)?/(biotools\:)?(?P<biotoolsID>[a-zA-Z0-9.~_-]+)/disown/?$', views.DisownResourceView.as_view()),
	url(r'^f(unction)?/?$', views.FunctionList.as_view()),
	url(r'^o(ntology)?/(?P<name>[a-zA-Z0-9.~_-]+)/?$', views.OntologyDetail.as_view()),
	url(r'^used-terms/(?P<ontology>[a-zA-Z0-9.~_-]+)/?$', views.UsedTermsList.as_view()),
	url(r'^stats/?$', views.Stats.as_view()),
	url(r'^stats/total-entries/?$', views.TotalEntriesStats.as_view()),
	url(r'^stats/annotation-count/?$', views.AnnotationCountStats.as_view()),
	url(r'^stats/users/?$', views.UserStats.as_view()),
	url(r'^env/?$', views.Environment.as_view()),
	url(r'^sitemap.xml$', sitemap.Sitemap.as_view()),
	url(r'^d(omain)?/?$', views.DomainView.as_view()),
	url(r'^d(omain)?/(?P<domain>[a-zA-Z0-9.~_-]+)/?$', views.DomainResourceView.as_view()),
	url(r'^request/?$', views.ResourceRequestView.as_view()),
	url(r'^request/conclude/?$', views.ProcessResourceRequest.as_view()),
	url(r'^tool-list/?$', views.ToolList.as_view()),
	url(r'^w/?$', views.WorkflowView.as_view()),
	url(r'^w/(?P<id>[a-zA-Z0-9.~_-]+)/?$', views.WorkflowDetailView.as_view()),
	url(r'^(biotools\:)?(?P<biotoolsID>[a-zA-Z0-9.~_-]+)/?$', views.ResourceDetail.as_view()),
	url(r'^(biotools\:)?(?P<biotoolsID>[a-zA-Z0-9.~_-]+)/validate/?$', views.ResourceUpdateValidator.as_view()),
	# url(r'^(biotools\:)?(?P<biotoolsID>[a-zA-Z0-9.~_-]+)/i(ssues)?/(?P<issueId>[a-zA-Z0-9.~_-]+)?$', views.IssueView.as_view()),
	url(r'^(biotools\:)?(?P<biotoolsID>[a-zA-Z0-9.~_-]+)/disown/?$', views.DisownResourceView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# urlpatterns += patterns('',
# 	(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
# 		'document_root': settings.MEDIA_ROOT}))


urlpatterns += [
		re_path(r'^media/(?P<path>.*)$', serve, {
			'document_root': settings.MEDIA_ROOT
		})
]