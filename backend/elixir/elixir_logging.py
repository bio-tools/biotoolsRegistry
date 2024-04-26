from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from elixir.models import SearchTermLog, SearchQueryLog
import elixir.search_settings


#######################################################################################################################
# Serialization
#######################################################################################################################

class SearchTermLogSerializer(serializers.ModelSerializer):
	name = serializers.CharField()
	term = serializers.CharField()

	class Meta:
		model = SearchTermLog
		fields = ['name', 'term']


class SearchQueryLogSerializer(serializers.ModelSerializer):
	terms = SearchTermLogSerializer(many=True, read_only=True)

	class Meta:
		model = SearchQueryLog
		fields = ['terms']


#######################################################################################################################
# Interface
#######################################################################################################################

class SearchLogger:
	# initialization and operations
	def __init__(self, query):
		self.query = query

	def commit(self):
		serializer_data = self.construct_serializer_dict()
		query_log = self.query_log(serializer_data)
		if query_log:
			for term in serializer_data['terms']:
				query_term = self.query_log_terms(data=term)
				query_log.terms.add(query_term)

	# data operations
	def query_log(self, data):
		query_serializer = SearchQueryLogSerializer(data=data)
		if query_serializer.is_valid():
			return query_serializer.save()
		return

	def query_log_terms(self, data):
		# if log already exists in the database just return it
		exsiting_log_term = SearchTermLog.objects.filter(name=data['name'], term=data['term'])
		if exsiting_log_term.count() > 0:
			return exsiting_log_term[0]
		# in case the log does not exsist create a new one
		term_serializer = SearchTermLogSerializer(data=data)
		if term_serializer.is_valid():
			return term_serializer.save()
		return

	# data transformations
	def construct_serializer_dict(self):
		serizalizer_term_dict = []
		term_dict = self.strip_query_control_elements(self.query)
		for term_id in term_dict:
			for term in term_dict[term_id]:
				# Invalid search term do not log.
				if term != '':
					# Make sure that the data fits in the database.
					serizalizer_term_dict.append({'name': term_id, 'term': term[0:32]})
		return {'terms': serizalizer_term_dict}

	def strip_query_control_elements(self, query):
		stripped_dict = dict(query)
		if 'sort' in stripped_dict:
			del stripped_dict['sort']
		if 'ord' in stripped_dict:
			del stripped_dict['ord']
		return stripped_dict
		
# data access
def search_log_json_data():
	searchTerms = SearchTermLog.objects.all()
	searchTermsData = []
	for term in searchTerms:
		termSerializer = SearchTermLogSerializer(term)
		termData = {}
		termData['type'] = 'query' if (termSerializer.data['name'] == 'q') else termSerializer.data['name']
		termData['term'] = termSerializer.data['term']
		termData['count'] = len(term.queries.all())
		searchTermsData.append(termData)
	return sorted(searchTermsData, key=lambda term: term['count'], reverse = True)
