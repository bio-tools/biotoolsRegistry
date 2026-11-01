from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from elixir.permissions import (
    IsOwnerOrReadOnly,
    HasEditPermissionToEditResourceOrReadOnly,
    CanConcludeResourceRequest,
    IsStaffOrReadOnly,
)
from rest_framework.settings import api_settings
from rest_framework.exceptions import ValidationError
from elixir.queries import get_tool, search_tools, ToolNotFound, SearchPageNotFound
import elixir.elixir_logging as elixir_logging
from django.conf import settings
from rest_framework.response import Response
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from elasticsearch.exceptions import TransportError
from elixir.management_errors import ManagementUnavailable
from elixir.models import *
from elixir.serializers import *
from django.http import Http404
import uuid
from django.db.models import Q
from django.db import transaction
from elixir.renderers import XMLSchemaRenderer, JSONLDRenderer
from rest_framework.renderers import JSONRenderer
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework_yaml.renderers import YAMLRenderer

from rest_framework.parsers import JSONParser
from rest_framework_yaml.parsers import YAMLParser
from elixir.parsers import XMLSchemaParser
from elixir.tasks import notify_admins
from elixir.tasks import notify_resource_request
from elixir.tasks import (
    create_ecosystem_tool,
    update_ecosystem_tool,
    delete_ecosystem_tool,
)
import json
from hashlib import sha256
from django.utils import timezone

es = Elasticsearch(settings.ELASTIC_SEARCH_URLS)


def payload_fingerprint(validated_data, validated):
    # Version the comparison: upstream hashes sorted/deduplicated ordered annotations.
    payload = {key: value for key, value in validated_data.items()
               if key not in {'biotoolsID', 'additionDate', 'lastUpdate'}}
    # These four relations are explicitly sets in ResourceSerializer.create.
    for key in ('toolType', 'operatingSystem', 'language', 'collectionID'):
        if key in payload:
            payload[key] = sorted(payload[key], key=lambda item: json.dumps(item, sort_keys=True))
    return 'ordered-v1:' + sha256(json.dumps([payload, validated], sort_keys=True).encode()).hexdigest()


def check_update_confidence_flag(resource_confidence_flag, request_confidence_flag):
    # cannot change confidence_flag to high, medium, low, very low once it's been set to None or 'tool'
    if (resource_confidence_flag == "tool" or resource_confidence_flag is None) and (
        request_confidence_flag is not None and request_confidence_flag != "tool"
    ):
        return False
    return True


class ResourceList(APIView):
    """
    List all resources, or create a new resource.
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)
    parser_classes = (JSONParser, XMLSchemaParser, YAMLParser)
    renderer_classes = (
        BrowsableAPIRenderer,
        JSONRenderer,
        XMLSchemaRenderer,
        YAMLRenderer,
    )

    def get(self, request, format=None):
        query_dict = request.GET
        per_page_param = query_dict.get("per_page", api_settings.PAGE_SIZE)
        try:
            per_page = int(per_page_param)
        except (ValueError, TypeError):
            per_page = api_settings.PAGE_SIZE
        per_page = min(per_page, 100)
        page = int(query_dict.get("page", "1"))

        searchLogger = elixir_logging.SearchLogger(query_dict)
        searchLogger.commit()

        try:
            result = search_tools(query_dict, page=page, per_page=per_page)
        except SearchPageNotFound as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            {
                "count": result.count,
                "next": None if (page * result.per_page >= result.count) else "?page=" + str(page + 1),
                "previous": None if page == 1 else "?page=" + str(page - 1),
                "list": result.items,
            },
            status=200,
        )

    def post(self, request, format=None):
        serializer = ResourceSerializer(
            data=request.data, context={"request": request, "request_type": "POST"}
        )

        if serializer.is_valid():
            if (
                not request.user.is_superuser
                and request.data.get("confidence_flag")
                and request.data.get("confidence_flag") != "tool"
            ):
                return Response(
                    {
                        "detail": "Error: Only superusers can add entries with a confidence score other than 'tool'."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            right_now = timezone.now()

            # there is a very small millisecond difference between additionDate now and auto_now from lastUpdate
            # if we ever do some analysis we need to make sure we keep that in mind
            serializer.save(owner=request.user, additionDate=right_now)
            # issue_function(Resource.objects.get(biotoolsID=serializer.data['biotoolsID'], visibility=1), request.user)
            # Immediate management actions must be able to find this search document.
            es.index(
                index=settings.ELASTIC_SEARCH_INDEX,
                doc_type="_doc",
                body=serializer.data,
                refresh='wait_for',
            )
            # notify_admins(serializer.data['biotoolsID'], 'Tool CREATE', 'A tool was created.')

            if settings.GITHUB_ECOSYSTEM_ON:
                create_ecosystem_tool(serializer.data, str(request.user))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DisownResourceView(APIView):
    """
    Disown the request
    """

    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    )

    def get_object(self, biotoolsID):
        try:
            obj = Resource.objects.select_for_update().filter(visibility=1).get(
                biotoolsID__iexact=biotoolsID
            )
            self.check_object_permissions(self.request, obj)
            return obj
        except Resource.DoesNotExist:
            raise Http404

    def get_disowned_user(self):
        return User.objects.get(username__iexact="admin")

    @transaction.atomic
    def post(self, request, biotoolsID, format=None):
        resource = self.get_object(biotoolsID)
        resource.owner = self.get_disowned_user()
        resource.save()
        try:
            result = es.search(index=settings.ELASTIC_SEARCH_INDEX,
                               body={'query': {'match': {'biotoolsID': resource.biotoolsID.lower()}}})
            hits = result['hits']['hits']
            if len(hits) > 1:
                raise ManagementUnavailable('Duplicate index records require administrator repair. Nothing was disowned.')
            es.index(index=settings.ELASTIC_SEARCH_INDEX, doc_type='_doc',
                     id=hits[0]['_id'] if hits else resource.biotoolsID.lower(),
                     body=ResourceSerializer(resource).data, refresh='wait_for')
        except TransportError as exc:
            raise ManagementUnavailable() from exc
        return Response(
            {"detail": "You have successfully disowned your entry."},
            status=status.HTTP_200_OK,
        )


class ResourceRequestView(APIView):
    """
    Create or obtain resource requests.
    """

    permission_classes = (IsAuthenticated,)

    def put(self, request, format=None):
        if not isinstance(request.data, dict):
            raise ValidationError('Send a request object.')
        serializerData = request.data.copy()
        serializerData["username"] = request.user.username
        serializerData["email"] = request.user.email
        serializerData["requestId"] = str(uuid.uuid4())
        serializer = ResourceRequestSerializer(data=serializerData)
        if serializer.is_valid():
            serializer.save()
            notify_resource_request(
                serializer.data["type"], json.dumps(serializer.data)
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        my_requests = ResourceRequest.objects.filter(user=request.user)
        if request.user.is_superuser:
            received_requests = ResourceRequest.objects.all()
        else:
            owned = Resource.objects.filter(visibility=1, owner=request.user).values('biotoolsID')
            received_requests = ResourceRequest.objects.filter(
                Q(resource__biotoolsID__in=owned) | Q(completedBy=request.user)
            )
        received_requests_serializer = ResourceRequestSerializer(
            instance=received_requests, many=True
        )
        my_requests_serializer = ResourceRequestSerializer(
            instance=my_requests, many=True
        )
        return Response(
            {
                "requests": {
                    "received": received_requests_serializer.data,
                    "sent": my_requests_serializer.data,
                }
            },
            status=status.HTTP_200_OK,
        )


class ProcessResourceRequest(APIView):
    """
    Retrieve, update or delete a resource instance.
    """

    permission_classes = (IsAuthenticated, CanConcludeResourceRequest)

    @transaction.atomic
    def post(self, request, format=None):
        if not isinstance(request.data, dict):
            raise ValidationError('Send a request object.')
        if "requestId" not in request.data:
            return Response(
                {
                    "detail": "Request could not be completed. Missing parameter: 'requestId'."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if "accept" not in request.data:
            return Response(
                {
                    "detail": "Request could not be completed. Missing parameter: 'accept'."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not isinstance(request.data['requestId'], str):
            raise ValidationError({'requestId': ['Supply a request identifier.']})
        try:
            resourceRequest = ResourceRequest.objects.get(
                requestId=request.data["requestId"]
            )
            # Requests may point to a historical version after an editor save.
            # Lock the current resource before checking ownership or concluding.
            current = Resource.objects.select_for_update().get(
                biotoolsID=resourceRequest.resource.biotoolsID, visibility=1)
            resourceRequest = ResourceRequest.objects.select_for_update().get(pk=resourceRequest.pk)
            resourceRequest.resource = current
        except (ResourceRequest.DoesNotExist, Resource.DoesNotExist, AttributeError):
            return Response(
                {
                    "detail": "No active requests with a specified 'requestId' could be found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        self.check_object_permissions(self.request, resourceRequest)
        if resourceRequest.completed:
            return Response(
                {"detail": "Request has already been concluded."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = ResourceRequestConcludeSerializer(
            resourceRequest, data=request.data, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if resourceRequest.accepted:
            result = es.search(index=settings.ELASTIC_SEARCH_INDEX, body={
                'query': {'match': {'biotoolsID': current.biotoolsID.lower()}}})
            for hit in result['hits']['hits']:
                es.index(index=settings.ELASTIC_SEARCH_INDEX, doc_type='_doc',
                         id=hit['_id'], body=ResourceSerializer(current).data)
        responseSerializer = ResourceRequestSerializer(resourceRequest)
        return Response(responseSerializer.data, status=status.HTTP_200_OK)


class ResourceDetail(APIView):
    """
    Retrieve a specific resource
    """

    permission_classes = (
        IsAuthenticatedOrReadOnly,
        HasEditPermissionToEditResourceOrReadOnly,
    )
    # if interested in the resource update response content (other than the status)
    # then should add ?format=json or format=xml or format=yaml
    # because otherwise it will be by default format=api
    # to really make it clean, should have renderer for get() and renderers for put and delete
    # best here is to use functions instead of classes, and have api_view decorators for functions
    renderer_classes = (
        BrowsableAPIRenderer,
        JSONRenderer,
        XMLSchemaRenderer,
        YAMLRenderer,
        JSONLDRenderer,
    )
    parser_classes = (JSONParser, XMLSchemaParser, YAMLParser)

    def get_object(self, biotoolsID, *, lock=False):
        try:
            obj = get_tool(biotoolsID)
            if lock:
                obj = Resource.objects.select_for_update().get(pk=obj.pk, visibility=1)
        except (ToolNotFound, Resource.DoesNotExist):
            raise Http404
        self.check_object_permissions(self.request, obj)
        return obj

    def check_for_edit_permissions(self, request, resource):
        if request.user == resource.owner or request.user.is_superuser:
            return True
        return False

    def check_editing_permissions(self, request, resource):
        if "editPermission" in request.data:
            serializer = EditPermissionSerializer(data=request.data["editPermission"])
            if not serializer.is_valid():
                raise ValidationError({'editPermission': serializer.errors})
            if (
                "type" in request.data["editPermission"]
                and resource.editPermission.type
                != request.data["editPermission"]["type"]
            ):
                return True
            authors = set(
                resource.editPermission.authors.all().values_list(
                    "user__username", flat=True
                )
            )
            if "authors" not in request.data["editPermission"]:
                return False
            authorsRequest = set(request.data["editPermission"]["authors"])
            if authors != authorsRequest:
                return True
        return False

    def get(self, request, biotoolsID, format=None):
        resource = self.get_object(biotoolsID)
        serializer = ResourceSerializer(resource)
        return Response(serializer.data)

    def process_request_for_otherID(self, request, rID):
        if request.user.is_superuser:
            return request
        # only works if not superuser, and otherID is present and a valid list
        if (
            not request.user.is_superuser
            and request.data.get("otherID")
            and isinstance(request.data["otherID"], list)
        ):
            for oID in list(request.data["otherID"]):
                # we check for the "value" property on otherID
                if isinstance(oID, dict) and isinstance(oID.get("value"), str) and oID["value"].lower().startswith("biotools:"):
                    # remove if value is for "biotools" otherID
                    request.data["otherID"].remove(oID)

        # retrieve otherID of type biotools, if any, from current version of tool
        # and add them to the request object
        o_objects = OtherID.objects.filter(
            resource_id=rID, value__startswith="biotools:"
        )
        if len(o_objects) > 0:
            if not request.user.is_superuser and (
                not (request.data.get("otherID"))
                or not (isinstance(request.data["otherID"], list))
            ):
                request.data["otherID"] = []

            for o in o_objects:
                o_new = {}
                if o.value:
                    o_new["value"] = o.value
                if o.type:
                    o_new["type"] = o.type
                if o.version:
                    o_new["version"] = o.version
                request.data["otherID"].append(o_new)

            # if we removed all values and otherID is empty we need to remove it
            # to make sure we don't get validation error
        if (
            request.data.get("otherID")
            and isinstance(request.data["otherID"], list)
            and len(request.data["otherID"]) == 0
        ):
            del request.data["otherID"]

        return request

    # the update is actually creating a brand new resource, copying a few key information, and setting the visibility of the original to 0
    # use ?format=json or ?format=xml  if doing update (PUT) in the API
    # default is ?format=api
    @transaction.atomic
    def put(self, request, biotoolsID, format=None):
        resource = self.get_object(biotoolsID, lock=True)
        canEditPermissions = self.check_for_edit_permissions(request, resource)
        isEditingPermissions = self.check_editing_permissions(request, resource)
        if canEditPermissions == False and isEditingPermissions == True:
            return Response(
                {
                    "detail": "Only the owner can edit permissions for a specified resource."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        # Copy permissions from the existing resource in case not specified.
        if not isEditingPermissions:
            permissionSerializer = EditPermissionSerializer(resource.editPermission)
            request.data["editPermission"] = permissionSerializer.data

        request = self.process_request_for_otherID(request, resource.id)

        serializer = ResourceUpdateSerializer(
            data=request.data, context={"request": request, "request_type": "PUT", "previous_resource": resource}
        )

        if serializer.is_valid():
            # only superusers can change confidence_flag from tool to something else
            if not request.user.is_superuser and not (
                check_update_confidence_flag(
                    resource.confidence_flag, request.data.get("confidence_flag")
                )
            ):
                return Response(
                    {
                        "detail": "Error: Cannot change confidence_flag once it has been set to describe a tool."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            # only superusers can change the validated / was_id_validated flag, even so, it can only be 0 or 1
            is_id_valid = resource.was_id_validated
            if request.user.is_superuser and request.data.get("validated") in [0, 1]:
                is_id_valid = request.data["validated"]

            fingerprint = payload_fingerprint(serializer.validated_data, is_id_valid)
            if fingerprint == resource.version_hash and not isEditingPermissions and is_id_valid == resource.was_id_validated:
                self.check_replacement(ResourceSerializer(resource).data)
                return Response({'no_changes': True, 'detail': 'No changes detected.'})

            resource.visibility = 0
            resource.save()

            # copying the textual id and additionDate to the newly created resource
            # Perhaps we should throw a validation error if there was a change
            # attempt on the biotoolsID or biotoolsCURIE
            # Note that we need throw errors here we need to throw them before
            # makeing the old resource visibility 0 (see above)
            serializer.save(
                biotoolsID=resource.biotoolsID,
                biotoolsCURIE=resource.biotoolsCURIE,
                additionDate=resource.additionDate,
                owner=resource.owner,
                was_id_validated=is_id_valid,
                homepage_status=resource.homepage_status,
                elixir_badge=resource.elixir_badge,
                version_hash=fingerprint,
            )
            self.check_replacement(serializer.data)
            # issue_function(Resource.objects.get(biotoolsID=serializer.data['biotoolsID'], visibility=1), str(resource.owner))

            # update the existing resource in elastic
            result = es.search(
                index=settings.ELASTIC_SEARCH_INDEX,
                body={
                    "query": {
                        "bool": {
                            "must": [
                                {"match": {"biotoolsID": resource.biotoolsID.lower()}}
                            ]
                        }
                    }
                },
            )
            count = result["hits"]["total"]["value"]
            if count == 1:
                es.index(
                    index=settings.ELASTIC_SEARCH_INDEX,
                    doc_type="_doc",
                    body=serializer.data,
                    id=result["hits"]["hits"][0]["_id"],
                    refresh='wait_for',
                )
            # notify_admins(serializer.data['biotoolsID'], 'Tool UPDATE', 'A tool was updated.')
            if settings.GITHUB_ECOSYSTEM_ON:
                update_ecosystem_tool(serializer.data, str(request.user))
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def check_replacement(self, data):
        """Allow a restricted editor to verify preservation before external writes."""
        pass

    @transaction.atomic
    def delete(self, request, biotoolsID, format=None):
        if request.user.is_superuser:
            resource = self.get_object(biotoolsID, lock=True)
            # setting the visibility of the current resource to 0
            resource.visibility = 0
            resource.save()

            try:
                result = es.search(index=settings.ELASTIC_SEARCH_INDEX,
                                   body={'query': {'match': {'biotoolsID': resource.biotoolsID.lower()}}})
                if result['hits']['total']['value'] > len(result['hits']['hits']):
                    raise ManagementUnavailable('Duplicate index records require administrator repair. Nothing was removed.')
                for hit in result['hits']['hits']:
                    es.delete(
                        index=settings.ELASTIC_SEARCH_INDEX,
                        doc_type="_doc",
                        id=hit['_id'], refresh='wait_for', ignore=[404],
                    )
            except TransportError as exc:
                raise ManagementUnavailable() from exc
            transaction.on_commit(lambda: notify_admins(biotoolsID, "Tool DELETE", "A tool was deleted."))
            if settings.GITHUB_ECOSYSTEM_ON:
                transaction.on_commit(lambda: delete_ecosystem_tool(biotoolsID, str(request.user)))
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"detail": "Only a superuser can remove a resource."},
                status=status.HTTP_403_FORBIDDEN,
            )


# class ResourceDetailVersionList(APIView):
# 	"""
# 	Retrieve a list of versions for a resource
# 	"""
# 	# permission_classes = (IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly)

# 	def get_list(self, biotoolsID):
# 		try:
# 			obj = Resource.objects.filter(visibility=1, biotoolsID__iexact=biotoolsID)
# 			self.check_object_permissions(self.request, obj)
# 			return obj
# 		except Resource.DoesNotExist:
# 			raise Http404

# 	def get(self, request, biotoolsID, version=None, format=None):
# 		resource = self.get_list(biotoolsID)
# 		serializer = VersionLatestSerializer(instance=resource, many=True)
# 		return Response(serializer.data)


class ResourceCreateValidator(APIView):
    """
    Validate creating a resource.
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)
    parser_classes = (JSONParser, XMLSchemaParser, YAMLParser)
    renderer_classes = (
        BrowsableAPIRenderer,
        JSONRenderer,
        XMLSchemaRenderer,
        YAMLRenderer,
    )
    # should also have renderers except the browsableapi one since we don't really need it...

    def post(self, request, format=None):
        # original
        # serializer = ResourceSerializer(data=request.data)

        # with context
        serializer = ResourceSerializer(
            data=request.data, context={"request": request, "request_type": "POST"}
        )
        if serializer.is_valid():
            if (
                not request.user.is_superuser
                and request.data.get("confidence_flag")
                and request.data.get("confidence_flag") != "tool"
            ):
                return Response(
                    {
                        "detail": "Error: Only superusers can add entries with a confidence score other than 'tool'."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResourceUpdateValidator(APIView):
    """
    Validate updating a resource.
    """

    permission_classes = (
        IsAuthenticatedOrReadOnly,
        HasEditPermissionToEditResourceOrReadOnly,
    )
    parser_classes = (JSONParser, XMLSchemaParser, YAMLParser)
    renderer_classes = (
        BrowsableAPIRenderer,
        JSONRenderer,
        XMLSchemaRenderer,
        YAMLRenderer,
    )
    # should also have renderers except the browsableapi one since we don't really need it...

    def get_object(self, biotoolsID):
        try:
            obj = Resource.objects.filter(visibility=1).get(biotoolsID=biotoolsID)
            self.check_object_permissions(self.request, obj)
            return obj
        except Resource.DoesNotExist:
            raise Http404

    def put(self, request, biotoolsID, format=None):
        resource = self.get_object(biotoolsID)
        serializer = ResourceUpdateSerializer(
            data=request.data, context={"request": request, "request_type": "PUT"}
        )
        if serializer.is_valid():
            # only superusers can change confidence_flag from tool to something else
            if not request.user.is_superuser and not (
                check_update_confidence_flag(
                    resource.confidence_flag, request.data.get("confidence_flag")
                )
            ):
                return Response(
                    {
                        "detail": "Error: Cannot change confidence_flag once it has been set to describe a tool."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            return Response(serializer.validated_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
