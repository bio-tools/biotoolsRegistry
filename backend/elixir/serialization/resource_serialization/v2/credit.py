from rest_framework import serializers
from elixir.models import *
from elixir.validators import *


class LegacyCreditSerializer(serializers.ModelSerializer):
	# TODO: make name validate as a token, i.e. no newline, no leading or trailing spaces, no duplicate spaces, no tabs, xml token
	name = serializers.CharField(allow_blank=False, max_length=100, min_length=1, validators=[IsStringTypeValidator], required=True)
	# name = CreditNameSerializer(many=True, required=True, allow_empty=False)
	url = serializers.CharField(allow_blank=False, validators=[IsURLValidator], required=False)
	email = serializers.CharField(allow_blank=False, max_length=300, validators=[IsStringTypeValidator, IsEmailValidator], required=False)
	orcidId = serializers.CharField(allow_blank=False, validators=[IsStringTypeValidator], required=False, source="orcidid")
	typeEntity = serializers.CharField(allow_blank=False, required=False)
	typeRole = serializers.SerializerMethodField()
	# TODO tel should be a token
	#tel = serializers.CharField(allow_blank=False, min_length=5, max_length=50, validators=[IsStringTypeValidator], required=False)
	comment = serializers.CharField(allow_blank=False, min_length=10, max_length=1000, validators=[IsStringTypeValidator], required=False, source='note')

	class Meta:
		model = Credit
		fields = ('name', 'url', 'email', 'orcidId', 'typeEntity', 'typeRole', 'comment')

	def validate_typeEntity(self, attrs):
		enum = ENUMValidator([u'Person', u'Project', u'Division', u'Institute', u'Consortium', u'Funding agency'])
		attrs = enum(attrs)
		return attrs


	def validate_orcidid(self, attrs):
		p = re.compile('^http://orcid.org/[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{4}$', re.IGNORECASE | re.UNICODE)
		if not p.search(attrs):
			raise serializers.ValidationError('This field can only contain an Orcid ID')
		return attrs

	def validate_elixirPlatform(self, attrs):
		enum = ENUMValidator([u'Data', u'Tools', u'Compute', u'Interoperability', u'Training'])
		attrs = enum(attrs)
		return attrs

	def validate_elixirNode(self, attrs):
		enum = ENUMValidator([u'Belgium', u'Czech Republic', u'Denmark', u'EMBL', u'Estonia', u'Finland', u'France', u'Germany', u'Greece', u'Hungary', u'Ireland', u'Israel', u'Italy', u'Luxembourg', u'Netherlands', u'Norway', u'Portugal', u'Slovenia', u'Spain', u'Sweden', u'Switzerland', u'UK'])
		attrs = enum(attrs)
		return attrs

	def get_typeRole(self, obj):
 		typeRole = obj.typeRole.all()[0].typeRole
 		if typeRole:
 			return typeRole
 		return ''

	def get_pk_field(self, model_field):
		return None