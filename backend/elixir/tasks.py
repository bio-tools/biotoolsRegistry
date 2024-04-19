# from celery import shared_task
from elixir.models import StatsData
import elixir.stats as stats
from elixir.models import *
from elixir.issues import *
import datetime, django.utils.timezone
from django.utils import timezone
import time
from datetime import datetime, timedelta
from datetime import date
import django.db
import requests
import json
import requests
from elixir.publication_metadata import update_publication

def backup_stats_with_date(upperDateLimit=datetime.today()):
    #django.db.close_connection()
    statsData = StatsData()
    statsData.data = stats.StatsInfo().statsData(10, upperDateLimit)
    statsData.totalEntries = statsData.data['totalEntries']
    statsData.creditAffiliationCount = 0 # statsData.data['creditAffiliationCount']
    statsData.edamAnnotationsCount = statsData.data['edamAnnotationsCount']
    statsData.formatAnnotationsCount = statsData.data['formatAnnotationsCount']
    statsData.functionAnnotationsCount = statsData.data['functionAnnotationsCount']
    statsData.topicAnnotationsCount = statsData.data['topicAnnotationsCount']
    statsData.dataTypeAnnotationsCount = statsData.data['dataTypeAnnotationsCount']
    # annotations stats
    statsData.nameAnnotationCount = statsData.data["totalAnnotationCount"]["nameAnnotationCount"]
    statsData.uniqueIDAnnotationCount = statsData.data["totalAnnotationCount"]["uniqueIDAnnotationCount"]
    statsData.topicAnnotationCount = statsData.data["totalAnnotationCount"]["topicAnnotationCount"]
    statsData.operatingSystemAnnotationCount = statsData.data["totalAnnotationCount"]["operatingSystemAnnotationCount"]
    statsData.codeAvailabilityAnnotationCount = statsData.data["totalAnnotationCount"]["codeAvailabilityAnnotationCount"]
    statsData.operationAnnotationCount = statsData.data["totalAnnotationCount"]["operationAnnotationCount"]
    statsData.descriptionAnnotationCount = statsData.data["totalAnnotationCount"]["descriptionAnnotationCount"]
    statsData.downloadsAnnotationCount = statsData.data["totalAnnotationCount"]["downloadsAnnotationCount"]
    statsData.dataFormatsAnnotationCount = statsData.data["totalAnnotationCount"]["dataFormatsAnnotationCount"]
    statsData.accessibilityAnnotationCount = statsData.data["totalAnnotationCount"]["accessibilityAnnotationCount"]
    statsData.toolTypeAnnotationCount = statsData.data["totalAnnotationCount"]["toolTypeAnnotationCount"]
    statsData.documentationAnnotationCount = statsData.data["totalAnnotationCount"]["documentationAnnotationCount"]
    statsData.inputOutputAnnotationCount = statsData.data["totalAnnotationCount"]["inputOutputAnnotationCount"]
    statsData.communityAnnotationCount = statsData.data["totalAnnotationCount"]["communityAnnotationCount"]
    statsData.contactAnnotationCount = statsData.data["totalAnnotationCount"]["contactAnnotationCount"]
    statsData.homepageAnnotationCount = statsData.data["totalAnnotationCount"]["homepageAnnotationCount"]
    statsData.publicationAnnotationCount = statsData.data["totalAnnotationCount"]["publicationAnnotationCount"]
    statsData.save()
    statsData.date = upperDateLimit
    statsData.save()
    return "Statistics for " + str(statsData.totalEntries) + " entries saved sucessfully."

# @shared_task
def backup_stats():
    backup_stats_with_date()

def check_publications(queryset, user):
    pass
    # NoPublicationIssue(queryset, user).report()
    # NonePublicationIssue(queryset, user).report()

def check_broken_links(queryset, user):
    pass
    # URLHomepageIssue(queryset, user).report()
    # URLCreditIssue(queryset, user).report()
    # URLContactIssue(queryset, user).report()
    # URLDownloadIssue(queryset, user).report()
    # URLDocumentationIssue(queryset, user).report()
    # URLLinkIssue(queryset, user).report()


def check_EDAM(queryset, user):
    pass
    # EDAMTopicIssue(queryset, user).report()
    # EDAMOperationIssue(queryset, user).report()
    # EDAMDataIssue(queryset, user).report()
    # EDAMFormatIssue(queryset, user).report()


# @shared_task
def qa_qc_task():
    pass
    # _q = Resource.objects.all()
    # check_publications(_q, 'system')
    # check_broken_links(_q)
    # NoContactIssue(_q, 'system').report()
    # NoTOSIssue(_q, 'system').report()
    # NoLicenseIssue(_q, 'system').report()
    # check_EDAM(_q, 'system')


# @shared_task
def update_publication_metadata():
    currentPublicationIndex = 1
    publicationCount = Publication.objects.count()
    for publication in Publication.objects.all(): 
        #print("Processing publication " + str(currentPublicationIndex) + " out of " + str(publicationCount))
        update_publication(publication)
        currentPublicationIndex = currentPublicationIndex + 1

# @shared_task
def update_pmcid_only_publication_metadata():
    currentPublicationIndex = 1
    pubs = [p for p in Publication.objects.filter(pmcid__isnull=False).select_related('resource') if p.resource.visibility == 1]
    publicationCount = len(pubs)
    for publication in pubs: 
        print(("Processing publication " + str(currentPublicationIndex) + " out of " + str(publicationCount)))
        update_publication(publication)
        currentPublicationIndex = currentPublicationIndex + 1


# @shared_task
def genereate_missing_stats():
    monthsCount = 12
    currentMonth = datetime.today().replace(day=1)
    for i in range(12):
        backup_stats_with_date(currentMonth)
        currentMonth = (currentMonth - timedelta(days=1)).replace(day=1)


# Background tasks
from background_task import background
from django.contrib.auth.models import User

@background(schedule=60)
def notify_user(user_id):
    # lookup user by id and send them a message
    user = User.objects.get(pk=user_id)
    user.email_user('Here is a notification', 'You have been notified')

# Background tasks
from django.conf import settings
from django.core.mail import send_mail

@background(schedule=60)
def notify_admins(identifier, subject, message):
    final_message = message + '\n' + 'ID:' + identifier
    send_mail(
        subject, 
        final_message,
        settings.DEFAULT_FROM_EMAIL,
        settings.ADMIN_EMAIL_LIST
    )

@background(schedule=60)
def notify_resource_request(type, request_body):
    send_mail(
        "Resource " +  type + " request", 
        request_body,
        settings.DEFAULT_FROM_EMAIL,
        settings.ADMIN_EMAIL_LIST
    )

# Ecosytem background tasks
# import the ecosytem_handle_tool_operations which handles the create, update and delete ecosystem operations
from elixir.biotools_to_github import ecosytem_handle_tool_operations

@background(schedule=30)
def create_ecosystem_tool(tool, user):
    # We might need to clean the tool before if we don't accept "empty" properties

    # Convert to string and pretty format
    tool_json = json.dumps(
        tool,
        sort_keys=True,
        indent=4,
        separators=(',', ': ')
    )
    ecosytem_handle_tool_operations(user, tool_json, 'CREATE')
    

@background(schedule=30)
def update_ecosystem_tool(tool, user):
    # We might need to clean the tool before if we don't accept "empty" properties
    
    # Convert to string and pretty format
    tool_json = json.dumps(
        tool,
        sort_keys=True,
        indent=4,
        separators=(',', ': ')
    )
    ecosytem_handle_tool_operations(user, tool_json, 'UPDATE')

@background(schedule=30)
def delete_ecosystem_tool(tool_id, user):
    # Convert to string and pretty format a minimal tool JSON with only the biotoolsID
    tool_json = json.dumps(
        {"biotoolsID":tool_id},
        sort_keys=True,
        indent=4,
        separators=(',', ': ')
    )

    ecosytem_handle_tool_operations(user, tool_json, 'DELETE')