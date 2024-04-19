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
		enum = ENUMValidator(['ActionScript', 'Ada', 'AppleScript', 'Assembly language', 'AWK', 'Bash', 'C', 'C#', 'C++', 'COBOL', 'ColdFusion', 'CWL', 'D', 'Delphi', 'Dylan', 'Eiffel', 'Elm', 'Forth', 'Fortran', 'Groovy', 'Haskell', 'Icarus', 'Java', 'JavaScript', 'JSP', 'Julia', 'LabVIEW', 'Lisp', 'Lua', 'Maple', 'Mathematica', 'MATLAB', 'MLXTRAN', 'NMTRAN', 'OCaml', 'Pascal', 'Perl', 'PHP', 'Prolog', 'PyMOL', 'Python', 'R', 'Racket', 'REXX', 'Ruby', 'SAS', 'Scala', 'Scheme', 'Shell', 'Smalltalk', 'SQL', 'Turing', 'Verilog', 'VHDL', 'Visual Basic', 'XAML', 'Other'])
		data = enum(data)
		return {'name': data}