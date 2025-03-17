from django.contrib import admin


from .models import Resource

class ResourceAdmin(admin.ModelAdmin):
    pass

admin.site.register(Resource, ResourceAdmin)


# from django.contrib import messages
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from django.contrib.auth.models import User
# from django.contrib.admin.helpers import ActionForm
# from django import forms
# from elasticsearch import Elasticsearch
# from .models import *
# from .serializers import *
# from django.contrib.admin.views.decorators import staff_member_required
# from django.conf.urls import patterns, include, url
# from django.http import HttpResponseRedirect
# from django.contrib.admin import TabularInline, StackedInline, site
# from super_inlines.admin import SuperInlineModelAdmin, SuperModelAdmin
# from django.db.models import Q
# from pprint import pprint
# from django.conf import settings
# from django.core import urlresolvers
# from django.forms import TextInput, Textarea
# from models import Workflow, WorkflowAnnotation


# # Elastic connection
# es = Elasticsearch(settings.ELASTIC_SEARCH_URLS)

# admin.site.register(Workflow)
# admin.site.register(WorkflowAnnotation)

# # alter types and sizes of text areas
# class SuperModelAdmin(SuperModelAdmin):
# 	formfield_overrides = {
# 		models.CharField: {'widget': TextInput(attrs={'size':'50'})},
# 		models.TextField: {'widget': TextInput(attrs={'size':'50'})},
# 	}

# # alter types and sizes of text areas
# class StackedInline(StackedInline):
# 	formfield_overrides = {
# 		models.CharField: {'widget': TextInput(attrs={'size':'50'})},
# 		models.TextField: {'widget': TextInput(attrs={'size':'50'})},
# 	}

# # class UserProfileInline(admin.StackedInline):
# # 	model = UserProfile
# # 	can_delete = False

# # class UserAdmin(BaseUserAdmin):
# # 	inlines = (UserProfileInline, )

# # admin.site.unregister(User)
# # admin.site.register(User, UserAdmin)

# # actions

# class UpdateTermURIForm(ActionForm):
# 	term = forms.CharField(required=False)
# 	uri = forms.CharField(required=False)

# def update_term(modeladmin, request, queryset):
# 	term = request.POST['term']
# 	queryset.update(term=term)
# 	modeladmin.message_user(request, ("Successfully updated term for %d rows") % (queryset.count(),), messages.SUCCESS)

# def update_uri(modeladmin, request, queryset):
# 	uri = request.POST['uri']
# 	queryset.update(uri=uri)
# 	modeladmin.message_user(request, ("Successfully updated uri for %d rows") % (queryset.count(),), messages.SUCCESS)

# @staff_member_required
# def es_regenerate(request):
# 	# purge
# 	try:
# 		resp = es.indices.delete(index='elixir')
# 	except ESExceptions.TransportError as TE:
# 		if TE.status_code == 404:
# 			do_nothing = True
# 		else:
# 			raise TE

# 	# recreate
# 	resourceList = Resource.objects.filter(visibility=1)
# 	for resourceItem in resourceList:
# 		resource = ResourceSerializer(resourceItem, many=False).data
# 		es.index(index='elixir', doc_type='tool', body=resource)
# 	# modeladmin.message_user(request, "Successfully regenerated Elastic", messages.SUCCESS)

# 	return HttpResponseRedirect(request.META["HTTP_REFERER"])


# update_term.short_description = 'Update term of selected rows'
# update_uri.short_description = 'Update URI of selected rows'
# es_regenerate.short_description = 'Regenerate Elastic'

# # models

# class TopicAdmin(SuperModelAdmin):
	
# 	search_fields = ['term', 'uri', 'resource__name']
# 	list_display = ['term', 'uri', 'link_to_resource']

# 	action_form = UpdateTermURIForm
# 	actions = [update_term, update_uri]

# 	def link_to_resource(self, obj):
# 		resource = Resource.objects.filter(visibility=1,id=obj.resource.id)
# 		link=urlresolvers.reverse("admin:elixir_resource_change", args=[obj.resource.id])
# 		return u'<a href="%s">%s</a>' % (link,resource[0])
# 	link_to_resource.allow_tags=True

# 	# get only visible resources
# 	def get_queryset(self, request):
# 		qs = super(TopicAdmin, self).get_queryset(request)
# 		return qs.filter(resource__visibility=1)

# 	def get_urls(self):
# 		urls = super(TopicAdmin, self).get_urls()
# 		my_urls = patterns("",
# 			url(r"^es_regenerate/$", es_regenerate)
# 		)
# 		return my_urls + urls

# admin.site.register(Topic, TopicAdmin)

# class TopicInline(SuperInlineModelAdmin, StackedInline):
# 	model = Topic
# 	can_delete = True
# 	extra = 0

# class OperationAdmin(SuperModelAdmin):
# 	search_fields = ['term', 'uri', 'function__resource__name']
# 	list_display = ['term', 'uri', 'link_to_function', 'link_to_resource']

# 	action_form = UpdateTermURIForm
# 	actions = [update_term, update_uri]

# 	def link_to_function(self, obj):
# 		link=urlresolvers.reverse("admin:elixir_function_change", args=[obj.function.id])
# 		return u'<a href="%s">%s</a>' % (link,"Link")
# 	link_to_function.allow_tags=True

# 	def link_to_resource(self, obj):
# 		resource = Resource.objects.filter(visibility=1,id=obj.function.resource.id)
# 		link=urlresolvers.reverse("admin:elixir_resource_change", args=[obj.function.resource.id])
# 		return u'<a href="%s">%s</a>' % (link,resource[0])
# 	link_to_resource.allow_tags=True

# 	# add distinct() to queryset after searching, otherwise results are somehow duplicated
# 	def get_search_results(self, request, queryset, search_term):
# 		queryset, use_distinct = super(OperationAdmin, self).get_search_results(request, queryset, search_term)
# 		queryset = queryset.distinct()
# 		return queryset, use_distinct

# 	# get only visible resources
# 	def get_queryset(self, request):
# 		qs = super(OperationAdmin, self).get_queryset(request)
# 		return qs.filter(function__resource__visibility=1)

# 	# get only visible resources
# 	def get_queryset(self, request):
# 		qs = super(OperationAdmin, self).get_queryset(request)
# 		return qs.filter(function__resource__visibility=1)

# 	def get_urls(self):
# 		urls = super(OperationAdmin, self).get_urls()
# 		my_urls = patterns("",
# 			url(r"^es_regenerate/$", es_regenerate)
# 		)
# 		return my_urls + urls

# admin.site.register(Operation, OperationAdmin)

# class OperationInline(SuperInlineModelAdmin, StackedInline):
# 	model = Operation
# 	can_delete = True
# 	extra = 0

# class DataAdmin(SuperModelAdmin):
	
# 	search_fields = ['term', 'uri', 'input__function__resource__name', 'output__function__resource__name']
# 	list_display = ['term', 'uri', 'link_to_input', 'link_to_output', 'link_to_function', "link_to_resource"]

# 	action_form = UpdateTermURIForm
# 	actions = [update_term, update_uri]

# 	def link_to_input(self, obj):
# 		input = Input.objects.get(data=obj.id)
# 		link=urlresolvers.reverse("admin:elixir_input_change", args=[input.id])
# 		return u'<a href="%s">%s</a>' % (link,"Link")
# 	link_to_input.allow_tags=True

# 	def link_to_output(self, obj):
# 		output = Output.objects.get(data=obj.id)
# 		link=urlresolvers.reverse("admin:elixir_output_change", args=[output.id])
# 		return u'<a href="%s">%s</a>' % (link,"Link")
# 	link_to_output.allow_tags=True

# 	def link_to_function(self, obj):
# 		function = Function.objects.filter(Q(input__data__id=obj.id) | Q(output__data__id=obj.id))
# 		link=urlresolvers.reverse("admin:elixir_function_change", args=[function[0].id])
# 		return u'<a href="%s">%s</a>' % (link,"Link")
# 	link_to_function.allow_tags=True

# 	def link_to_resource(self, obj):
# 		resource = Resource.objects.filter(visibility=1).filter(Q(function__input__data__id=obj.id) | Q(function__output__data__id=obj.id))
# 		link=urlresolvers.reverse("admin:elixir_resource_change", args=[resource[0].id])
# 		return u'<a href="%s">%s</a>' % (link,resource[0])
# 	link_to_resource.allow_tags=True

# 	# add distinct() to queryset after searching, otherwise results are somehow duplicated
# 	def get_search_results(self, request, queryset, search_term):
# 		queryset, use_distinct = super(DataAdmin, self).get_search_results(request, queryset, search_term)
# 		queryset = queryset.distinct()
# 		return queryset, use_distinct

# 	# get only visible resources
# 	def get_queryset(self, request):
# 		qs = super(DataAdmin, self).get_queryset(request)
# 		return qs.filter(Q(input__function__resource__visibility=1) | Q(output__function__resource__visibility=1))

# 	def get_urls(self):
# 		urls = super(DataAdmin, self).get_urls()
# 		my_urls = patterns("",
# 			url(r"^es_regenerate/$", es_regenerate)
# 		)
# 		return my_urls + urls

# admin.site.register(Data, DataAdmin)

# class DataInline(SuperInlineModelAdmin, StackedInline):
# 	model = Data
# 	can_delete = True
# 	extra = 0

# class FormatAdmin(SuperModelAdmin):
	
# 	search_fields = ['term', 'uri', 'input__function__resource__name', 'output__function__resource__name']
# 	list_display = ['term', 'uri', 'link_to_input', 'link_to_output', 'link_to_function', "link_to_resource"]

# 	action_form = UpdateTermURIForm
# 	actions = [update_term, update_uri]

# 	def link_to_input(self, obj):
# 		input = Input.objects.get(format=obj.id)
# 		link=urlresolvers.reverse("admin:elixir_input_change", args=[input.id])
# 		return u'<a href="%s">%s</a>' % (link,"Link")
# 	link_to_input.allow_tags=True

# 	def link_to_output(self, obj):
# 		output = Output.objects.get(format=obj.id)
# 		link=urlresolvers.reverse("admin:elixir_output_change", args=[output.id])
# 		return u'<a href="%s">%s</a>' % (link,"Link")
# 	link_to_output.allow_tags=True

# 	def link_to_function(self, obj):
# 		function = Function.objects.filter(Q(input__format__id=obj.id) | Q(output__format__id=obj.id))
# 		link=urlresolvers.reverse("admin:elixir_function_change", args=[function[0].id])
# 		return u'<a href="%s">%s</a>' % (link,"Link")
# 	link_to_function.allow_tags=True

# 	def link_to_resource(self, obj):
# 		resource = Resource.objects.filter(visibility=1).filter(Q(function__input__format__id=obj.id) | Q(function__output__format__id=obj.id))
# 		link=urlresolvers.reverse("admin:elixir_resource_change", args=[resource[0].id])
# 		return u'<a href="%s">%s</a>' % (link,resource[0])
# 	link_to_resource.allow_tags=True

# 	# get only visible resources, from both input and output
# 	def get_queryset(self, request):
# 		qs = super(FormatAdmin, self).get_queryset(request)
# 		return qs.filter(Q(input__function__resource__visibility=1) | Q(output__function__resource__visibility=1))

# 	def get_urls(self):
# 		urls = super(FormatAdmin, self).get_urls()
# 		my_urls = patterns("",
# 			url(r"^es_regenerate/$", es_regenerate)
# 		)
# 		return my_urls + urls

# admin.site.register(Format, FormatAdmin)

# class FormatInline(SuperInlineModelAdmin, StackedInline):
# 	model = Format
# 	can_delete = True
# 	extra = 0

# class InputAdmin(SuperModelAdmin):

# 	search_fields = ["function__operation__term", "function__resource__name"]
# 	list_display = ["link_to_function", "link_to_resource"]

# 	def link_to_function(self, obj):
# 		operations = Operation.objects.filter(function__resource__visibility=1,function=obj.function.id)
# 		functions = ""
# 		for i, e in enumerate(operations):
# 			functions += e.term
# 			if i != len(operations) - 1:
# 				functions += ", "
# 		link=urlresolvers.reverse("admin:elixir_function_change", args=[obj.function.id])
# 		return u'<a href="%s">%s</a>' % (link,functions)
# 	link_to_function.allow_tags=True

# 	def link_to_resource(self, obj):
# 		resource = Resource.objects.filter(visibility=1,id=obj.function.resource.id)
# 		link=urlresolvers.reverse("admin:elixir_resource_change", args=[obj.function.resource.id])
# 		return u'<a href="%s">%s</a>' % (link,resource[0])
# 	link_to_resource.allow_tags=True

# 	# TODO: needs to enable DataInline
# 	inlines = [FormatInline]

# 	# add distinct() to queryset after searching, otherwise results are somehow duplicated
# 	def get_search_results(self, request, queryset, search_term):
# 		queryset, use_distinct = super(InputAdmin, self).get_search_results(request, queryset, search_term)
# 		queryset = queryset.distinct()
# 		return queryset, use_distinct

# 	# get only visible resources
# 	def get_queryset(self, request):
# 		qs = super(InputAdmin, self).get_queryset(request)
# 		return qs.filter(function__resource__visibility=1)

# 	# add url for regenerating Elastic
# 	def get_urls(self):
# 		urls = super(InputAdmin, self).get_urls()
# 		my_urls = patterns("",
# 			url(r"^es_regenerate/$", es_regenerate)
# 		)
# 		return my_urls + urls

# admin.site.register(Input, InputAdmin)

# class InputInline(SuperInlineModelAdmin, StackedInline):
# 	model = Input
# 	# TODO: needs to enable DataInline
# 	inlines = [FormatInline]
# 	can_delete = True
# 	extra = 0

# class OutputAdmin(SuperModelAdmin):

# 	search_fields = ["function__operation__term", "function__resource__name"]
# 	list_display = ["link_to_function", "link_to_resource"]

# 	def link_to_function(self, obj):
# 		operations = Operation.objects.filter(function__resource__visibility=1,function=obj.function.id)
# 		functions = ""
# 		for i, e in enumerate(operations):
# 			functions += e.term
# 			if i != len(operations) - 1:
# 				functions += ", "
# 		link=urlresolvers.reverse("admin:elixir_function_change", args=[obj.function.id])
# 		return u'<a href="%s">%s</a>' % (link,functions)
# 	link_to_function.allow_tags=True

# 	def link_to_resource(self, obj):
# 		resource = Resource.objects.filter(visibility=1,id=obj.function.resource.id)
# 		link=urlresolvers.reverse("admin:elixir_resource_change", args=[obj.function.resource.id])
# 		return u'<a href="%s">%s</a>' % (link,resource[0])
# 	link_to_resource.allow_tags=True

# 	# TODO: needs to enable DataInline
# 	inlines = [FormatInline]

# 	# add distinct() to queryset after searching, otherwise results are somehow duplicated
# 	def get_search_results(self, request, queryset, search_term):
# 		queryset, use_distinct = super(OutputAdmin, self).get_search_results(request, queryset, search_term)
# 		queryset = queryset.distinct()
# 		return queryset, use_distinct

# 	# get only visible resources
# 	def get_queryset(self, request):
# 		qs = super(OutputAdmin, self).get_queryset(request)
# 		return qs.filter(function__resource__visibility=1)

# 	# add url for regenerating Elastic
# 	def get_urls(self):
# 		urls = super(OutputAdmin, self).get_urls()
# 		my_urls = patterns("",
# 			url(r"^es_regenerate/$", es_regenerate)
# 		)
# 		return my_urls + urls

# admin.site.register(Output, OutputAdmin)

# class OutputInline(SuperInlineModelAdmin, StackedInline):
# 	model = Output
# 	# TODO: needs to enable DataInline
# 	inlines = [FormatInline]
# 	can_delete = True
# 	extra = 0

# class FunctionAdmin(SuperModelAdmin):
# 	search_fields = ["comment", "operation__term", "resource__name"]
# 	list_display = ["function", "comment", "link_to_resource"]
# 	inlines = [OperationInline, InputInline, OutputInline]

# 	def function(self, obj):
# 		operations = Operation.objects.filter(function__resource__visibility=1,function=obj.id)
# 		functions = ""
# 		for i, e in enumerate(operations):
# 			functions += e.term
# 			if i != len(operations) - 1:
# 				functions += ", "
# 		return functions
# 	function.allow_tags=True

# 	def link_to_resource(self, obj):
# 		resource = Resource.objects.filter(visibility=1,id=obj.resource.id)
# 		link=urlresolvers.reverse("admin:elixir_resource_change", args=[obj.resource.id])
# 		return u'<a href="%s">%s</a>' % (link,resource[0])
# 	link_to_resource.allow_tags=True

# 	# get only visible resources
# 	def get_queryset(self, request):
# 		qs = super(FunctionAdmin, self).get_queryset(request)
# 		return qs.filter(resource__visibility=1)

# 	def get_urls(self):
# 		urls = super(FunctionAdmin, self).get_urls()
# 		my_urls = patterns("",
# 			url(r"^es_regenerate/$", es_regenerate)
# 		)
# 		return my_urls + urls

# admin.site.register(Function, FunctionAdmin)

# class FunctionInline(SuperInlineModelAdmin, StackedInline):
# 	model = Function
# 	inlines = [OperationInline, InputInline, OutputInline]
# 	can_delete = True
# 	extra = 0

# class PublicationAdmin(SuperModelAdmin):
# 	search_fields = ["pmcid", "pmid", "doi", "type", "resource__name"]
# 	list_display = ["pmcid", "pmid", "doi", "type", "link_to_resource"]
# 	# inlines = [PublicationOtherInline]

# 	def link_to_resource(self, obj):
# 		resource = Resource.objects.get(publication=obj.id)
# 		link=urlresolvers.reverse("admin:elixir_resource_change", args=[resource.id])
# 		return u'<a href="%s">%s</a>' % (link,resource)
# 	link_to_resource.allow_tags=True

# 	# get only visible resources
# 	def get_queryset(self, request):
# 		qs = super(PublicationAdmin, self).get_queryset(request)
# 		return qs.filter(resource__visibility=1)

# 	def get_urls(self):
# 		urls = super(PublicationAdmin, self).get_urls()
# 		my_urls = patterns("",
# 			url(r"^es_regenerate/$", es_regenerate)
# 		)
# 		return my_urls + urls

# admin.site.register(Publication, PublicationAdmin)

# class PublicationInline(SuperInlineModelAdmin, StackedInline):
# 	model = Publication
# 	# inlines = [PublicationOtherInline]
# 	can_delete = True
# 	extra = 0

# class ElixirInfoAdmin(SuperModelAdmin):
# 	search_fields = ["status", "node", "resource__name"]
# 	list_display = ["status", "node", "link_to_resource"]
# 	# inlines = []

# 	def link_to_resource(self, obj):
# 		resource = Resource.objects.get(elixirInfo=obj.id)
# 		link=urlresolvers.reverse("admin:elixir_resource_change", args=[resource.id])
# 		return u'<a href="%s">%s</a>' % (link,resource)
# 	link_to_resource.allow_tags=True

# 	# get only visible resources
# 	def get_queryset(self, request):
# 		qs = super(ElixirInfoAdmin, self).get_queryset(request)
# 		return qs.filter(resource__visibility=1)

# 	def get_urls(self):
# 		urls = super(ElixirInfoAdmin, self).get_urls()
# 		my_urls = patterns("",
# 			url(r"^es_regenerate/$", es_regenerate)
# 		)
# 		return my_urls + urls

# admin.site.register(ElixirInfo, ElixirInfoAdmin)

# class ElixirInfoInline(SuperInlineModelAdmin, StackedInline):
# 	model = ElixirInfo
# 	# inlines = []
# 	can_delete = True
# 	extra = 0

# class OperatingSystemAdmin(SuperModelAdmin):
# 	search_fields = ["name", "resource__name"]
# 	list_display = ["name", "link_to_resource"]
# 	# inlines = []

# 	def link_to_resource(self, obj):
# 		resource = Resource.objects.get(id=obj.resource.id)
# 		link=urlresolvers.reverse("admin:elixir_resource_change", args=[obj.resource.id])
# 		return u'<a href="%s">%s</a>' % (link,resource)
# 	link_to_resource.allow_tags=True

# 	# get only visible resources
# 	def get_queryset(self, request):
# 		qs = super(OperatingSystemAdmin, self).get_queryset(request)
# 		return qs.filter(resource__visibility=1)

# 	def get_urls(self):
# 		urls = super(OperatingSystemAdmin, self).get_urls()
# 		my_urls = patterns("",
# 			url(r"^es_regenerate/$", es_regenerate)
# 		)
# 		return my_urls + urls

# admin.site.register(OperatingSystem, OperatingSystemAdmin)

# class OperatingSystemInline(SuperInlineModelAdmin, StackedInline):
# 	model = OperatingSystem
# 	# inlines = []
# 	can_delete = True
# 	extra = 0

# class ToolTypeAdmin(SuperModelAdmin):
# 	search_fields = ["name", "resource__name"]
# 	list_display = ["name", "link_to_resource"]
# 	# inlines = []

# 	def link_to_resource(self, obj):
# 		resource = Resource.objects.get(id=obj.resource.id)
# 		link=urlresolvers.reverse("admin:elixir_resource_change", args=[obj.resource.id])
# 		return u'<a href="%s">%s</a>' % (link,resource)
# 	link_to_resource.allow_tags=True

# 	# get only visible resources
# 	def get_queryset(self, request):
# 		qs = super(ToolTypeAdmin, self).get_queryset(request)
# 		return qs.filter(resource__visibility=1)

# 	def get_urls(self):
# 		urls = super(ToolTypeAdmin, self).get_urls()
# 		my_urls = patterns("",
# 			url(r"^es_regenerate/$", es_regenerate)
# 		)
# 		return my_urls + urls

# admin.site.register(ToolType, ToolTypeAdmin)

# class ToolTypeInline(SuperInlineModelAdmin, StackedInline):
# 	model = ToolType
# 	# inlines = []
# 	can_delete = True
# 	extra = 0

# class LanguageAdmin(SuperModelAdmin):
# 	search_fields = ["name", "resource__name"]
# 	list_display = ["name", "link_to_resource"]
# 	# inlines = []

# 	def link_to_resource(self, obj):
# 		resource = Resource.objects.get(id=obj.resource.id)
# 		link=urlresolvers.reverse("admin:elixir_resource_change", args=[obj.resource.id])
# 		return u'<a href="%s">%s</a>' % (link,resource)
# 	link_to_resource.allow_tags=True

# 	# get only visible resources
# 	def get_queryset(self, request):
# 		qs = super(LanguageAdmin, self).get_queryset(request)
# 		return qs.filter(resource__visibility=1)

# 	def get_urls(self):
# 		urls = super(LanguageAdmin, self).get_urls()
# 		my_urls = patterns("",
# 			url(r"^es_regenerate/$", es_regenerate)
# 		)
# 		return my_urls + urls

# admin.site.register(Language, LanguageAdmin)

# class LanguageInline(SuperInlineModelAdmin, StackedInline):
# 	model = Language
# 	# inlines = []
# 	can_delete = True
# 	extra = 0

# # class InterfaceAdmin(SuperModelAdmin):
# # 	search_fields = ["interfaceType", "interfaceDocs", "interfaceSpecURL", "interfaceSpecFormat", "resource__name"]
# # 	list_display = ["interfaceType", "interfaceDocs", "interfaceSpecURL", "interfaceSpecFormat", "link_to_resource"]
# # 	# inlines = []

# # 	def link_to_resource(self, obj):
# # 		resource = Resource.objects.filter(visibility=1,id=obj.resource.id)
# # 		link=urlresolvers.reverse("admin:elixir_resource_change", args=[obj.resource.id])
# # 		return u'<a href="%s">%s</a>' % (link,resource[0])
# # 	link_to_resource.allow_tags=True

# # 	# get only visible resources
# # 	def get_queryset(self, request):
# # 		qs = super(InterfaceAdmin, self).get_queryset(request)
# # 		return qs.filter(resource__visibility=1)

# # 	def get_urls(self):
# # 		urls = super(InterfaceAdmin, self).get_urls()
# # 		my_urls = patterns("",
# # 			url(r"^es_regenerate/$", es_regenerate)
# # 		)
# # 		return my_urls + urls

# # admin.site.register(Interface, InterfaceAdmin)

# # class InterfaceInline(SuperInlineModelAdmin, StackedInline):
# # 	model = Interface
# # 	# inlines = []
# # 	can_delete = True
# # 	extra = 0

# class UsesAdmin(SuperModelAdmin):
# 	search_fields = ["name", "homepage", "version", "resource__name"]
# 	list_display = ["name", "homepage", "version", "link_to_resource"]
# 	# inlines = []

# 	def link_to_resource(self, obj):
# 		resource = Resource.objects.filter(visibility=1,id=obj.resource.id)
# 		link=urlresolvers.reverse("admin:elixir_resource_change", args=[obj.resource.id])
# 		return u'<a href="%s">%s</a>' % (link,resource[0])
# 	link_to_resource.allow_tags=True

# 	# get only visible resources
# 	def get_queryset(self, request):
# 		qs = super(UsesAdmin, self).get_queryset(request)
# 		return qs.filter(resource__visibility=1)

# 	def get_urls(self):
# 		urls = super(UsesAdmin, self).get_urls()
# 		my_urls = patterns("",
# 			url(r"^es_regenerate/$", es_regenerate)
# 		)
# 		return my_urls + urls

# admin.site.register(Uses, UsesAdmin)

# class UsesInline(SuperInlineModelAdmin, StackedInline):
# 	model = Uses
# 	# inlines = []
# 	can_delete = True
# 	extra = 0

# class CollectionIDAdmin(SuperModelAdmin):
# 	search_fields = ["name", "resource__name"]
# 	list_display = ["name", "link_to_resource"]
# 	# inlines = []

# 	def link_to_resource(self, obj):
# 		resource = Resource.objects.get(id=obj.resource.id)
# 		link=urlresolvers.reverse("admin:elixir_resource_change", args=[obj.resource.id])
# 		return u'<a href="%s">%s</a>' % (link,resource)
# 	link_to_resource.allow_tags=True

# 	# get only visible resources
# 	def get_queryset(self, request):
# 		qs = super(CollectionIDAdmin, self).get_queryset(request)
# 		return qs.filter(resource__visibility=1)

# 	def get_urls(self):
# 		urls = super(CollectionIDAdmin, self).get_urls()
# 		my_urls = patterns("",
# 			url(r"^es_regenerate/$", es_regenerate)
# 		)
# 		return my_urls + urls

# admin.site.register(CollectionID, CollectionIDAdmin)

# class CollectionIDInline(SuperInlineModelAdmin, StackedInline):
# 	model = CollectionID
# 	# inlines = []
# 	can_delete = True
# 	extra = 0

# class ContactAdmin(SuperModelAdmin):
# 	search_fields = ["email", "name", "tel", "url", "resource__name"]
# 	list_display = ["email", "name", "tel", "url", "link_to_resource"]
# 	# inlines = [ContactRoleInline]

# 	def link_to_resource(self, obj):
# 		resource = Resource.objects.filter(visibility=1,id=obj.resource.id)
# 		link=urlresolvers.reverse("admin:elixir_resource_change", args=[obj.resource.id])
# 		return u'<a href="%s">%s</a>' % (link,resource[0])
# 	link_to_resource.allow_tags=True

# 	# get only visible resources
# 	def get_queryset(self, request):
# 		qs = super(ContactAdmin, self).get_queryset(request)
# 		return qs.filter(resource__visibility=1)

# 	def get_urls(self):
# 		urls = super(ContactAdmin, self).get_urls()
# 		my_urls = patterns("",
# 			url(r"^es_regenerate/$", es_regenerate)
# 		)
# 		return my_urls + urls

# admin.site.register(Contact, ContactAdmin)

# class ContactInline(SuperInlineModelAdmin, StackedInline):
# 	model = Contact
# 	# inlines = [ContactRoleInline]
# 	can_delete = True
# 	extra = 0

# class ResourceAdmin(SuperModelAdmin):
# 	inlines = [TopicInline, FunctionInline, OperatingSystemInline, ToolTypeInline, LanguageInline, CollectionIDInline, UsesInline, ContactInline]
# 	search_fields = ['name']
# 	list_filter = ['additionDate', 'lastUpdate']
# 	list_display = ['textId','name', 'version', 'additionDate', 'lastUpdate']

# 	# make inlines collapsible
# 	class Media:
# 		js = ['admin/js/jquery-1.3.2.min.js', 'admin/js/collapsed_stacked_inlines.js',]

# 	# get only visible resources
# 	def get_queryset(self, request):
# 		qs = super(ResourceAdmin, self).get_queryset(request)
# 		return qs.filter(visibility=1)

# 	def get_urls(self):
# 		urls = super(ResourceAdmin, self).get_urls()
# 		my_urls = patterns("",
# 			url(r"^es_regenerate/$", es_regenerate)
# 		)
# 		return my_urls + urls

# admin.site.register(Resource, ResourceAdmin)
