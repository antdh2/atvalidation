import os
from .models import Profile, Picklist, Validation, ValidationGroup, ValidationGroupRule, Entity, Company
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from django.http import HttpResponseRedirect
import json

############################################################
#
# This is for the picklist module
#
############################################################

def create_picklist(request):
    picklist_messages = []
    if request.user.profile.company == None or request.user.profile.company.name == "No Company" or request.user.profile.company.id == 1:
        return False
    string = "create_picklist_module --username {} --password {} atvar-{}.py".format(request.user.profile.autotask_username, request.user.profile.autotask_password, request.user.profile.company.id)
    picklist_messages.append("<div class='note note-info'>Creating picklist...this can take a while depending on the size of your database.</div>")
    os.system(string)
    picklist_messages.append("<div class='note note-info'>Created picklist module for company {} </div>".format(request.user.profile.company.name))
    return True


def create_picklist_database(request):
    picklist_messages = []
    created = False
    if request.user.profile.company == None or request.user.profile.company.name == "No Company" or request.user.profile.company.id == 1:
        messages.add_message(request, messages.ERROR, '<div class="note note-danger">You must create/join a company and have valid Autotask credentials before creating a picklist.</div>')
        return redirect('index')
    # First we must delete any existing picklists or they will be added to exponentially
    picklist_messages.append("<div class='note note-info'>Deleting existing picklist database...</div>")
    picklists = Picklist.objects.filter(company=request.user.profile.id)
    for picklist in picklists:
        picklist.delete()
    string = "create_picklist_module --username {} --password {} atvar-{}.py".format(request.user.profile.autotask_username, request.user.profile.autotask_password, request.user.profile.company.id)
    picklist_messages.append("<div class='note note-info'>Creating picklist...this can take a while depending on the size of your database.</div>")
    os.system(string)
    picklist_messages.append("<div class='note note-info'>Created picklist module for company {} </div>".format(request.user.profile.company.name))
    file = open('atvar-{}.py'.format(request.user.profile.company.id), 'r')
    picklist_messages.append("<div class='note note-info'>Writing new picklist entities into database...</div>")
    for line in file.readlines():
        # Split the line by whitespace giving ['Account_TerritoryID_Local', '=', '29682778']
        line_array = line.split()
        # Set the key to array index 0 to get left side of string, ie. Account_TerritoryID_Local
        db_key = line_array[0]
        # Now select third element in index 2, ie. 29682778
        db_value = line_array[2]
        Picklist.objects.create(company=request.user.profile.company, key=db_key, value=db_value)
    picklist_messages.append("<div class='note note-success'>Added all picklist entities to database</div>")
    cleaned_picklist_message = ''
    for msg in picklist_messages:
        cleaned_picklist_message += msg
    messages.add_message(request, messages.WARNING, mark_safe(cleaned_picklist_message))
    # return redirect('profile', request.user.id)


def ajax_create_picklist(request):
    if request.method == "POST":
        create_picklist_database(request)
        django_messages = []
        for message in messages.get_messages(request):
            django_messages.append({
                "level": message.level_tag,
                "message": message.message,
                "extra_tags": message.tags,
        })
        django_messages.append({"picklist": True})
        return HttpResponse(json.dumps(django_messages), content_type="application/json")
    else:
        return HttpResponse(json.dumps({"nothing to see": "this isn't happening"}), content_type="application/json")


def create_picklist_dict(dict_name, index, regex):
    file = open('atvar.py', 'r')
    for line in file.readlines():
        my_line = line
        if re.search(regex, line):
            line_array = line.split()
            # This splits the left side of the equasion into an array seperated by underscore
            dict_key_parse = line_array[0].split("_", 3)
            # Then we grab the specific array we want for key name
            dict_key = dict_key_parse[index] # we want 2
            # Now to build the atvar string and we must convert to int for conditions to work
            dict_value = int(line_array[2])
            dict_name[dict_key] = dict_value
    return dict_name
