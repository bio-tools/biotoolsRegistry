from elixir.models import Resource, StatsData
from elixir.serializers import *
from django.db.models import Count
import time
from datetime import datetime, timedelta
from datetime import date
import elixir.elixir_logging as elixir_logging
import collections

class StatsInfo():
	# historic data handling
	def statsDataForLast(self, days):
		return StatsData.objects.filter(date__gte=datetime.now()-timedelta(days=days)).order_by('date')

	def totalEntriesForLast(self, months):
		stats = self.statsDataForLast(months * 30)
		entriesStats = []
		lastAddedDate = datetime.today()
		for index, stat in enumerate(stats):
			# not last stats entry
			if index < len(stats) - 1:
				# check if a given month already exists 
				if stat.date.month != lastAddedDate.month and stat.date.month != stats[index+1].date.month:
					entriesStats.append(self.generateStatsEntry(stat))
					lastAddedDate = stat.date
			else:
				# check if a given month already exists 
				if stat.date.month != lastAddedDate.month:
					entriesStats.append({"date": stat.date, 
						"entriesCount": self.totalEntries(), 
						"creditAffiliationCount": stat.creditAffiliationCount,
						"dataTypeAnnotationsCount": self.dataTypeAnnotationsCount(), 
						"edamAnnotationsCount": self.edamAnnotationCount(), 
						"formatAnnotationsCount": self.formatAnnotationsCount(), 
						"functionAnnotationsCount": self.functionAnnotationsCount(), 
						"topicAnnotationsCount": self.topicAnnotationsCount()})
					lastAddedDate = stat.date
		return entriesStats

	def generateStatsEntry(self, stat):
		return {"date": stat.date, "entriesCount": stat.totalEntries, 
				"creditAffiliationCount": stat.creditAffiliationCount,
				"dataTypeAnnotationsCount": stat.dataTypeAnnotationsCount, 
				"edamAnnotationsCount": stat.edamAnnotationsCount, 
				"formatAnnotationsCount": stat.formatAnnotationsCount, 
				"functionAnnotationsCount": stat.functionAnnotationsCount, 
				"topicAnnotationsCount": stat.topicAnnotationsCount}

	def totalAnnotationsCountForLast(self, months):
		stats = self.statsDataForLast(months * 30)
		annotationStats = []
		lastAddedDate = datetime.today()
		for index, stat in enumerate(stats):
			# not last stats entry
			if index < len(stats) - 1:
				# check if a given month already exists 
				if stat.date.month != lastAddedDate.month and stat.date.month != stats[index+1].date.month:
					annotationStats.append(self.generateTotalAnnotationsCount(stat))
					lastAddedDate = stat.date
			else:
				# check if a given month already exists 
				if stat.date.month != lastAddedDate.month:
					latestAnnotationCounts = self.totalAnnotationCount()
					latestAnnotationCounts.update({"date": stat.date})
					annotationStats.append(latestAnnotationCounts)
					lastAddedDate = stat.date
		return annotationStats

	def generateTotalAnnotationsCount(self, stat):
		return {"date": stat.date, 
				"nameAnnotationCount": stat.nameAnnotationCount,
				"uniqueIDAnnotationCount": stat.uniqueIDAnnotationCount,
				"topicAnnotationCount": stat.topicAnnotationCount,
				"operatingSystemAnnotationCount": stat.operatingSystemAnnotationCount,
				"codeAvailabilityAnnotationCount": stat.codeAvailabilityAnnotationCount,
				"operationAnnotationCount": stat.operationAnnotationCount,
				"descriptionAnnotationCount": stat.descriptionAnnotationCount,
				"downloadsAnnotationCount": stat.downloadsAnnotationCount,
				"dataFormatsAnnotationCount": stat.dataFormatsAnnotationCount,
				"accessibilityAnnotationCount": stat.accessibilityAnnotationCount,
				"toolTypeAnnotationCount": stat.toolTypeAnnotationCount,
				"documentationAnnotationCount": stat.documentationAnnotationCount,
				"inputOutputAnnotationCount": stat.inputOutputAnnotationCount,
				"communityAnnotationCount": stat.communityAnnotationCount,
				"contactAnnotationCount": stat.contactAnnotationCount,
				"homepageAnnotationCount": stat.homepageAnnotationCount,
				"publicationAnnotationCount": stat.publicationAnnotationCount
				}

	# current data handling
	def statsData(self, query_limit, upperDateLimit=datetime.today()):
		data = {}
		data['date'] = upperDateLimit.strftime('%c %Z')
		data['totalEntries'] = self.totalEntries(upperDateLimit)
		data['totalUsers'] = self.totalUsers(upperDateLimit)
		# data['entriesByResourceType'] = self.resourceTypeList()
		# data['entriesByInterfaceType'] = self.interfaceTypeList()
		# data['creditAffiliationCount'] = self.creditAffiliationCount()
		# data['entriesByAffiliation'] = self.entriesByAffiliation()
		# data['topSearchStats'] = self.topSearchStats(query_limit)
		data['edamAnnotationsCount'] = self.edamAnnotationCount(upperDateLimit)
		data['functionAnnotationsCount'] = self.functionAnnotationsCount(upperDateLimit)
		data['topicAnnotationsCount'] = self.topicAnnotationsCount(upperDateLimit)
		data['formatAnnotationsCount'] = self.formatAnnotationsCount(upperDateLimit)
		data['dataTypeAnnotationsCount'] = self.dataTypeAnnotationsCount(upperDateLimit)
		data['topTopics'] = self.topTopics(query_limit, upperDateLimit)
		data['topFunctions'] = self.topFunctions(query_limit, upperDateLimit)
		data['topDataTypes'] = self.topDataTypes(query_limit, upperDateLimit)
		data['topDataFormats'] = self.topDataFormats(query_limit, upperDateLimit)
		data['topContributors'] = self.topContributors(query_limit, upperDateLimit)
		data['totalAnnotationCount'] = self.totalAnnotationCount(upperDateLimit)
		self.userGrowthByMonth()
		return data

	def totalEntries(self, upperDateLimit=datetime.today()):
		return Resource.objects.filter(visibility=1, additionDate__lt=upperDateLimit).count()

	def totalUsers(self, upperDateLimit=datetime.today()):
		return User.objects.filter(date_joined__lt=upperDateLimit).count()

	def edamAnnotationCount(self, upperDateLimit=datetime.today()):
		edamAnnotations = 0
		edamAnnotations += Operation.objects.filter(function__resource__visibility=1, additionDate__lt=upperDateLimit).count()
		edamAnnotations += Topic.objects.filter(resource__visibility=1, additionDate__lt=upperDateLimit).count()
		edamAnnotations += Format.objects.filter(input__function__resource__visibility=1, additionDate__lt=upperDateLimit).count()
		edamAnnotations += Format.objects.filter(output__function__resource__visibility=1, additionDate__lt=upperDateLimit).count()
		edamAnnotations += Data.objects.filter(input__function__resource__visibility=1, additionDate__lt=upperDateLimit).count()
		edamAnnotations += Data.objects.filter(output__function__resource__visibility=1, additionDate__lt=upperDateLimit).count()
		return edamAnnotations

	def functionAnnotationsCount(self, upperDateLimit=datetime.today()):
		return Operation.objects.filter(function__resource__visibility=1, additionDate__lt=upperDateLimit).count()

	def topicAnnotationsCount(self, upperDateLimit=datetime.today()):
		return Topic.objects.filter(resource__visibility=1, additionDate__lt=upperDateLimit).count()

	def formatAnnotationsCount(self, upperDateLimit=datetime.today()):
		formatAnnotations = 0
		formatAnnotations += Format.objects.filter(input__function__resource__visibility=1, additionDate__lt=upperDateLimit).count()
		formatAnnotations += Format.objects.filter(output__function__resource__visibility=1, additionDate__lt=upperDateLimit).count()
		return formatAnnotations

	def dataTypeAnnotationsCount(self, upperDateLimit=datetime.today()):
		dataAnnotations = 0
		dataAnnotations += Data.objects.filter(input__function__resource__visibility=1, additionDate__lt=upperDateLimit).count()
		dataAnnotations += Data.objects.filter(output__function__resource__visibility=1, additionDate__lt=upperDateLimit).count()
		return dataAnnotations

	def topTopics(self, limit, upperDateLimit=datetime.today()):
		topicCountList = Topic.objects.exclude(term="N/A").filter(resource__visibility=1, additionDate__lt=upperDateLimit).values('term').annotate(count=Count('term'))
		topicCountList = sorted(topicCountList, key=lambda topic: topic['count'], reverse = True)[:limit]
		topicCountData = [{"topic": topic["term"], "count": topic["count"]} for topic in topicCountList]
		topicCountData = [data for data in topicCountData if data["topic"] != "Topic"]
		return topicCountData

	def topFunctions(self, limit, upperDateLimit=datetime.today()):
		functionCountList = Operation.objects.exclude(term="N/A").filter(function__resource__visibility=1, additionDate__lt=upperDateLimit).values('term').annotate(count=Count('term'))
		functionCountList = sorted(functionCountList, key=lambda function: function['count'], reverse = True)[:limit]
		topicCountData = [{"function": function["term"], "count": function["count"]} for function in functionCountList]
		topicCountData = [data for data in topicCountData if data["function"] != "Operation"]
		return topicCountData

	def topDataTypes(self, limit, upperDateLimit=datetime.today()):
		dataTypeCountList = Data.objects.filter(input__function__resource__visibility=1, additionDate__lt=upperDateLimit).values('term').annotate(count=Count('term'))
		dataTypeCountList = sorted(dataTypeCountList, key=lambda dataType: dataType['count'], reverse = True)[:limit]
		dataTypeCountData = [{"dataType": dataType["term"], "count": dataType["count"]} for dataType in dataTypeCountList]
		dataTypeCountData = [data for data in dataTypeCountData if data["dataType"] != "Data"]
		return dataTypeCountData
		
	def topDataFormats(self, limit, upperDateLimit=datetime.today()):
		dataFormatCountList = Format.objects.filter(input__function__resource__visibility=1, additionDate__lt=upperDateLimit).values('term').annotate(count=Count('term'))
		dataFormatCountList = sorted(dataFormatCountList, key=lambda dataFormat: dataFormat['count'], reverse = True)[:limit]
		dataFormatCountData = [{"dataFormat": dataFormat["term"], "count": dataFormat["count"]} for dataFormat in dataFormatCountList]
		dataFormatCountData = [data for data in dataFormatCountData if data["dataFormat"] != "Format"]
		return dataFormatCountData

	def topContributors(self, limit, upperDateLimit=datetime.today()):
		emailsList = User.objects.filter(date_joined__lt=upperDateLimit).values('email')
		emailsList = [data for data in emailsList if data['email'] != None and data['email'] != '' and '@' in data['email']] # discard empty emails
		emailsList = [data['email'].split(".").pop() for data in emailsList] # extract domains
		emailsList = collections.Counter(emailsList) # count occurences
		emailsList = emailsList.most_common(limit) # sort and limit occurences
		emailsList = [{ 'domain': data[0], 'count': data[1]} for data in emailsList] # format data
		return emailsList

	def totalAnnotationCount(self, upperDateLimit=datetime.today()):
		annotationInfo = {}
		annotationInfo.update(self.nameAnnotationCount(upperDateLimit))
		annotationInfo.update(self.descriptionAnnotationCount(upperDateLimit))
		annotationInfo.update(self.homepageAnnotationCount(upperDateLimit))
		annotationInfo.update(self.toolTypeAnnotationCount(upperDateLimit))
		annotationInfo.update(self.uniqueIDAnnotationCount(upperDateLimit))
		annotationInfo.update(self.topicAnnotationCount(upperDateLimit))
		annotationInfo.update(self.publicationAnnotationCount(upperDateLimit))
		annotationInfo.update(self.contactAnnotationCount(upperDateLimit))
		annotationInfo.update(self.operationAnnotationCount(upperDateLimit))
		annotationInfo.update(self.documentationAnnotationCount(upperDateLimit))
		annotationInfo.update(self.operatingSystemAnnotationCount(upperDateLimit))
		annotationInfo.update(self.inputOutputAnnotationCount(upperDateLimit))
		annotationInfo.update(self.codeAvailabilityAnnotationCount(upperDateLimit))
		annotationInfo.update(self.accessibilityAnnotationCount(upperDateLimit))
		annotationInfo.update(self.dataFormatsAnnotationCount(upperDateLimit))
		annotationInfo.update(self.communityAnnotationCount(upperDateLimit))
		annotationInfo.update(self.downloadsAnnotationCount(upperDateLimit))
		return annotationInfo

	def nameAnnotationCount(self, upperDateLimit=datetime.today()):
		return {'nameAnnotationCount': Resource.objects.filter(visibility=1, additionDate__lt=upperDateLimit).exclude(name="").count()}

	def descriptionAnnotationCount(self, upperDateLimit=datetime.today()):
		return {'descriptionAnnotationCount': Resource.objects.filter(visibility=1, additionDate__lt=upperDateLimit).exclude(description="").count()}

	def homepageAnnotationCount(self, upperDateLimit=datetime.today()):
		return {'homepageAnnotationCount': Resource.objects.filter(visibility=1, additionDate__lt=upperDateLimit).exclude(homepage="").count()}

	def toolTypeAnnotationCount(self, upperDateLimit=datetime.today()):
		return {'toolTypeAnnotationCount':  ToolType.objects.filter(resource__visibility=1, additionDate__lt=upperDateLimit).count()}

	def uniqueIDAnnotationCount(self, upperDateLimit=datetime.today()):
		return {'uniqueIDAnnotationCount': Resource.objects.filter(visibility=1, additionDate__lt=upperDateLimit).exclude(biotoolsID="").count()}

	def topicAnnotationCount(self, upperDateLimit=datetime.today()):
		return {'topicAnnotationCount': Topic.objects.filter(resource__visibility=1, additionDate__lt=upperDateLimit).count()}

	def publicationAnnotationCount(self, upperDateLimit=datetime.today()):
		return {'publicationAnnotationCount': Publication.objects.filter(resource__visibility=1, additionDate__lt=upperDateLimit).count()}

	def contactAnnotationCount(self, upperDateLimit=datetime.today()):
		return {'contactAnnotationCount': Contact.objects.filter(resource__visibility=1, additionDate__lt=upperDateLimit).count()}

	def operationAnnotationCount(self, upperDateLimit=datetime.today()):
		return {'operationAnnotationCount': Operation.objects.filter(function__resource__visibility=1, additionDate__lt=upperDateLimit).count()}

	def documentationAnnotationCount(self, upperDateLimit=datetime.today()):
		return {'documentationAnnotationCount': Documentation.objects.filter(resource__visibility=1, additionDate__lt=upperDateLimit).count()}

	def operatingSystemAnnotationCount(self, upperDateLimit=datetime.today()):
		return {'operatingSystemAnnotationCount': OperatingSystem.objects.filter(resource__visibility=1, additionDate__lt=upperDateLimit).count()}

	def inputOutputAnnotationCount(self, upperDateLimit=datetime.today()):
		count = 0
		count += Input.objects.filter(function__resource__visibility=1, additionDate__lt=upperDateLimit).count()
		count += Output.objects.filter(function__resource__visibility=1, additionDate__lt=upperDateLimit).count()
		return {'inputOutputAnnotationCount': count}

	def codeAvailabilityAnnotationCount(self, upperDateLimit=datetime.today()):
		count = 0
		count += Language.objects.filter(resource__visibility=1, additionDate__lt=upperDateLimit).count()
		count += Resource.objects.filter(visibility=1, additionDate__lt=upperDateLimit).exclude(license__isnull=True).exclude(license="").count()
		count += Download.objects.filter(resource__visibility=1, additionDate__lt=upperDateLimit).count()
		return {'codeAvailabilityAnnotationCount': count}

	def accessibilityAnnotationCount(self, upperDateLimit=datetime.today()):
		return {'accessibilityAnnotationCount': Resource.objects.filter(visibility=1,additionDate__lt=upperDateLimit).exclude(accessibility__isnull=True).exclude(accessibility="").count()}

	def dataFormatsAnnotationCount(self, upperDateLimit=datetime.today()):
		count = 0
		count += Format.objects.filter(input__function__resource__visibility=1, additionDate__lt=upperDateLimit).count()
		count += Format.objects.filter(output__function__resource__visibility=1, additionDate__lt=upperDateLimit).count()
		return {'dataFormatsAnnotationCount': count}

	def communityAnnotationCount(self, upperDateLimit=datetime.today()):
		return {'communityAnnotationCount': Link.objects.filter(resource__visibility=1, additionDate__lt=upperDateLimit).count()}

	def downloadsAnnotationCount(self, upperDateLimit=datetime.today()):
		return {'downloadsAnnotationCount': Download.objects.filter(resource__visibility=1, additionDate__lt=upperDateLimit).count()}
		
	def topSearchStats(self, limit):
		return elixir_logging.search_log_json_data()[:limit]
		
	# def resourceTypeList(self):
	# 	resourceTypeList = ResourceType.objects.filter(resource__visibility=1).values('name').annotate(count=Count('name'))
	# 	resourceTypeList = sorted(resourceTypeList, key=lambda resourceType: resourceType['count'], reverse = True)
	# 	return [{'resourceType': elem['name'], 'count': elem['count']} for elem in resourceTypeList]
		
	# def interfaceTypeList(self):
	# 	interfaceTypeList = Interface.objects.filter(resource__visibility=1).values('interfaceType').annotate(count=Count('interfaceType'))
	# 	return sorted(interfaceTypeList, key=lambda interfaceType: interfaceType['count'], reverse = True)

	def userGrowthByMonth(self):
		qs = (User.objects.all().
    	extra(select={
        	'month': "EXTRACT(month FROM date_joined)",
        	'year': "EXTRACT(year FROM date_joined)",
    	}).
    	values('month', 'year').
    	annotate(count_items=Count('date_joined')))

		user_stats = []
		# Create stats for users
		for idx, item in enumerate(qs):
			user_data = {}
			user_data["date"] = datetime(year=int(item['year']), month=int(item['month']), day=1).strftime('%Y-%m-%dT%H:%M:%SZ')
			user_data["newUsersCount"] = item["count_items"]
			if idx == 0:	
				user_data["totalUsersCount"] = item["count_items"]
			else:
				user_data["totalUsersCount"] = item["count_items"] + user_stats[idx-1]["totalUsersCount"]
			user_stats.append(user_data)

		return user_stats
		
	# def creditAffiliationCount(self):
	# 	return CreditsAffiliation.objects.values('name').distinct().count()
	
	# def entriesByAffiliation(self):
	# 	entriesByAffiliationList = CreditsAffiliation.objects.filter(credits__resource__visibility=1).values('name').annotate(count=Count('name'))
	# 	entriesByAffiliationList = sorted(entriesByAffiliationList, key=lambda affiliation: affiliation['count'], reverse = True)
	# 	dataFormatCountData = [{"affiliation": affiliation["name"], "count": affiliation["count"]} for affiliation in entriesByAffiliationList]
	# 	return dataFormatCountData