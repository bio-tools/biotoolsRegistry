from rest_framework import serializers
from elixir.models import *
from elixir.validators import *


class LanguageSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        allow_blank=False, validators=[IsStringTypeValidator], required=False
    )

    class Meta:
        model = Language
        fields = ("name",)

    def get_pk_field(self, model_field):
        return None

    def to_representation(self, obj):
        return obj.name

    # need to add validation here since this method overrides all validation
    def to_internal_value(self, data):
        # checking if blank
        IsNotBlankValidator(data)
        # checking if within enum
        enum = ENUMValidator(
            [
                "ActionScript",
                "Ada",
                "AppleScript",
                "Assembly language",
                "AWK",
                "Bash",
                "C",
                "C#",
                "C++",
                "Clojure",
                "COBOL",
                "Cython",
                "ColdFusion",
                "CUDA",
                "CWL",
                "D",
                "Delphi",
                "Dylan",
                "Eiffel",
                "Elm",
                "F#",
                "Forth",
                "Fortran",
                "Go",
                "Groovy",
                "Haskell",
                "Java",
                "JavaScript",
                "Julia",
                "Jython",
                "JSP",
                "Kotlin",
                "LabVIEW",
                "Lisp",
                "Lua",
                "Maple",
                "Mathematica",
                "MATLAB",
                "MLXTRAN",
                "NMTRAN",
                "OCaml",
                "Pascal",
                "Perl",
                "PHP",
                "Prolog",
                "PyMOL",
                "Python",
                "Q#",
                "QCL",
                "R",
                "Racket",
                "REXX",
                "Ruby",
                "Rust",
                "SAS",
                "Scala",
                "Scheme",
                "Shell",
                "Smalltalk",
                "SQL",
                "Swift",
                "Turing",
                "TypeScript",
                "Verilog",
                "VHDL",
                "Visual Basic",
                "XAML",
                "Other",
            ]
        )
        data = enum(data)
        return {"name": data}
