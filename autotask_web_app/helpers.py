from django.shortcuts import render, redirect
from django.shortcuts import render_to_response
from django.contrib import messages
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.files import File
from django.utils.safestring import mark_safe

import time
import datetime
from datetime import datetime
from datetime import timedelta
import os
import re
import atws
import atws.monkeypatch.attributes
import account.views
import account.forms
import autotask_web_app.forms
import operator
import json
from autotask_web_app.models import Profile, Picklist, Validation, ValidationGroup, ValidationGroupRule, Entity, Company

def validate_input(request, valgrouprules):
    error_message = []
    validated = True
    # Grab all validation group rules from function input (all of these are specific to users company)
    validation_group_rules = valgrouprules
    for v in validation_group_rules:
        # For straight up strings
        # This segment of code is ONLY triggered when the validation trigger is a string matching a strings
        # e.g. "Title" == "MOT Ticket" rather than the other scenario which is "QueueID" = 28723212
        if OPERATORS[v.operator](request.POST[v.key], v.value):
            # If the rule has triggered - lets get all validations for this rules group
            error_message.append("<strong>Validation Group " + "''" + v.validation_group.name + "''" + " has been triggered by the following rule</strong><br>" + v.key + " " + v.operator + " " + v.value + ".<br>" + "<small>Validation errors will appear below</small><br><br>")
            validations = Validation.objects.filter(validation_group=v.validation_group)
            # Now we cycle through each validation and check if it is true or not
            for validation in validations:
                # First we want to check whether or not the validation is enforced or not
                if validation.mandatory:
                    # If it is, we need to check whether this is a picklist entity or not, -100 means it isn't and value must be a string
                    if validation.picklist_number == -100:
                        # If the user input is equal to the validation value (eg. Title = "MOT Ticket")
                        if request.POST[validation.key] == validation.value:
                            # Then we display a success message and skip the rest of the loop for performance
                            pass
                        # If this condition is false then the validation failed and we need to set validated to False and display a helpful error message
                        # Below line equates to eg. "Title" == "MOT Tic" when it should be "MOT Ticket"
                        if not OPERATORS[validation.operator](request.POST[validation.key].lower(), validation.value):
                            error_message.append("<div class='note note-danger'><strong>ERROR:</strong> " + validation.key + " not valid.<br><small>" + validation.key + " must be " + validation.operator + " " + validation.value + "</small></div>")
                    # We also need to check if the validation IS from an Autotask picklist (ie. predetermined values imported from AT db)
                    # Unlike non-picklist entities these are ALWAYS numbers
                    elif validation.picklist_number != -100:
                        # Using a try catch block because we can get invalid literal for int() with base 10 errors due to HTML inputting empty values as ""
                        # which causes the int() function to throw a hissy fit as "" is clearly not an integer.
                        try:
                            # Below equasion would read as "QueueID" == "29736321" a rather simple check
                            # If it's failed validation, set validated to say so and display an error message
                            if not OPERATORS[validation.operator](int(request.POST[validation.key]), validation.picklist_number):
                                validated = False
                                error_message.append("<div class='note note-danger'><strong>ERROR:</strong> " + validation.key + " not valid.<br><small>" + validation.key + " must be " + validation.operator + " " + validation.value + "</small></div>")
                        # As explained above if user input has a select vvalue for e.g which has been left unselected, the POST values will be ""
                        # but we can handle this nicely by saying to the user they forgot to select something which needs to be validated
                        except:
                            error_message.append("<div class='note note-danger'><strong>ERROR:</strong> " + validation.key + " is empty or not selected.<br><small>" + validation.key + " must be " + validation.operator + " " + validation.value + "</small></div>")
                            print("invalid literal for int() with base 10:")
                            validated = False
                # Now if the validation is NOT mandatory, we do the same again but with different error messages
                else:
                    if validation.picklist_number == -100:
                        if request.POST[validation.key] == validation.value:
                            pass
                        if not OPERATORS[validation.operator](request.POST[validation.key].lower(), validation.value):
                            validated = False
                            error_message.append("<div class='note note-warning'><strong>WARNING:</strong> " + validation.key + " may be incorrect.<br><small>" + validation.key + " should be " + validation.operator + " " + validation.value + "<br>Please be aware that this request may be incorrect yet has still been processed as it has been marked as not mandatory." + "</small></div>")
                    elif validation.picklist_number != -100:
                        try:
                            if not OPERATORS[validation.operator](int(request.POST[validation.key]), validation.picklist_number):
                                validated = False
                                error_message.append("<div class='note note-warning'><strong>WARNING:</strong> " + validation.key + " may be incorrect.<br><small>" + validation.key + " should be " + validation.operator + " " + validation.value + "<br>Please be aware that this request may be incorrect yet has still been processed as it has been marked as not mandatory." + "</small></div>")
                        except:
                            error_message.append("<div class='note note-warning'><strong>WARNING:</strong> " + validation.key + " may be incorrect.<br><small>" + validation.key + " should be " + validation.operator + " " + validation.value + "<br>Please be aware that this request may be incorrect yet has still been processed as it has been marked as not mandatory." + "</small></div>")
                            print("invalid literal for int() with base 10: 234")
        # IF we do not have a string match, we then need to check if there is a picklist match
        # e.g checking that a dropdown box matches - "QueueID" == 28723212 would be read as 28723212 == 28723212
        # When using int() we must use a try catch block to process the error if user hasnt selected the appropriate drop down
        try:
            if OPERATORS[v.operator](int(request.POST[v.key]), v.picklist_number):
                error_message.append("<strong>Validation Group " + "''" + v.validation_group.name + "''" + " has been triggered by the following rule</strong><br>" + v.key + " " + v.operator + " " + v.value + ".<br>" + "<small>Validation errors will appear below</small><br><br>")
                # If the rule has triggered - lets get all validations for this rules group
                validations = Validation.objects.filter(validation_group=v.validation_group)
                # Now we cycle through each validation and check if it is true or not
                for validation in validations:
                    # First we want to check whether or not the validation is enforced or not
                    if validation.mandatory:
                        # If it is, we need to check whether this is a picklist entity or not, -100 means it isn't and value must be a string
                        if validation.picklist_number == -100:
                            # If the user input is equal to the validation value (eg. Title = "MOT Ticket")
                            if request.POST[validation.key] == validation.value:
                                # Then we display a success message and skip the rest of the loop for performance
                                pass
                            # If this condition is false then the validation failed and we need to set validated to False and display a helpful error message
                            # Below line equates to eg. "Title" == "MOT Tic" when it should be "MOT Ticket"
                            if not OPERATORS[validation.operator](request.POST[validation.key].lower(), validation.value):
                                validated = False
                                error_message.append("<div class='note note-danger'><strong>ERROR:</strong> " + validation.key + " not valid.<br><small>" + validation.key + " must be " + validation.operator + " " + validation.value + "</small></div>")
                        # We also need to check if the validation IS from an Autotask picklist (ie. predetermined values imported from AT db)
                        # Unlike non-picklist entities these are ALWAYS numbers
                        elif validation.picklist_number != -100:
                            # Using a try catch block because we can get invalid literal for int() with base 10 errors due to HTML inputting empty values as ""
                            # which causes the int() function to throw a hissy fit as "" is clearly not an integer.
                            try:
                                # Below equasion would read as "QueueID" == "29736321" a rather simple check
                                # If it's failed validation, set validated to say so and display an error message
                                if not OPERATORS[validation.operator](int(request.POST[validation.key].lower()), validation.picklist_number):
                                    validated = False
                                    error_message.append("<div class='note note-danger'><strong>ERROR:</strong> " + validation.key + " not valid.<br><small>" + validation.key + " must be " + validation.operator + " " + validation.value + "</small></div>")
                            # As explained above if user input has a select vvalue for e.g which has been left unselected, the POST values will be ""
                            # but we can handle this nicely by saying to the user they forgot to select something which needs to be validated
                            except:
                                error_message.append("<div class='note note-danger'><strong>ERROR:</strong> " + validation.key + " is empty or not selected.<br><small>" + validation.key + " must be " + validation.operator + " " + validation.value + "</small></div>")
                                print("invalid literal for int() with base 10:")
                                validated = False
                    # Now if the validation is NOT mandatory, we do the same again but with different error messages
                    else:
                        if validation.picklist_number == -100:
                            print(request.POST[validation.key])
                            if request.POST[validation.key] == validation.value:
                                pass
                            if not OPERATORS[validation.operator](request.POST[validation.key].lower(), validation.value):
                                validated = False
                                error_message.append("<div class='note note-warning'><strong>WARNING:</strong> " + validation.key + " may be incorrect.<br><small>" + validation.key + " should be " + validation.operator + " " + validation.value + "<br>Please be aware that this request may be incorrect yet has still been processed as it has been marked as not mandatory." + "</small></div>")
                        elif validation.picklist_number != -100:
                            try:
                                if not OPERATORS[validation.operator](int(request.POST[validation.key].lower()), validation.picklist_number):
                                    validated = False
                                    error_message.append("<div class='note note-warning'><strong>WARNING:</strong> " + validation.key + " may be incorrect.<br><small>" + validation.key + " should be " + validation.operator + " " + validation.value + "<br>Please be aware that this request may be incorrect yet has still been processed as it has been marked as not mandatory." + "</small></div>")
                            except:
                                error_message.append("<div class='note note-warning'><strong>WARNING:</strong> " + validation.key + " may be incorrect.<br><small>" + validation.key + " should be " + validation.operator + " " + validation.value + "<br>Please be aware that this request may be incorrect yet has still been processed as it has been marked as not mandatory." + "</small></div>")
                                print("invalid literal for int() with base 10: 555555")
                                print(error_message['6'])
                                validated = False
        except:
            print("invalid literal for int() with base 10: rule trigger not a match")

    cleaned_error_message = ""
    for msg in error_message:
        cleaned_error_message += msg
    messages.add_message(request, messages.INFO, mark_safe(cleaned_error_message))
    return validated

def ataccount(request, id):
    account_id = id
    ataccount = get_account(account_id)
    tickets = get_tickets_for_account(account_id)
    ticket_account_name = resolve_account_name_from_id(account_id)
    ticket_info = get_ticket_info(tickets)
    return render(request, 'account.html', {"ataccount": ataccount, "tickets": tickets, "ticket_account_name": ticket_account_name,  "TICKET_SOURCES": TICKET_SOURCES})

def check_account_exists(account_name):
    aquery = atws.Query('Account')
    aquery.WHERE('AccountName',aquery.Equals,account_name)
    accounts = at.query(aquery).fetch_all()
    if accounts:
        return True
    else:
        return False

def get_contact_for_account(account_id):
    tquery = atws.Query('Contact')
    tquery.WHERE('AccountID',tquery.Equals,account_id)
    contact = at.query(tquery).fetch_one()
    return contact

def get_contacts_for_account(account_id):
    tquery = atws.Query('Contact')
    tquery.WHERE('AccountID',tquery.Equals,account_id)
    contact = at.query(tquery).fetch_all()
    return contact

def get_account(account_id):
    # Then we need to grab a query object using autotask wrapper
    query = atws.Query('Account')
    # Then filter what we want the query object to grab using SQL
    query.WHERE('id',query.Equals,account_id)
    # Assign the generator from query object to a list which we can interact with
    accounts = at.query(query).fetch_one()
    return accounts

def get_tickets_for_account(account_id):
    tquery = atws.Query('Ticket')
    tquery.WHERE('AccountID',tquery.Equals,account_id)
    tickets = at.query(tquery).fetch_all()
    return tickets

def get_ticket_from_id(ticket_id):
    tquery = atws.Query('Ticket')
    tquery.WHERE('id',tquery.Equals,ticket_id)
    ticket = at.query(tquery).fetch_one()
    return ticket

def get_ticket_info(tickets):
    # tickets variable is entered as a LIST of tickets
    # each LIST of tickets have the tuples so I need to loop through each LIST and then unpack into a dict
    ticket_info = {}
    for ticket in tickets:
        i = 0
        for field, value in ticket:
            try:
                ticket_info.update({field:value})
            except ValueError:
                print("Some error with unpacking tuple")
    return ticket_info

def get_individual_ticket_info(ticket):
    ticket_info = {}
    for field, value in ticket:
        try:
            ticket_info.update({field:value})
        except ValueError:
            print("Some error with unpacking tuple")
    return ticket_info

def resolve_account_name(string):
    aquery = atws.Query('Account')
    aquery.WHERE('AccountName',aquery.Contains,string)
    accounts = at.query(aquery).fetch_all()
    return accounts

def resolve_account_id(string):
    aquery = atws.Query('Account')
    aquery.WHERE('AccountName',aquery.Equals,string)
    accounts = at.query(aquery).fetch_one()
    for field, value in accounts:
        if field == "id":
            acc_id = value
        else:
            acc_id = None
        return acc_id

def resolve_account_name_from_id(account_id):
    aquery = atws.Query('Account')
    aquery.WHERE('id',aquery.Equals,account_id)
    accounts = at.query(aquery).fetch_one()
    for field, value in accounts:
        if field == "AccountName":
            account_name = value
            return account_name

def get_resource_from_id(resource_id):
    aquery = atws.Query('Resource')
    aquery.WHERE('id',aquery.Equals,resource_id)
    resource = at.query(aquery).fetch_one()
    return resource

def get_resource_from_username(username):
    aquery = atws.Query('Resource')
    aquery.WHERE('UserName',aquery.Equals,username)
    resource = at.query(aquery).fetch_one()
    return resource

def get_contact_for_ticket(contact_id):
    aquery = atws.Query('Contact')
    aquery.WHERE('id',aquery.Equals,contact_id)
    contact = at.query(aquery).fetch_one()
    return contact

def autotask_login_function(request, username, password):
    try:
        global at
        at_username = username
        at_password = password
        profile = Profile.objects.get(user=request.user)
        profile.autotask_username = username
        profile.autotask_password = password
        profile.save()
        at = atws.connect(username=profile.autotask_username,password=profile.autotask_password)
        return at
    except NameError:
        messages.add_message(request, messages.ERROR, 'Something went wrong')
    except ValueError:
        messages.add_message(request, messages.ERROR, 'Autotask username/password incorrect')

def ticket_create_new(validated, **kwargs):
    new_ticket = at.new('Ticket')
    new_ticket.AccountID = kwargs.get('AccountID', None)
    new_ticket.AEMAlertID = kwargs.get('AEMAlertID', None)
    new_ticket.AllocationCodeID = kwargs.get('AllocationCodeID', None)
    new_ticket.AssignedResourceID = kwargs.get('AssignedResourceID', None)
    new_ticket.AssignedResourceRoleID = kwargs.get('AssignedResourceRoleID', None)
    new_ticket.ChangeApprovalBoard = kwargs.get('ChangeApprovalBoard', None)
    new_ticket.ChangeApprovalStatus = kwargs.get('ChangeApprovalStatus', None)
    new_ticket.ChangeApprovalType = kwargs.get('ChangeApprovalType', None)
    new_ticket.ChangeInfoField1 = kwargs.get('ChangeInfoField1', None)
    new_ticket.ChangeInfoField2 = kwargs.get('ChangeInfoField2', None)
    new_ticket.ChangeInfoField3 = kwargs.get('ChangeInfoField3', None)
    new_ticket.ChangeInfoField4 = kwargs.get('ChangeInfoField4', None)
    new_ticket.ChangeInfoField5 = kwargs.get('ChangeInfoField5', None)
    new_ticket.CompletedDate = kwargs.get('CompletedDate', None)
    new_ticket.ContactID = kwargs.get('ContactID', None)
    new_ticket.ContractID = kwargs.get('ContractID', None)
    new_ticket.CreatorResourceID = kwargs.get('CreatorResourceID', None)
    new_ticket.Description = kwargs.get('Description', None)
    new_ticket.DueDateTime = kwargs.get('DueDateTime', None)
    new_ticket.FirstResponseDateTime = kwargs.get('FirstResponseDateTime', None)
    new_ticket.FirstResponseDueDateTime = kwargs.get('FirstResponseDueDateTime', None)
    new_ticket.HoursToBeScheduled = kwargs.get('HoursToBeScheduled', None)
    new_ticket.InstalledProductID = kwargs.get('InstalledProductID', None)
    new_ticket.IssueType = kwargs.get('IssueType', None)
    new_ticket.LastActivityDate = kwargs.get('LastActivityDate', None)
    new_ticket.LastCustomerNotificationDateTime = kwargs.get('LastCustomerNotificationDateTime', None)
    new_ticket.LastCustomerVisibleActivityDateTime = kwargs.get('LastCustomerVisibleActivityDateTime', None)
    new_ticket.MonitorID = kwargs.get('MonitorID', None)
    new_ticket.MonitorTypeID = kwargs.get('MonitorTypeID', None)
    new_ticket.OpportunityId = kwargs.get('OpportunityId', None)
    new_ticket.Priority = kwargs.get('Priority', None)
    new_ticket.ProblemTicketId = kwargs.get('ProblemTicketId', None)
    new_ticket.PurchaseOrderNumber = kwargs.get('PurchaseOrderNumber', None)
    new_ticket.QueueID = kwargs.get('QueueID', None)
    new_ticket.Resolution = kwargs.get('Resolution', None)
    new_ticket.ResolutionPlanDateTime = kwargs.get('ResolutionPlanDateTime', None)
    new_ticket.ResolutionPlanDueDateTime = kwargs.get('ResolutionPlanDueDateTime', None)
    new_ticket.ResolvedDateTime = kwargs.get('ResolvedDateTime', None)
    new_ticket.ResolvedDueDateTime = kwargs.get('ResolvedDueDateTime', None)
    new_ticket.ServiceLevelAgreementHasBeenMet = kwargs.get('ServiceLevelAgreementHasBeenMet', None)
    new_ticket.ServiceLevelAgreementID = kwargs.get('ServiceLevelAgreementID', None)
    new_ticket.Source = kwargs.get('Source', None)
    new_ticket.Status = kwargs.get('Status', None)
    new_ticket.SubIssueType = kwargs.get('SubIssueType', None)
    new_ticket.TicketNumber = kwargs.get('TicketNumber', None)
    new_ticket.TicketType = kwargs.get('TicketType', None)
    new_ticket.Title = kwargs.get('Title', None)
    ticket = at.create(new_ticket).fetch_one()
    return ticket

def contact_create_new(validated, **kwargs):
    new_contact = at.new('Contact')
    new_contact.FirstName = kwargs.get('FirstName', None)
    new_contact.LastName = kwargs.get('LastName', None)
    new_contact.EMailAddress = kwargs.get('EMailAddress', None)
    new_contact.AddressLine = kwargs.get('AddressLine', None)
    new_contact.AddressLine1 = kwargs.get('AddressLine1', None)
    new_contact.City = kwargs.get('City', None)
    new_contact.ZipCode = kwargs.get('ZipCode', None)
    new_contact.Phone = kwargs.get('Phone', None)
    new_contact.AccountID = kwargs.get('AccountID', None)
    new_contact.Active = 1
    contact = at.create(new_contact).fetch_one()
    return contact

def get_contract_for_ticket(account_id, contract_name):
    aquery = atws.Query('Contract')
    aquery.WHERE('AccountID',aquery.Equals,account_id)
    aquery.WHERE('ContractName',aquery.Equals,contract_name)
    contract = at.query(aquery).fetch_one()
    return contract

def get_resources():
    aquery = atws.Query('Resource')
    aquery.WHERE('id',aquery.GreaterThan,0)
    resources = at.query(aquery).fetch_all()
    return resources

def get_roles():
    aquery = atws.Query('Role')
    aquery.WHERE('id',aquery.GreaterThan,0)
    roles = at.query(aquery).fetch_all()
    return roles

def get_contracts(account_id):
    aquery = atws.Query('Contract')
    aquery.WHERE('AccountID',aquery.Equals,account_id)
    contracts = at.query(aquery).fetch_all()
    return contracts

def get_all_contracts():
    aquery = atws.Query('Contract')
    aquery.WHERE('AccountID',aquery.GreaterThan,-1)
    aquery.WHERE('Status',aquery.Equals,1)
    contracts = at.query(aquery).fetch_all()
    return contracts

def get_allocation_codes():
    aquery = atws.Query('AllocationCode')
    aquery.WHERE('UseType',aquery.Equals,1)
    allocation_codes = at.query(aquery).fetch_all()
    return allocation_codes

def get_contract_services(account_id):
    aquery = atws.Query('ContractService')
    aquery.WHERE('id',aquery.Equals,account_id)
    services = at.query(aquery).fetch_all()
    return services

def get_ticket_type_picklist():
    ticket_types = Picklist.objects.filter(key__icontains="Ticket_TicketType")
    return ticket_types

def get_issue_type_picklist():
    issue_types = Picklist.objects.filter(key__icontains="Ticket_IssueType")
    return issue_types

def get_sub_issue_type_picklist():
    sub_issue_types = Picklist.objects.filter(key__icontains="Ticket_SubIssueType")
    return sub_issue_types

def get_sla_picklist():
    slas = Picklist.objects.filter(key__icontains="Ticket_ServiceLevelAgreementID")
    return slas

def get_ticket_source_picklist():
    ticket_sources = Picklist.objects.filter(key__icontains="Ticket_Source")
    return ticket_sources

def get_queueid_picklist():
    queue_ids = Picklist.objects.filter(key__icontains="Ticket_QueueID")
    return queue_ids

def get_priority_picklist():
    priorities = Picklist.objects.filter(key__icontains="Ticket_Priority")
    return priorities

def get_status_picklist():
    statuses = Picklist.objects.filter(key__icontains="Ticket_Status")
    return statuses

def get_account_types_picklist():
    account_types = Picklist.objects.filter(key__icontains="Account_AccountType")
    return account_types


OPERATORS = {
    "+": operator.add,
    "-": operator.sub,
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
}



RESOURCE_ROLES = {
    "Engineer": 29682834,
    "Admin": 29683587,
    "Home User Engineer": 29683586,
    "Sales": 29683582,
}


STARTER_ENTITIES = {
    "Ticket": "Ticket",
}

STANDARD_ENTITIES = {
    "Ticket": "Ticket",
    "Contact": "Contact",
    "Contract": "Contract",
    "Invoice": "Invoice",
}

PROFESSIONAL_ENTITIES = {
    "Ticket": "Ticket",
    "Contact": "Contact",
    "Contract": "Contract",
    "Invoice": "Invoice",
    "Product": "Product",
    "Quote": "Quote",
    "Opportunity": "Opportunity",
    "Appointment": "Appointment",
    "Task": "Task",
}
