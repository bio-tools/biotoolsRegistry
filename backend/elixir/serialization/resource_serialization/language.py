from rest_framework import serializers
from elixir.models import *
from elixir.validators import *

class LanguageSerializer(serializers.ModelSerializer):
	name = serializers.CharField(allow_blank=False, validators=[IsStringTypeValidator], required=False)

	class Meta:
		model = Language
		fields = ('name',)

	def get_pk_field(self, model_field):
		return None

	def to_representation(self, obj):
		return obj.name

	# need to add validation here since this method overrides all validation
	def to_internal_value(self, data):
		# checking if blank
		IsNotBlankValidator(data)
		# checking if within enum
		enum = ENUMValidator([u'ActionScript', u'Ada', u'AppleScript', u'Assembly language', u'AWK', u'Bash', u'C', u'C#', u'C++', u'COBOL', u'ColdFusion', u'CWL', u'D', u'Delphi', u'Dylan', u'Eiffel', u'Forth', u'Fortran', u'Groovy', u'Haskell', u'Icarus', u'Java', u'JavaScript', u'JSP', u'LabVIEW', u'Lisp', u'Lua', u'Maple', u'Mathematica', u'MATLAB', u'MLXTRAN', u'NMTRAN', u'OCaml', u'Pascal', u'Perl', u'PHP', u'Prolog', u'PyMOL', u'Python', u'R', u'Racket', u'REXX', u'Ruby', u'SAS', u'Scala', u'Scheme', u'Shell', u'Smalltalk', u'SQL', u'Turing', u'Verilog', u'VHDL', u'Visual Basic', u'XAML', u'Other'])
		data = enum(data)
		return {'name': data}