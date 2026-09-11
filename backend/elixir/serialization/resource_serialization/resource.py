from rest_framework import serializers
from elixir.models import *
from elixir.validators import *
from elixir.licenses import ALLOWED_LICENSES
from django.conf import settings
from rest_framework.pagination import PageNumberPagination
from elixir.serialization.resource_serialization.domain import *
from elixir.serialization.resource_serialization.edam import *
from elixir.serialization.resource_serialization.operatingSystem import *
from elixir.serialization.resource_serialization.toolType import *
from elixir.serialization.resource_serialization.language import *

# from elixir.serialization.resource_serialization.accessibility import *
from elixir.serialization.resource_serialization.publication import *
from elixir.serialization.resource_serialization.credit import *
from elixir.serialization.resource_serialization.link import *
from elixir.serialization.resource_serialization.download import *
from elixir.serialization.resource_serialization.documentation import *
from elixir.serialization.resource_serialization.collection import *
from elixir.serialization.resource_serialization.contact import *
from elixir.serialization.resource_serialization.version import *
from rest_framework.validators import UniqueValidator


def issue_function(resource, user):
    pass
    # check for issues
    # EDAMTopicIssue([resource], user=user).report()
    # EDAMOperationIssue([resource], user=user).report()
    # EDAMDataIssue([resource], user=user).report()
    # EDAMFormatIssue([resource], user=user).report()
    # NoLicenseIssue([resource], user=user).report()
    # NoContactIssue([resource], user=user).report()
    # NoTOSIssue([resource], user=user).report()


class OtherIDSerializer(serializers.ModelSerializer):
    value = serializers.CharField(allow_blank=False, required=True)
    type = serializers.CharField(allow_blank=True, required=False)
    version = serializers.CharField(
        allow_blank=True,
        max_length=100,
        min_length=1,
        validators=[IsVersionValidator],
        required=False,
    )

    class Meta:
        model = OtherID
        fields = ("value", "type", "version")

    def validate_value(self, attrs):
        # make sure the version matches the regular expression
        d = re.compile(r"^DOI:10\.[0-9]{4,9}\/[-\._;\(\)\/:a-zA-Z0-9]+$", re.IGNORECASE)
        r = re.compile(r"^RRID:.+$", re.IGNORECASE | re.UNICODE)
        c = re.compile(r"^cpe:.+$", re.IGNORECASE | re.UNICODE)
        # The biotoolsCURIE must have at least one character, that's why the + is there
        # need access to multiple fields should merge the two validate_ functions into one validate()
        b = re.compile(r"^biotools:[_\-.0-9a-zA-Z]+$", re.IGNORECASE | re.UNICODE)

        if not (
            d.search(attrs) or r.search(attrs) or c.search(attrs) or b.search(attrs)
        ):
            raise serializers.ValidationError(
                "The value has to be a DOI, RRID, cpe or biotoolsCURIE. Make sure you added the prefixes."
            )
        return attrs

    def validate_type(self, attrs):
        enum = ENUMValidator(["doi", "rrid", "cpe", "biotoolsCURIE"])
        attrs = enum(attrs)
        return attrs

    def validate(self, data):
        if data.get("type") and data.get("value"):
            # check if super user , who is the only one allowed to change biotools type of otherID
            if data["type"] == "biotoolsCURIE":
                try:
                    is_superuser = self.context["request"].user.is_superuser
                    if is_superuser == False and self.context["request_type"] == "POST":
                        raise serializers.ValidationError(
                            "Only admin users can add 'biotools:'-type of otherID."
                        )
                except (AttributeError, KeyError):
                    # this means there is no context, so no PUT / POST request
                    pass
                if not (data["value"].lower().startswith("biotools:")):
                    raise serializers.ValidationError(
                        "The type of the id is not the same as the id value."
                    )
            elif not (data["value"].lower().startswith(data["type"].lower() + ":")):
                raise serializers.ValidationError(
                    "The type of the id is not the same as the id value."
                )
        elif data.get("value"):
            if data["value"].lower().startswith("biotools:"):
                try:
                    is_superuser = self.context["request"].user.is_superuser
                    if is_superuser == False and self.context["request_type"] == "POST":
                        raise serializers.ValidationError(
                            "Only admin users can add 'biotools:'-type of otherID."
                        )
                except (AttributeError, KeyError):
                    # this means there is no context, so no PUT / POST request
                    pass

        return data

    def get_pk_field(self, model_field):
        return None


# elixirPlatform
class ElixirPlatformSerializer(serializers.ModelSerializer):
    elixirPlatform = serializers.CharField(allow_blank=False, required=False)

    class Meta:
        model = ElixirPlatform
        fields = ("elixirPlatform",)

    def validate_elixirPlatform(self, attrs):
        enum = ENUMValidator(
            ["Data", "Tools", "Compute", "Interoperability", "Training"]
        )
        attrs = enum(attrs)
        return attrs

    def to_representation(self, obj):
        return obj.elixirPlatform

    def get_pk_field(self, model_field):
        return None

    def to_internal_value(self, data):
        # checking if blank
        IsNotBlankValidator(data)
        enum = ENUMValidator(
            ["Data", "Tools", "Compute", "Interoperability", "Training"]
        )
        data = enum(data)

        return {"elixirPlatform": data}


# elixirNode
class ElixirNodeSerializer(serializers.ModelSerializer):
    elixirNode = serializers.CharField(allow_blank=False, required=False)

    class Meta:
        model = ElixirNode
        fields = ("elixirNode",)

    def validate_elixirNode(self, attrs):
        enum = ENUMValidator(
            [
                "Belgium",
                "Czech Republic",
                "Denmark",
                "EMBL",
                "Estonia",
                "Finland",
                "France",
                "Germany",
                "Greece",
                "Hungary",
                "Ireland",
                "Israel",
                "Italy",
                "Luxembourg",
                "Netherlands",
                "Norway",
                "Portugal",
                "Slovenia",
                "Spain",
                "Sweden",
                "Switzerland",
                "UK",
            ]
        )
        attrs = enum(attrs)
        return attrs

    def to_representation(self, obj):
        return obj.elixirNode

    def to_internal_value(self, data):
        # checking if blank

        IsNotBlankValidator(data)
        enum = ENUMValidator(
            [
                "Belgium",
                "Czech Republic",
                "Denmark",
                "EMBL",
                "Estonia",
                "Finland",
                "France",
                "Germany",
                "Greece",
                "Hungary",
                "Ireland",
                "Israel",
                "Italy",
                "Luxembourg",
                "Netherlands",
                "Norway",
                "Portugal",
                "Slovenia",
                "Spain",
                "Sweden",
                "Switzerland",
                "UK",
            ]
        )
        data = enum(data)

        return {"elixirNode": data}

    def get_pk_field(self, model_field):
        return None


# elixirCommunity
class ElixirCommunitySerializer(serializers.ModelSerializer):
    elixirCommunity = serializers.CharField(allow_blank=False, required=False)

    class Meta:
        model = ElixirCommunity
        fields = ("elixirCommunity",)

    def validate_elixirCommunity(self, attrs):
        enum = ENUMValidator(
            [
                "3D-BioInfo",
                "Biodiversity",
                "Cancer Data",
                "Federated Human Data",
                "Food and Nutrition",
                "Galaxy",
                "Human Copy Number Variation",
                "Intrinsically Disordered Proteins",
                "Marine Metagenomics",
                "Metabolomics",
                "Microbial Biotechnology",
                "Microbiome",
                "Plant Sciences",
                "Proteomics",
                "Rare Diseases",
                "Research Data Management",
                "Single-cell Omics",
                "Systems Biology",
                "Toxicology",
            ]
        )
        attrs = enum(attrs)
        return attrs

    def to_representation(self, obj):
        return obj.elixirCommunity

    def to_internal_value(self, data):
        # checking if blank

        IsNotBlankValidator(data)
        enum = ENUMValidator(
            [
                "3D-BioInfo",
                "Biodiversity",
                "Federated Human Data",
                "Galaxy",
                "Human Copy Number Variation",
                "Intrinsically Disordered Proteins",
                "Marine Metagenomics",
                "Metabolomics",
                "Microbial Biotechnology",
                "Plant Sciences",
                "Proteomics",
                "Rare Diseases",
                "Systems Biology",
            ]
        )
        data = enum(data)

        return {"elixirCommunity": data}

    def get_pk_field(self, model_field):
        return None


# relations
class RelationSerializer(serializers.ModelSerializer):
    biotoolsID = serializers.CharField(allow_blank=False, required=True)
    type = serializers.CharField(allow_blank=True, required=True)

    class Meta:
        model = Relation
        fields = ("biotoolsID", "type")

    def validate_biotoolsID(self, attrs):

        r = Resource.objects.filter(visibility=1, biotoolsID=attrs)

        if len(r) == 0:
            raise serializers.ValidationError(
                "There is no resource with biotoolsID:"
                + attrs
                + ";The resource might have been deleted."
            )

        if len(r) > 1:
            raise serializers.ValidationError(
                "DuplicateBiotoolsIDError on resource with id:"
                + attrs
                + ";please contact our support team and paste the error in the message."
            )

        return attrs

    def validate_type(self, attrs):
        enum = ENUMValidator(
            [
                "isNewVersionOf",
                "hasNewVersion",
                "uses",
                "usedBy",
                "includes",
                "includedIn",
            ]
        )
        attrs = enum(attrs)
        return attrs

    def get_pk_field(self, model_field):
        return None


class ResourceSerializer(serializers.ModelSerializer):

    # instead of the id we use biotoolsID to identify the resources from the user point of view
    lookup_field = "biotoolsID"

    # # need an alias so input has 'id' which is saved in the 'biotoolsID' field
    # id = serializers.CharField(read_only=True, source="biotoolsID");
    # id = serializers.CharField(allow_blank=False, max_length=50, min_length=1, source="biotoolsID", validators=[UniqueValidator(queryset=Resource.objects.filter(visibility=1), message="A resource with this ID already exists.")]);

    # get the owner username from the auth_user table
    owner = serializers.SlugRelatedField(read_only=True, slug_field="username")
    # alias for 'was_id_validated'
    validated = serializers.IntegerField(read_only=True, source="was_id_validated")

    biotoolsID = serializers.CharField(
        min_length=1,
        max_length=100,
        allow_blank=False,
        validators=[
            UniqueValidator(
                queryset=Resource.objects.filter(visibility=1),
                message="A resource with this ID already exists. bio.tools IDs need to be unique",
            )
        ],
    )
    # biotoolsCURIE = serializers.CharField(allow_blank=False, validators=[UniqueValidator(queryset=Resource.objects.filter(visibility=1), message="A resource with this ID already exists.")])
    # biotoolsID = serializers.CharField(read_only=True);
    biotoolsCURIE = serializers.CharField(read_only=True)
    # name = serializers.CharField(min_length=1, max_length=100, allow_blank=False, validators=[IsStringTypeValidator, UniqueValidator(queryset=Resource.objects.filter(visibility=1), message="The resource ID (biotoolsID) generated from this name already exists; Use a different name.")])

    name = serializers.CharField(
        min_length=1,
        max_length=100,
        allow_blank=False,
        validators=[IsStringTypeValidator],
    )
    homepage = serializers.CharField(
        max_length=300,
        min_length=1,
        allow_blank=False,
        validators=[is_blacklisted_url_validator],
    )

    elixir_badge = serializers.IntegerField(read_only=True)
    homepage_status = serializers.IntegerField(read_only=True)
    confidence_flag = serializers.CharField(
        allow_blank=False, max_length=8, min_length=1, required=False
    )
    cost = serializers.CharField(
        allow_blank=False, max_length=300, min_length=1, required=False
    )
    maturity = serializers.CharField(
        allow_blank=False, max_length=300, min_length=1, required=False
    )
    license = serializers.CharField(
        allow_blank=False, max_length=300, min_length=1, required=False
    )
    accessibility = serializers.CharField(
        allow_blank=True,
        max_length=300,
        min_length=1,
        required=False,
        validators=[IsNotBlankValidator],
    )
    # Version this needs to be 0 to many

    version = VersionSerializer(many=True, required=False, allow_empty=False)
    # version = serializers.CharField(max_length=100, allow_blank=True, validators=[IsStringTypeValidator], required=False, default=None)
    otherID = OtherIDSerializer(many=True, required=False, allow_empty=False)
    # canonicalID = serializers.CharField(max_length=50, allow_blank=True, validators=[IsStringTypeValidator], required=False)
    description = serializers.CharField(
        min_length=10,
        max_length=1000,
        allow_blank=False,
        validators=[IsStringTypeValidator],
        required=True,
    )
    # short_description = serializers.CharField(min_length=10, max_length=100, allow_blank=False, validators=[IsStringTypeValidator], required=False)

    # nested attributes
    topic = TopicSerialiser(
        many=True,
        required=False,
        allow_empty=False,
        error_messages={"empty": "This list may not be empty."},
    )
    function = FunctionSerializer(many=True, required=False, allow_empty=False)
    credit = CreditSerializer(many=True, required=False, allow_empty=False)
    # elixirInfo = ElixirInfoSerializer(many=False, required=False)
    link = LinkSerializer(many=True, required=False, allow_empty=False)
    documentation = DocumentationSerializer(
        many=True, required=False, allow_empty=False
    )
    download = DownloadSerializer(many=True, required=False, allow_empty=False)
    operatingSystem = OperatingSystemSerializer(
        many=True, required=False, allow_empty=False
    )
    toolType = ToolTypeSerializer(many=True, required=False, allow_empty=False)
    language = LanguageSerializer(many=True, required=False, allow_empty=False)
    # accessibility = AccessibilitySerializer(many=True, required=False, allow_empty=False)
    publication = PublicationSerializer(many=True, required=False, allow_empty=False)

    elixirPlatform = ElixirPlatformSerializer(
        many=True, required=False, allow_empty=False
    )
    elixirNode = ElixirNodeSerializer(many=True, required=False, allow_empty=False)
    elixirCommunity = ElixirCommunitySerializer(
        many=True, required=False, allow_empty=False
    )

    # uses = UsesSerializer(many=True, required=False, allow_empty=False)
    collectionID = CollectionIDSerializer(many=True, required=False, allow_empty=False)

    # relation
    relation = RelationSerializer(many=True, required=False, allow_empty=False)

    # contact = ContactSerializer(many=True, required=False, allow_empty=False)
    editPermission = EditPermissionSerializer(many=False, required=False)

    class Meta:
        model = Resource
        fields = (
            "name",
            "description",
            "homepage",
            "biotoolsID",
            "biotoolsCURIE",
            "version",
            "otherID",
            "relation",
            "function",
            "toolType",
            "topic",
            "operatingSystem",
            "language",
            "license",
            "collectionID",
            "maturity",
            "cost",
            "accessibility",
            "elixirPlatform",
            "elixirNode",
            "elixirCommunity",
            "link",
            "download",
            "documentation",
            "publication",
            "credit",
            "owner",
            "additionDate",
            "lastUpdate",
            #'availability',
            #'downtime',
            "editPermission",
            "validated",
            "homepage_status",
            "elixir_badge",
            "confidence_flag",
        )
        validators = []

    def validate_name(self, attrs):

        # make sure the name matches the regular expression
        # TODO: make name unique

        # this looks wrong
        # p = re.compile('^[\p{Zs}A-Za-z0-9+\.,\-_:;()]*$', re.IGNORECASE | re.UNICODE)

        # use this
        p = re.compile(r"^[ A-Za-z0-9+\.,\-\~_:;()]*$", re.IGNORECASE | re.UNICODE)

        if not p.search(attrs):
            raise serializers.ValidationError(
                "This field can only contain letters, numbers, spaces or these characters: + . , - ~ _ : ; ( )"
            )
        return attrs

    def validate_biotoolsID(self, attrs):
        p = re.compile(r"^[A-Za-z0-9\.\-\~_]*$", re.IGNORECASE | re.UNICODE)
        p1 = re.compile(r"^[A-Za-z0-9]+.*$", re.IGNORECASE | re.UNICODE)
        if not p.search(attrs):
            raise serializers.ValidationError(
                "The biotoolsID can only contain letters, numbers or these characters: . - _ ~ "
            )
        if not p1.search(attrs):
            raise serializers.ValidationError(
                "The biotoolsID can only start with letters and numbers"
            )
        if attrs.endswith("."):
            raise serializers.ValidationError("The biotoolsID cannot end with a dot")
        return attrs

    def validate_homepage(self, attrs):
        attrs = IsURLFTPValidator(attrs)
        return attrs

    def validate_confidence_flag(self, attrs):
        enum = ENUMValidator(["tool", "high", "medium", "low", "very low"])
        attrs = enum(attrs)
        return attrs

    def validate_cost(self, attrs):
        enum = ENUMValidator(
            ["Free of charge", "Free of charge (with restrictions)", "Commercial"]
        )
        attrs = enum(attrs)
        return attrs

    def validate_maturity(self, attrs):
        enum = ENUMValidator(["Emerging", "Mature", "Legacy"])
        attrs = enum(attrs)
        return attrs

    def validate_accessibility(self, attrs):
        enum = ENUMValidator(
            ["Open access", "Open access (with restrictions)", "Restricted access"]
        )
        attrs = enum(attrs)
        return attrs

    def validate_license(self, attrs):
        # The vocabulary lives in elixir/licenses.py: every current SPDX
        # identifier, plus the retired ones bio.tools already accepted, plus
        # bio.tools' own non-SPDX values. See that module before editing.
        enum = ENUMValidator(sorted(ALLOWED_LICENSES))
        attrs = enum(attrs)
        return attrs

    # creating the resource
    def create(self, validated_data):
        pop = lambda l, k: l.pop(k) if k in list(l.keys()) else []
        uniq = lambda l, k: [
            dict(t) for t in set([tuple(d.items()) for d in pop(l, k)])
        ]

        # nested attributes need to be popped from resource and added after resource has been saved
        # otherwise nothing will work
        # 2hrs it took me to understand this little detail

        # pop nested attributes
        version_list = (
            validated_data.pop("version")
            if "version" in list(validated_data.keys())
            else []
        )
        otherID_list = (
            validated_data.pop("otherID")
            if "otherID" in list(validated_data.keys())
            else []
        )
        topic_list = (
            validated_data.pop("topic")
            if "topic" in list(validated_data.keys())
            else []
        )
        function_list = (
            validated_data.pop("function")
            if "function" in list(validated_data.keys())
            else []
        )
        publication_list = (
            validated_data.pop("publication")
            if "publication" in list(validated_data.keys())
            else []
        )
        documentation_list = (
            validated_data.pop("documentation")
            if "documentation" in list(validated_data.keys())
            else []
        )
        download_list = (
            validated_data.pop("download")
            if "download" in list(validated_data.keys())
            else []
        )
        link_list = (
            validated_data.pop("link") if "link" in list(validated_data.keys()) else []
        )
        credit_list = (
            validated_data.pop("credit")
            if "credit" in list(validated_data.keys())
            else []
        )
        elixirPlatform_list = (
            validated_data.pop("elixirPlatform")
            if "elixirPlatform" in list(validated_data.keys())
            else []
        )
        elixirNode_list = (
            validated_data.pop("elixirNode")
            if "elixirNode" in list(validated_data.keys())
            else []
        )
        elixirCommunity_list = (
            validated_data.pop("elixirCommunity")
            if "elixirCommunity" in list(validated_data.keys())
            else []
        )

        credit_dict = (
            validated_data.pop("credit")
            if "credit" in list(validated_data.keys())
            else []
        )
        # elixirInfo_dict = validated_data.pop('elixirInfo') if 'elixirInfo' in validated_data.keys() else []
        operatingSystem_list = uniq(validated_data, "operatingSystem")
        toolType_list = uniq(validated_data, "toolType")
        language_list = uniq(validated_data, "language")

        # accessibility_list = uniq(validated_data, 'accessibility')
        # uses_list = uniq(validated_data, 'uses')
        collectionID_list = uniq(validated_data, "collectionID")

        relation_list = (
            validated_data.pop("relation")
            if "relation" in list(validated_data.keys())
            else []
        )

        # contact_list = validated_data.pop('contact') if 'contact' in validated_data.keys() else []
        editPermission_dict = (
            validated_data.pop("editPermission")
            if "editPermission" in list(validated_data.keys())
            else {}
        )
        editPermissionAuthor_dict = (
            editPermission_dict.pop("authors")
            if "authors" in list(editPermission_dict.keys())
            else {}
        )

        # elixirInfo = None
        # if elixirInfo_dict:
        # 	elixirInfo = ElixirInfo.objects.create(**elixirInfo_dict)

        editPermission = None
        # set default permission type
        if editPermission_dict:
            editPermission = EditPermission.objects.create(**editPermission_dict)
        else:
            editPermission = EditPermission.objects.create(type="private")
        # create resource authors
        if editPermissionAuthor_dict:
            for author_dict in editPermissionAuthor_dict:
                username = author_dict["username"]
                user = User.objects.filter(username=username)[0]
                authors = EditPermissionAuthor.objects.filter(user=user)
                author = None
                if authors.count() > 0:
                    author = authors[0]
                else:
                    author = EditPermissionAuthor.objects.create(user=user)
                author.editPermissions.add(editPermission)
                editPermission.authors.add(author)

        validated_data["biotoolsCURIE"] = "biotools:" + validated_data["biotoolsID"]

        # # if biotoolsID not passed in save(), then generate one out of name
        # if 'biotoolsID' not in validated_data:
        # 	# create id and randomize it if there are conflicts
        # 	biotoolsID = re.sub(r"[^a-zA-Z0-9_. -]*", "", validated_data['name'])
        # 	biotoolsID = re.sub(r"[ ]+", "_", biotoolsID)
        # 	if len(Resource.objects.filter(visibility=1, biotoolsID__iexact=biotoolsID)) > 0 or biotoolsID in settings.RESERVED_URL_KEYWORDS:
        # 		raise CustomError('The name you provided clashes with an existing biotoolsID. Please provide a different name.', 'biotoolsID', status_code=status.HTTP_400_BAD_REQUEST)
        # 		# biotoolsID = initialbiotoolsID + str(randint(1000, 9999))
        # 		# count += 1
        # 		# if count > 9998:
        # 		# 	raise CustomError('ID could not be generated', 'id', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # 	validated_data['biotoolsID'] = biotoolsID
        # 	validated_data['biotoolsCURIE'] = 'biotools:' + biotoolsID

        # create parent attribute
        resource = Resource.objects.create(
            editPermission=editPermission, **validated_data
        )

        # add nested attributes to parent attribute
        for version in version_list:
            Version.objects.create(resource=resource, **version)

        for otherID in otherID_list:
            OtherID.objects.create(resource=resource, **otherID)

        for elixirPlatform in elixirPlatform_list:
            ElixirPlatform.objects.create(resource=resource, **elixirPlatform)

        for elixirNode in elixirNode_list:
            ElixirNode.objects.create(resource=resource, **elixirNode)

        for elixirCommunity in elixirCommunity_list:
            ElixirCommunity.objects.create(resource=resource, **elixirCommunity)

        for topic in topic_list:
            Topic.objects.create(resource=resource, **topic)

        for publication in publication_list:
            publicationtype_list = (
                publication.pop("type") if "type" in list(publication.keys()) else []
            )

            publication_object = Publication.objects.create(
                resource=resource, **publication
            )

            for publicationtype in publicationtype_list:
                PublicationType.objects.create(
                    publication=publication_object, **publicationtype
                )

        # for publication in publication_list:
        # 	Publication.objects.create(resource=resource, **publication)

        # for documentation in documentation_list:
        # 	Documentation.objects.create(resource=resource, **documentation)

        for documentation in documentation_list:
            documentationtype_list = (
                documentation.pop("type")
                if "type" in list(documentation.keys())
                else []
            )

            documentation_object = Documentation.objects.create(
                resource=resource, **documentation
            )

            for documentationtype in documentationtype_list:
                DocumentationType.objects.create(
                    documentation=documentation_object, **documentationtype
                )

        for credit in credit_list:
            typerole_list = (
                credit.pop("typeRole") if "typeRole" in list(credit.keys()) else []
            )

            credit = Credit.objects.create(resource=resource, **credit)

            for typeRole in typerole_list:
                CreditTypeRole.objects.create(credit=credit, **typeRole)

        for link in link_list:
            linktype_list = link.pop("type") if "type" in list(link.keys()) else []

            link_object = Link.objects.create(resource=resource, **link)

            for linktype in linktype_list:
                LinkType.objects.create(link=link_object, **linktype)

        for download in download_list:
            Download.objects.create(resource=resource, **download)

        for function in function_list:
            # pop nested attributes, check if they exist in input data for optional ones
            operation_list = uniq(function, "operation")
            input_list = (
                function.pop("input") if "input" in list(function.keys()) else []
            )
            output_list = (
                function.pop("output") if "output" in list(function.keys()) else []
            )

            # create parent attribute
            function = Function.objects.create(resource=resource, **function)

            # add nested attributes to parent attribute

            for operation in operation_list:
                Operation.objects.create(function=function, **operation)

            for input in input_list:
                # pop nested attributes, check if they exist in input data for optional ones
                data = Data.objects.create(**(input.pop("data")))
                format_list = uniq(input, "format")

                # create parent attribute with grandparent and nested attributes
                input = Input.objects.create(function=function, data=data, **input)

                # add additional nested attributes to parent attribute
                for format in format_list:
                    Format.objects.create(input=input, **format)

            for output in output_list:
                # pop nested attributes, check if they exist in input data for optional ones
                data = Data.objects.create(**(output.pop("data")))
                format_list = uniq(output, "format")

                # create parent attribute with grandparent and nested attributes
                output = Output.objects.create(function=function, data=data, **output)

                # add additional nested attributes to parent attribute
                for format in format_list:
                    Format.objects.create(output=output, **format)

        for operatingSystem in operatingSystem_list:
            OperatingSystem.objects.create(resource=resource, **operatingSystem)

        for toolType in toolType_list:
            ToolType.objects.create(resource=resource, **toolType)

        for language in language_list:
            Language.objects.create(resource=resource, **language)

        # for accessibility in accessibility_list:
        # 	Accessibility.objects.create(resource=resource, **accessibility)

        for collectionID in collectionID_list:
            CollectionID.objects.create(resource=resource, **collectionID)

        for relation in relation_list:
            Relation.objects.create(resource=resource, **relation)

        # for contact in contact_list:
        # 	contact = Contact.objects.create(resource=resource, **contact)

        return resource


class ResourceUpdateSerializer(ResourceSerializer):
    # removed the uniqueness constraint, since this is an 'update'
    # id = serializers.CharField(source="biotoolsID", read_only=True)
    # curie = serializers.CharField(source="biotoolsCURIE", read_only=True)

    biotoolsID = serializers.CharField(
        min_length=1,
        max_length=100,
        allow_blank=False,
        validators=[
            IsStringTypeValidator,
        ],
    )
    # publication is not mandatory for updates, nor for anything else
    # this is so that other fields can be updated, without the lack of publication being a blocker
    # publication = PublicationSerializer(many=True, required=False, allow_empty=False)

    # initially the name generates the biotoolsID
    # now technically they can change the tool name
    # should we allow for name changes or not?
    # currently we do and thus the unique constraint message reflects this
    # if we don't allow change the unique constraint name message
    def validate(self, data):
        return data

    class Meta:
        model = Resource
        # exclude = ('id', 'biotoolsID', 'owner','name', 'curie')
        # initially it was exclude
        # we either exclude a lot of hidden stuff or we specify (even though duplicated) the fields below
        fields = (
            "name",
            "description",
            "homepage",
            "biotoolsID",
            "biotoolsCURIE",
            "version",
            "otherID",
            "relation",
            "function",
            "toolType",
            "topic",
            "operatingSystem",
            "language",
            "license",
            "collectionID",
            "maturity",
            "cost",
            "accessibility",
            "elixirPlatform",
            "elixirNode",
            "elixirCommunity",
            "link",
            "download",
            "documentation",
            "publication",
            "credit",
            "owner",
            "additionDate",
            "lastUpdate",
            #'availability',
            #'downtime',
            "editPermission",
            "validated",
            "homepage_status",
            "elixir_badge",
            "confidence_flag",
        )


# just get the names and the id's
class ResourceNameSerializer(ResourceSerializer):
    id = serializers.CharField(source="biotoolsID", read_only=True)

    class Meta:
        model = Resource
        fields = (
            "id",
            "name",
            "version",
            "additionDate",
            "lastUpdate",
            "editPermission",
        )


# basic information for tool list
class ToolListResourceSerializer(ResourceSerializer):
    # biotoolsID = serializers.CharField(source="biotoolsID", read_only=True)

    class Meta:
        model = Resource
        fields = (
            "biotoolsID",
            "name",
            "version",
            "additionDate",
            "lastUpdate",
        )


class ResourcePaginator(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "list": data,
            }
        )

    def get_next_link(self):
        if not self.page.has_next():
            return None
        page_number = self.page.next_page_number()
        return replace_query_param("", self.page_query_param, page_number)

    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        page_number = self.page.previous_page_number()
        return replace_query_param("", self.page_query_param, page_number)
