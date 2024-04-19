from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from elixir.permissions import IsOwnerOrReadOnly, HasEditPermissionToEditResourceOrReadOnly, CanConcludeResourceRequest, IsStaffOrReadOnly
from elixir.models import *
from elixir.serializers import *

class IssueView(APIView):
	"""
	Create, list or modify issues.
	"""
	permission_classes = (IsStaffOrReadOnly, )

	def get(self, request, biotoolsID, issueId=None):
		if not (biotoolsID):
			return Response({'data': None, 'text': 'Missing id.'}, status=status.HTTP_400_BAD_REQUEST)

		issue_qs = Issue.objects.filter(
			resource_biotoolsID__iexact=biotoolsID
		)
		if issueId:
			issue_qs = issue_qs.filter(
				id=issueId
			)
			
		return Response(
			IssueSerializer(
				instance=issue_qs,
				many=True
			).data,
			status=status.HTTP_200_OK
		)

	def post(self, request, biotoolsID, issueId=None):
		if not (biotoolsID):
			return Response({'data': None, 'text': 'Missing id.'}, status=status.HTTP_400_BAD_REQUEST)

		if issueId:
			payload = request.data
			if not payload:
				return Response({'data': None, 'text': 'Missing payload.'}, status=status.HTTP_400_BAD_REQUEST)
			for x in ['comment', 'issue_state']:
				if x not in list(payload.keys()):
					return Response({'data': None, 'text': 'Malformed payload.'}, status=status.HTTP_400_BAD_REQUEST)
			try:
				i = Issue.objects.get(id=issueId)
			except Issue.DoesNotExist:
				return Response({'data': None, 'text': 'Cannot find issue with this ID.'}, status=status.HTTP_404_NOT_FOUND)
			i_type = IssueType.objects.get(type='custom')
			
			if i.issue_type.id != i_type.id:
				return Response({'data': None, 'text': 'Cannot make changes to the non-custom issues.'}, status=status.HTTP_400_BAD_REQUEST)

			if payload.get('issue_state', None) not in ['fixed', 'fail', 'reopened']:
					return Response({'data': None, 'text': 'Malformed payload.'}, status=status.HTTP_400_BAD_REQUEST)

			i_state = IssueState.objects.get(name=payload.get('issue_state'))
			i.issue_state = i_state
			i.comment = payload.get('comment', None)
			i.resolution_actor = str(request.user)
			i.resolution_date = datetime.datetime.now()
			i.save()
			
			return Response(IssueSerializer(instance=i, many=False).data, status=status.HTTP_200_OK)

		payload = request.data
		comment = None
		field_name = None
		field_value = None
		if payload:
			comment = payload.get('comment', None)
			field_name = payload.get('field_name', None)
			field_value = payload.get('field_value', None)
		
		i_state = IssueState.objects.get(name=payload.get('issue_state'))
		i_type = IssueType.objects.get(type='custom')
		i = Issue(
			issue_type=i_type,
			issue_state=i_state,
			resource_biotoolsID=biotoolsID,
			comment=comment,
			creation_actor=str(request.user),
			field_name=field_name,
			field_value=field_value
		)
		i.save()
		i_s = IssueSerializer(instance=i, many=False)

		return Response(i_s.data, status=status.HTTP_201_CREATED)

