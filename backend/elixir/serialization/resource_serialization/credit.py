from rest_framework import serializers
from elixir.models import *
from elixir.validators import *


# class CreditNameSerializer(serializers.ModelSerializer):
# 	name = serializers.CharField(allow_blank=False, max_length=300, min_length=1, validators=[IsStringTypeValidator], required=False)

# 	class Meta:
# 		model = CreditName
# 		fields = ('name',)

# 	def get_pk_field(self, model_field):
# 		return None

# 	def to_representation(self, obj):
# 		return obj.name

# 	# TODO: fix this
# 	# need to add validation here since this method overrides all validation
# 	def to_internal_value(self, data):
# 		# checking if blank
# 		IsNotBlankValidator(data)
# 		# checking if within enum
# 		enum = ENUMValidator([u'Open access', u'Restricted access', u'Proprietary', u'Freeware'])
# 		data = enum(data)
# 		return {'name': data}


# TODO: make sure this works
# TODO: when migrating contacts, make them all have type role primary contact
# TODO: it's a choice of either elixirplatform OR elixirnode OR the rest
# but you can always have a comment

class CreditTypeRoleSerializer(serializers.ModelSerializer):
	typeRole = serializers.CharField(allow_blank=False, required=False)

	class Meta:
		model = CreditTypeRole
		fields = ('typeRole',)

	# def validate_typeRole(self, attrs):
	# 	enum = ENUMValidator([u'Developer', u'Maintainer', u'Provider', u'Documentor', u'Contributor', u'Support', u'Primary contact'])
	# 	attrs = enum(attrs)
	# 	return attrs

	def get_pk_field(self, model_field):
 		return None

	def to_representation(self, obj):
		return obj.typeRole

	def to_internal_value(self, data):
		# checking if blank
		IsNotBlankValidator(data)
		# checking if within enum
		enum = ENUMValidator(['Developer', 'Maintainer', 'Provider', 'Documentor', 'Contributor', 'Support', 'Primary contact'])
		data = enum(data)
		return {'typeRole': data}

class CreditSerializer(serializers.ModelSerializer):
	# TODO: make name validate as a token, i.e. no newline, no leading or trailing spaces, no duplicate spaces, no tabs, xml token
	name = serializers.CharField(allow_blank=False, max_length=100, min_length=1, validators=[IsStringTypeValidator], required=False)
	# name = CreditNameSerializer(many=True, required=True, allow_empty=False)
	url = serializers.CharField(allow_blank=False, validators=[IsURLValidator], required=False)
	email = serializers.CharField(allow_blank=False, max_length=300, validators=[IsStringTypeValidator, IsEmailValidator], required=False)
	orcidid = serializers.CharField(allow_blank=False, validators=[IsStringTypeValidator], required=False)
	gridid = serializers.CharField(allow_blank=False, validators=[IsStringTypeValidator], required=False)
	rorid = serializers.CharField(allow_blank=False, validators=[IsStringTypeValidator], required=False)
	fundrefid = serializers.CharField(allow_blank=False, validators=[IsStringTypeValidator], required=False)
	typeEntity = serializers.CharField(allow_blank=False, required=False)
	# TODO: now there can be several typeRoles
	#typeRole = serializers.CharField(allow_blank=False, required=False)
	typeRole = CreditTypeRoleSerializer(many=True, required=False, allow_empty=False)

	# TODO tel should be a token
	#tel = serializers.CharField(allow_blank=False, min_length=5, max_length=50, validators=[IsStringTypeValidator], required=False)
	note = serializers.CharField(allow_blank=False, min_length=10, max_length=1000, validators=[IsStringTypeValidator], required=False)

	class Meta:
		model = Credit
		fields = ('name', 'email', 'url', 'orcidid', 'gridid', 'rorid', 'fundrefid','typeEntity', 'typeRole', 'note')

	def validate_typeEntity(self, attrs):
		enum = ENUMValidator(['Person', 'Project', 'Division', 'Institute', 'Consortium', 'Funding agency'])
		attrs = enum(attrs)
		return attrs


	def validate_orcidid(self, attrs):
		p = re.compile('^https?://orcid.org/[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$', re.IGNORECASE | re.UNICODE)
		if not p.search(attrs):
			raise serializers.ValidationError('This field can only contain a valid ORCID ID')
		return attrs

	def validate(self, data):
		if data.get("name") == None and data.get("url") == None and data.get("email") == None:
			raise serializers.ValidationError('At least one of credit name, credit email or credit URL is mandatory.')
		return data

	# TODO in the user interface, wherever there is a regex we should give an example of what is expected
	def validate_gridid(self, attrs):
		p = re.compile('^grid.[0-9]{4,}.[a-f0-9]{1,2}$', re.IGNORECASE | re.UNICODE)
		if not p.search(attrs):
			raise serializers.ValidationError('This field can only contain a valid GRID ID')
		return attrs

	def validate_rorid(self, attrs):
		p = re.compile('^0[0-9a-zA-Z]{6}[0-9]{2}$', re.IGNORECASE | re.UNICODE)
		if not p.search(attrs):
			raise serializers.ValidationError('This field can only contain a valid ROR ID')
		return attrs
	
	def validate_fundrefid(self, attrs):
		p = re.compile('^10\.13039\/[-\.\[\]<>_;\(\)\/:a-zA-Z0-9]+$', re.IGNORECASE | re.UNICODE)
		if not p.search(attrs):
			raise serializers.ValidationError('This field can only contain a valid FundRef ID')
		return attrs

# TODO: in validate make this either elixirInfo or other info


	def get_pk_field(self, model_field):
		return None