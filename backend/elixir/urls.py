# patterns is no longer supported, to achieve the same effect use re_path
from django.urls import re_path
from django.urls import re_path # patterns
from django.conf.urls.static import static
from django.views.static import serve
from django.conf import settings
from rest_framework.urlpatterns import format_suffix_patterns
from elixir import views, sitemap
from elixir import edit_permissions

urlpatterns = [
	re_path(r'^user-list/?$', views.UserList.as_view()),
	re_path(r'^edit-permissions/?$', edit_permissions.EditPermissions.as_view()),
	re_path(r'^edit-permissions/(?P<pk>[0-9]+)/?$', edit_permissions.EditPermissions.as_view()),
	re_path(r'^matrix/$', views.ToolMatrix.as_view()),
	re_path(r'^t(ool)?/?$', views.ResourceList.as_view()),
	re_path(r'^t(ool)?/validate/?$', views.ResourceCreateValidator.as_view()),
	re_path(r'^t(ool)?/(biotools\:)?(?P<biotoolsID>[a-zA-Z0-9.~_-]+)/?$', views.ResourceDetail.as_view()),
	re_path(r'^t(ool)?/(biotools\:)?(?P<biotoolsID>[a-zA-Z0-9.~_-]+)/validate/?$', views.ResourceUpdateValidator.as_view()),
	# url(r'^t(ool)?/(biotools\:)?(?P<biotoolsID>[a-zA-Z0-9.~_-]+)/i(ssues)?/(?P<issueId>[a-zA-Z0-9.~_-]+)?$', views.IssueView.as_view()),
	re_path(r'^t(ool)?/(biotools\:)?(?P<biotoolsID>[a-zA-Z0-9.~_-]+)/disown/?$', views.DisownResourceView.as_view()),
	re_path(r'^f(unction)?/?$', views.FunctionList.as_view()),
	re_path(r'^o(ntology)?/(?P<name>[a-zA-Z0-9.~_-]+)/?$', views.OntologyDetail.as_view()),
	re_path(r'^used-terms/(?P<ontology>[a-zA-Z0-9.~_-]+)/?$', views.UsedTermsList.as_view()),
	re_path(r'^stats/?$', views.Stats.as_view()),
	re_path(r'^stats/total-entries/?$', views.TotalEntriesStats.as_view()),
	re_path(r'^stats/annotation-count/?$', views.AnnotationCountStats.as_view()),
	re_path(r'^stats/users/?$', views.UserStats.as_view()),
	re_path(r'^env/?$', views.Environment.as_view()),
	re_path(r'^sitemap.xml$', sitemap.Sitemap.as_view()),
	re_path(r'^d(omain)?/?$', views.DomainView.as_view()),
	re_path(r'^d(omain)?/(?P<domain>[a-zA-Z0-9.~_-]+)/?$', views.DomainResourceView.as_view()),
	re_path(r'^request/?$', views.ResourceRequestView.as_view()),
	re_path(r'^request/conclude/?$', views.ProcessResourceRequest.as_view()),
	re_path(r'^tool-list/?$', views.ToolList.as_view()),
	re_path(r'^w/?$', views.WorkflowView.as_view()),
	re_path(r'^w/(?P<id>[a-zA-Z0-9.~_-]+)/?$', views.WorkflowDetailView.as_view()),
	re_path(r'^(biotools\:)?(?P<biotoolsID>[a-zA-Z0-9.~_-]+)/?$', views.ResourceDetail.as_view()),
	re_path(r'^(biotools\:)?(?P<biotoolsID>[a-zA-Z0-9.~_-]+)/validate/?$', views.ResourceUpdateValidator.as_view()),
	# url(r'^(biotools\:)?(?P<biotoolsID>[a-zA-Z0-9.~_-]+)/i(ssues)?/(?P<issueId>[a-zA-Z0-9.~_-]+)?$', views.IssueView.as_view()),
	re_path(r'^(biotools\:)?(?P<biotoolsID>[a-zA-Z0-9.~_-]+)/disown/?$', views.DisownResourceView.as_view()),
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