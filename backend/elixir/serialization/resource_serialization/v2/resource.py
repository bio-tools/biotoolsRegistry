from rest_framework import serializers
from elixir.models import *
from elixir.validators import *
from django.conf import settings
from rest_framework.pagination import PageNumberPagination
from elixir.serialization.resource_serialization.domain import *
from elixir.serialization.resource_serialization.edam import *
from elixir.serialization.resource_serialization.operatingSystem import *
from elixir.serialization.resource_serialization.toolType import *
from elixir.serialization.resource_serialization.language import *
from elixir.serialization.resource_serialization.accessibility import *
from elixir.serialization.resource_serialization.publication import *
from elixir.serialization.resource_serialization.v2.credit import *
from elixir.serialization.resource_serialization.v2.link import *
from elixir.serialization.resource_serialization.v2.download import *
from elixir.serialization.resource_serialization.v2.documentation import *
from elixir.serialization.resource_serialization.collection import *
from elixir.serialization.resource_serialization.contact import *
from elixir.serialization.resource_serialization.v2.edam import *
from elixir.issues import EDAMTopicIssue, EDAMOperationIssue, EDAMDataIssue, EDAMFormatIssue, NoLicenseIssue, NoContactIssue, NoTOSIssue
from random import randint
from rest_framework.validators import UniqueValidator


class LegacyResourceSerializer(serializers.ModelSerializer):

	# instead of the id we use biotoolsID to identify the resources from the user point of view
	lookup_field = 'biotoolsID'

	# # need an alias so input has 'id' which is saved in the 'biotoolsID' field
	# id = serializers.CharField(read_only=True, source="biotoolsID");
	# id = serializers.CharField(allow_blank=False, max_length=50, min_length=1, source="biotoolsID", validators=[UniqueValidator(queryset=Resource.objects.filter(visibility=1), message="A resource with this ID already exists.")]);

	# get the owner username from the auth_user table
	owner = serializers.SlugRelatedField(read_only=True, slug_field='username')
	# alias for 'was_id_validated'
	validated = serializers.IntegerField(read_only=True, source='was_id_validated')

	#biotoolsID = serializers.CharField(allow_blank=False, validators=[UniqueValidator(queryset=Resource.objects.filter(visibility=1), message="A resource with this ID already exists.")])
	#biotoolsCURIE = serializers.CharField(allow_blank=False, validators=[UniqueValidator(queryset=Resource.objects.filter(visibility=1), message="A resource with this ID already exists.")])
	id = serializers.CharField(read_only=True, source='biotoolsID')


	name = serializers.CharField(min_length=1, max_length=100, allow_blank=False, validators=[IsStringTypeValidator, UniqueValidator(queryset=Resource.objects.filter(visibility=1), message="A resource with this name already exists.")])
	homepage = serializers.CharField(max_length=300, min_length=1, allow_blank=False)

	homepage_status = serializers.IntegerField(read_only=True)
	cost = serializers.CharField(allow_blank=False, max_length=300, min_length=1, required=False)
	maturity = serializers.CharField(allow_blank=False, max_length=300, min_length=1, required=False)
	license = serializers.CharField(allow_blank=False, max_length=300, min_length=1, required=False)
	# accessibility = serializers.CharField(allow_blank=True, max_length=300, min_length=1, required=False, validators=[IsNotBlankValidator])
	# Version this needs to be 0 to many
	
	version = serializers.SerializerMethodField()#LegacyVersionSerializer(many=True, required=False, allow_empty=False)
	#version = serializers.CharField(max_length=100, allow_blank=True, validators=[IsStringTypeValidator], required=False, default=None)
	#otherID = OtherIDSerializer(many=True, required=False, allow_empty=False)
	canonicalID = serializers.CharField(max_length=50, allow_blank=True, validators=[IsStringTypeValidator], required=False)
	description = serializers.CharField(min_length=10, max_length=500, allow_blank=False, validators=[IsStringTypeValidator], required=True)
	#short_description = serializers.CharField(min_length=10, max_length=100, allow_blank=False, validators=[IsStringTypeValidator], required=False)

	# nested attributes
	topic = TopicSerialiser(many=True, required=False, allow_empty=False, error_messages={'empty': 'This list may not be empty.'})
	function = LegacyFunctionSerializer(many=True, required=False, allow_empty=False)
	credit = LegacyCreditSerializer(many=True, required=False, allow_empty=False)
	# elixirInfo = ElixirInfoSerializer(many=False, required=False)
	link = LegacyLinkSerializer(many=True, required=False, allow_empty=False)
	documentation = LegacyDocumentationSerializer(many=True, required=False, allow_empty=False)
	download = LegacyDownloadSerializer(many=True, required=False, allow_empty=False)
	operatingSystem = OperatingSystemSerializer(many=True, required=False, allow_empty=False)
	toolType = ToolTypeSerializer(many=True, required=False, allow_empty=False)
	language = LanguageSerializer(many=True, required=False, allow_empty=False)
	accessibility = AccessibilitySerializer(many=True, required=False, allow_empty=False)
	publication = PublicationSerializer(many=True, required=False, allow_empty=False)

	# uses = UsesSerializer(many=True, required=False, allow_empty=False)
	collectionID = CollectionIDSerializer(many=True, required=False, allow_empty=False)
	# contact = ContactSerializer(many=True, required=False, allow_empty=False)
	editPermission = EditPermissionSerializer(many=False, required=False)

	class Meta:
		model = Resource
		fields = (
			'id',
			'name',
			'topic',
			'function',
			'version',
			'homepage',
			'description',
			'canonicalID',
			'accessibility',
			'additionDate',
			'lastUpdate',
			'availability',
			'downtime',
			'cost',
			'maturity',
			'credit',
			'link',
			'download',
			'license',
			'operatingSystem',
			'toolType',
			'language',
			'documentation',
			'publication',
			'collectionID',
			#'contact',
			'otherID',
			'owner',
			'editPermission',
			'validated',
			'homepage_status'
		)
		validators = [

		]

 	def get_version(self, obj):
 		versions = obj.version.all()
 		if len(versions) > 0:
 			version = versions[0].version
	 		if version:
 				return version
 		return None

	def validate_name(self, attrs):
		# make sure the name matches the regular expression
		# TODO: make name unique

		# this looks wrong
		#p = re.compile('^[\p{Zs}A-Za-z0-9+\.,\-_:;()]*$', re.IGNORECASE | re.UNICODE)

		#use this
		p = re.compile('^[ A-Za-z0-9+\.,\-_:;()]*$', re.IGNORECASE | re.UNICODE)
		if not p.search(attrs):
			raise serializers.ValidationError('This field can only contain letters, numbers, spaces or these characters: + . , - _ : ; ( )')
		return attrs

	def validate_homepage(self, attrs):
		attrs = IsURLValidator(attrs)
		return attrs

	def validate_cost(self, attrs):
		enum = ENUMValidator([u'Free of charge', u'Free of charge (with restrictions)', u'Commercial'])
		attrs = enum(attrs)
		return attrs

	def validate_maturity(self, attrs):
		enum = ENUMValidator([u'Emerging', u'Mature', u'Legacy'])
		attrs = enum(attrs)
		return attrs

	# def validate_accessibility(self, attrs):
	# 	enum = ENUMValidator([u'Open access', u'Restricted access', u'Proprietary', u'Freeware'])
	# 	attrs = enum(attrs)
	# 	return attrs

	def validate_license(self, attrs):
		enum = ENUMValidator([u'0BSD', u'AAL', u'ADSL', u'AFL-1.1', u'AFL-1.2', u'AFL-2.0', u'AFL-2.1', u'AFL-3.0', u'AGPL-1.0', u'AGPL-3.0', u'AMDPLPA', u'AML', u'AMPAS', u'ANTLR-PD', u'APAFML', u'APL-1.0', u'APSL-1.0', u'APSL-1.1', u'APSL-1.2', u'APSL-2.0', u'Abstyles', u'Adobe-2006', u'Adobe-Glyph', u'Afmparse', u'Aladdin', u'Apache-1.0', u'Apache-1.1', u'Apache-2.0', u'Artistic-1.0', u'Artistic-1.0-Perl', u'Artistic-1.0-cl8', u'Artistic-2.0', u'BSD-2-Clause', u'BSD-2-Clause-FreeBSD', u'BSD-2-Clause-NetBSD', u'BSD-3-Clause', u'BSD-3-Clause-Attribution', u'BSD-3-Clause-Clear', u'BSD-3-Clause-LBNL', u'BSD-3-Clause-No-Nuclear-License', u'BSD-3-Clause-No-Nuclear-License-2014', u'BSD-3-Clause-No-Nuclear-Warranty', u'BSD-4-Clause', u'BSD-4-Clause-UC', u'BSD-Protection', u'BSD-Source-Code', u'BSL-1.0', u'Bahyph', u'Barr', u'Beerware', u'BitTorrent-1.0', u'BitTorrent-1.1', u'Borceux', u'CATOSL-1.1', u'CC-BY-1.0', u'CC-BY-2.0', u'CC-BY-2.5', u'CC-BY-3.0', u'CC-BY-4.0', u'CC-BY-NC-1.0', u'CC-BY-NC-2.0', u'CC-BY-NC-2.5', u'CC-BY-NC-3.0', u'CC-BY-NC-4.0', u'CC-BY-NC-ND-1.0', u'CC-BY-NC-ND-2.0', u'CC-BY-NC-ND-2.5', u'CC-BY-NC-ND-3.0', u'CC-BY-NC-ND-4.0', u'CC-BY-NC-SA-1.0', u'CC-BY-NC-SA-2.0', u'CC-BY-NC-SA-2.5', u'CC-BY-NC-SA-3.0', u'CC-BY-NC-SA-4.0', u'CC-BY-ND-1.0', u'CC-BY-ND-2.0', u'CC-BY-ND-2.5', u'CC-BY-ND-3.0', u'CC-BY-ND-4.0', u'CC-BY-SA-1.0', u'CC-BY-SA-2.0', u'CC-BY-SA-2.5', u'CC-BY-SA-3.0', u'CC-BY-SA-4.0', u'CC0-1.0', u'CDDL-1.0', u'CDDL-1.1', u'CECILL-1.0', u'CECILL-1.1', u'CECILL-2.0', u'CECILL-2.1', u'CECILL-B', u'CECILL-C', u'CNRI-Jython', u'CNRI-Python', u'CNRI-Python-GPL-Compatible', u'CPAL-1.0', u'CPL-1.0', u'CPOL-1.02', u'CUA-OPL-1.0', u'Caldera', u'ClArtistic', u'Condor-1.1', u'Crossword', u'CrystalStacker', u'Cube', u'D-FSL-1.0', u'DOC', u'DSDP', u'Dotseqn', u'ECL-1.0', u'ECL-2.0', u'EFL-1.0', u'EFL-2.0', u'EPL-1.0', u'EUDatagrid', u'EUPL-1.0', u'EUPL-1.1', u'Entessa', u'ErlPL-1.1', u'Eurosym', u'FSFAP', u'FSFUL', u'FSFULLR', u'FTL', u'Fair', u'Frameworx-1.0', u'FreeImage', u'GFDL-1.1', u'GFDL-1.2', u'GFDL-1.3', u'GL2PS', u'GPL-1.0', u'GPL-2.0', u'GPL-3.0', u'Giftware', u'Glide', u'Glulxe', u'HPND', u'HaskellReport', u'IBM-pibs', u'ICU', u'ICU', u'IJG', u'IPA', u'IPL-1.0', u'ISC', u'ImageMagick', u'Imlib2', u'Info-ZIP', u'Intel', u'Intel-ACPI', u'Interbase-1.0', u'JSON', u'JasPer-2.0', u'LAL-1.2', u'LAL-1.3', u'LGPL-2.0', u'LGPL-2.1', u'LGPL-3.0', u'LGPLLR', u'LPL-1.0', u'LPL-1.02', u'LPPL-1.0', u'LPPL-1.1', u'LPPL-1.2', u'LPPL-1.3a', u'LPPL-1.3c', u'Latex2e', u'Leptonica', u'LiLiQ-P-1.1', u'LiLiQ-R-1.1', u'LiLiQ-Rplus-1.1', u'Libpng', u'MIT', u'MIT-CMU', u'MIT-advertising', u'MIT-enna', u'MIT-feh', u'MITNFA', u'MPL-1.0', u'MPL-1.1', u'MPL-2.0', u'MPL-2.0-no-copyleft-exception', u'MS-PL', u'MS-RL', u'MTLL', u'MakeIndex', u'MirOS', u'Motosoto', u'Multics', u'Mup', u'NASA-1.3', u'NBPL-1.0', u'NCSA', u'NGPL', u'NLOD-1.0', u'NLPL', u'NOSL', u'NPL-1.0', u'NPL-1.1', u'NPOSL-3.0', u'NRL', u'NTP', u'Naumen', u'NetCDF', u'Newsletr', u'Nokia', u'Noweb', u'Nunit', u'OCCT-PL', u'OCLC-2.0', u'ODbL-1.0', u'OFL-1.0', u'OFL-1.1', u'OGTSL', u'OLDAP-1.1', u'OLDAP-1.2', u'OLDAP-1.3', u'OLDAP-1.4', u'OLDAP-2.0', u'OLDAP-2.0.1', u'OLDAP-2.1', u'OLDAP-2.2', u'OLDAP-2.2.1', u'OLDAP-2.2.2', u'OLDAP-2.3', u'OLDAP-2.4', u'OLDAP-2.5', u'OLDAP-2.6', u'OLDAP-2.7', u'OLDAP-2.8', u'OML', u'OPL-1.0', u'OSET-PL-2.1', u'OSL-1.0', u'OSL-1.1', u'OSL-2.0', u'OSL-2.1', u'OSL-3.0', u'OpenSSL', u'PDDL-1.0', u'PHP-3.0', u'PHP-3.01', u'Plexus', u'PostgreSQL', u'Python-2.0', u'QPL-1.0', u'Qhull', u'RHeCos-1.1', u'RPL-1.1', u'RPL-1.5', u'RPSL-1.0', u'RSA-MD', u'RSCPL', u'Rdisc', u'Ruby', u'SAX-PD', u'SCEA', u'SGI-B-1.0', u'SGI-B-1.1', u'SGI-B-2.0', u'SISSL', u'SISSL-1.2', u'SMLNJ', u'SMPPL', u'SNIA', u'SPL-1.0', u'SWL', u'Saxpath', u'Sendmail', u'SimPL-2.0', u'Sleepycat', u'Spencer-86', u'Spencer-94', u'Spencer-99', u'SugarCRM-1.1.3', u'TCL', u'TMate', u'TORQUE-1.1', u'TOSL', u'UPL-1.0', u'Unicode-TOU', u'Unlicense', u'VOSTROM', u'VSL-1.0', u'Vim', u'W3C', u'W3C-19980720', u'WTFPL', u'Watcom-1.0', u'Wsuipa', u'X11', u'XFree86-1.1', u'XSkat', u'Xerox', u'Xnet', u'YPL-1.0', u'YPL-1.1', u'ZPL-1.1', u'ZPL-2.0', u'ZPL-2.1', u'Zed', u'Zend-2.0', u'Zimbra-1.3', u'Zimbra-1.4', u'Zlib', u'bzip2-1.0.5', u'bzip2-1.0.6', u'curl', u'diffmark', u'dvipdfm', u'eGenix', u'gSOAP-1.3b', u'gnuplot', u'iMatix', u'libtiff', u'mpich2', u'psfrag', u'psutils', u'xinetd', u'xpp', u'zlib-acknowledgement', u'Proprietary', u'Other', u'Unlicensed'])
		attrs = enum(attrs)
		return attrs



