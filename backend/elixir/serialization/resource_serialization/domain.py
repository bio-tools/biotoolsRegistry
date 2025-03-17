from rest_framework import serializers
from elixir.models import Domain, DomainResource, DomainTag, DomainCollection, Resource
from elixir.validators import *
from rest_framework.validators import UniqueValidator
from orderedset import OrderedSet
from django.http import Http404




# just get the names and the id's
class SubdomainNameSerializer(serializers.ModelSerializer):
	resourcesCount = serializers.SerializerMethodField()

	class Meta:
		model = Domain
		fields = ('name', 'resourcesCount')

	def get_resourcesCount(self, obj):
		return obj.resource.count()


class DomainResourceSerializer(serializers.ModelSerializer):
	name = serializers.CharField(min_length=1, max_length=100, allow_blank=False, required=False, validators=[IsStringTypeValidator])
	biotoolsID = serializers.CharField(min_length=1, max_length=100, allow_blank=False, required=True, validators=[IsStringTypeValidator])	
	
	
	class Meta:
		model = DomainResource
		fields = ('name', 'biotoolsID')

	def validate_biotoolsID(self, b_id):
		return b_id.lower()


class DomainTagSerializer(serializers.ModelSerializer):
	name = serializers.CharField(min_length=1, max_length=50, allow_blank=False, validators=[IsStringTypeValidator])

	class Meta:
		model = DomainTag
		fields = ('name',)

	def get_pk_field(self, model_field):
		return None

	def to_representation(self, obj):
		return obj.name

	def to_internal_value(self, data):
		# checking if blank
		IsNotBlankValidator(data)
		# check if length is not exceeded
		length = LengthValidator(50)
		length(data)
		return {'name': data}

class DomainCollectionSerializer(serializers.ModelSerializer):
	name = serializers.CharField(min_length=1, max_length=50, allow_blank=False, validators=[IsStringTypeValidator])

	class Meta:
		model = DomainCollection
		fields = ('name',)

	def get_pk_field(self, model_field):
		return None

	def to_representation(self, obj):
		return obj.name

	def to_internal_value(self, data):
		# checking if blank
		IsNotBlankValidator(data)
		# check if length is not exceeded
		length = LengthValidator(50)
		length(data)
		return {'name': data}

class DomainSerializer(serializers.ModelSerializer):
	domain = serializers.CharField(source='name',min_length=2, max_length=50, allow_blank=False, allow_null=False, required=True,
		validators=[IsStringTypeValidator, UniqueValidator(queryset=Domain.objects.filter(visibility=1), message="A domain with this name already exists. Choose a different domain name")]
	)
	title = serializers.CharField(max_length=50, allow_blank=True, required=False, allow_null=True)
	sub_title = serializers.CharField(max_length=150, allow_blank=True, required=False, allow_null=True)
	description = serializers.CharField(allow_blank=True, required=False, allow_null=True)
	is_private = serializers.BooleanField(default=True)
	resources = DomainResourceSerializer(source='resource', many=True, required=False, allow_empty=True, allow_null=False)
	tag = DomainTagSerializer(many=True, required=False, allow_empty=True, allow_null=False)
	collection = DomainCollectionSerializer(many=True, required=False, allow_empty=True, allow_null=False)

	class Meta:
		model = Domain
		fields = ('domain', 'title', 'sub_title', 'description', 'is_private', 'tag', 'collection', 'resources', )

	def get_domain(self, obj):
		return obj.domain.lower()

	def validate_domain(self, domain_name):
		if self.context['request_type'] in ['POST', 'PUT', 'DELETE'] and domain_name.strip().lower() == 'all':
			raise serializers.ValidationError('Domain name not allowed')
		
		# If the domain doesn't exist you can't update it or delete it
		if self.context['request_type'] in ['PUT', 'DELETE']:
			try:
				Domain.objects.get(name=domain_name, visibility = 1)
			except Domain.DoesNotExist:
				raise Http404


		p = re.compile('^[a-zA-Z0-9-]{2,40}$', re.IGNORECASE | re.UNICODE)

		if not p.search(domain_name):
			raise serializers.ValidationError('Domain name can only contain alphanumeric characters and dashes, with length between 2 and 40 characters.')

		return domain_name.lower()



	def validate(self, data):
		return data

	def create(self, validated_data):
		pop = lambda l, k: l.pop(k) if k in list(l.keys()) else []
		uniq = lambda l, k: [dict(t) for t in OrderedSet([tuple(d.items()) for d in pop(l, k)])]

		# domain resource unique list
		resources_list = pop(validated_data, 'resource') if 'resource' in list(validated_data.keys()) else []
		seen = set()
		resources_list = [seen.add(obj['biotoolsID']) or obj for obj in resources_list if obj['biotoolsID'] not in seen]


		# domain tags unique list
		tag_list = uniq(validated_data, 'tag')
		
		# domain collection unique list
		collection_list = uniq(validated_data, 'collection')

		domain = Domain.objects.create(**validated_data)

		for r in resources_list:
			tool_r = Resource.objects.filter(visibility=1, biotoolsID = r['biotoolsID'])
			if len(tool_r) == 1:
				r['name'] = tool_r[0].name
				DomainResource.objects.create(domain=domain, **r)

		for tag in tag_list:
			DomainTag.objects.create(domain=domain, **tag)

		for collection in collection_list:
			DomainCollection.objects.create(domain=domain, **collection)

		return domain


# Need this class to bypass the unique constraint on domain names enforced when POST ing
class DomainUpdateSerializer(DomainSerializer):
	domain = serializers.CharField(source='name',min_length=2, max_length=50, allow_blank=False, allow_null=False, required=True,
		validators=[IsStringTypeValidator]
	)