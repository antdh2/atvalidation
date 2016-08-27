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
from django.contrib.auth.hashers  import make_password

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
# import the wonderful decorator for stripe
from djstripe.decorators import subscription_payment_required
from .helpers import *
from .picklist import *
from .models import Profile, Picklist, Validation, ValidationGroup, ValidationGroupRule, Entity, Company
from account.signals import user_logged_in


# Constants
at = None
accounts = None
step = 1


@receiver(post_save, sender=User)
def handle_user_save(sender, instance, created, **kwargs):
    if created:
        try:
            company = Company.objects.get(name="No Company")
        except:
            company = None
        if company:
            profile = Profile.objects.create(user=instance, company=company)
        else:
            company = Company.objects.create(name="No Company", password='')

############################################################
#
# All views must go inside of here
#
############################################################

def generate_entities(request, id):
    # entities_in_db = Entity.objects.filter(profile=request.user.profile)
    # for e in entities_in_db:
    #     e.delete()
    # First we must know if this user has a subscription equal to starter package
    if request.user.customer.current_subscription.plan == 'starter':
        # First we must delete all entites to avoid giving them option to use them if downgraded plan
        entities_in_db = Entity.objects.filter(profile=request.user.profile)
        for e in entities_in_db:
            e.delete()
        if not entities_in_db:
            for key, value in STARTER_ENTITIES.items():
                print(key + ": " + value)
                Entity.objects.create(name=key, profile=request.user.profile)
        if entities_in_db:
            for key, value in STARTER_ENTITIES.items():
                for entity in entities_in_db:
                    try:
                        t = Entity.objects.get(name=key, profile=request.user.profile)
                    except:
                        t = None
                    if t:
                        continue
                    else:
                        Entity.objects.create(name=key, profile=request.user.profile)
    if request.user.customer.current_subscription.plan == 'standard':
        # First we must delete all entites to avoid giving them option to use them if downgraded plan
        entities_in_db = Entity.objects.filter(profile=request.user.profile)
        for e in entities_in_db:
            e.delete()
        if not entities_in_db:
            for key, value in STANDARD_ENTITIES.items():
                print(key + ": " + value)
                Entity.objects.create(name=key, profile=request.user.profile)
        if entities_in_db:
            for key, value in STANDARD_ENTITIES.items():
                for entity in entities_in_db:
                    try:
                        t = Entity.objects.get(name=key, profile=request.user.profile)
                    except:
                        t = None
                    if t:
                        print(t.name)
                        continue
                    else:
                        Entity.objects.create(name=key, profile=request.user.profile)
    if request.user.customer.current_subscription.plan == 'professional':
        # First we must delete all entites to avoid giving them option to use them if downgraded plan
        entities_in_db = Entity.objects.filter(profile=request.user.profile)
        for e in entities_in_db:
            e.delete()
        if not entities_in_db:
            for key, value in PROFESSIONAL_ENTITIES.items():
                print(key + ": " + value)
                Entity.objects.create(name=key, profile=request.user.profile)
        if entities_in_db:
            for key, value in PROFESSIONAL_ENTITIES.items():
                for entity in entities_in_db:
                    try:
                        t = Entity.objects.get(name=key, profile=request.user.profile)
                    except:
                        t = None
                    if t:
                        continue
                    else:
                        Entity.objects.create(name=key, profile=request.user.profile)
    return redirect('input_validation', id)

def home(request):
    return render(request, 'home.html', {})

input_validation_dict = {}
@subscription_payment_required
def input_validation(request, id):
    generate_entities(request, id)
    page = 'validation'
    step = 1
    if request.user:
        at = autotask_login_function(request, request.user.profile.autotask_username, request.user.profile.autotask_password)
    try:
        existing_validation_groups = ValidationGroup.objects.filter(company=request.user.profile.company)
        existing_validation_group_rules = ValidationGroupRule.objects.filter(company=request.user.profile.company)
        existing_validations = []
        validations = Validation.objects.all()
        for v in validations:
            existing_validations.append(v)
    except:
        existing_validations = None
        existing_validation_groups = None
    entitytypes = Entity.objects.all
    try:
        entity_attributes = at.new(input_validation_dict['EntityName'])
    except:
        entity_attributes = None
    entity = None
    values = None
    selected_key = None
    if request.method == "POST":
        if request.POST.get('step1', False):
            step = 2
            entity = Entity.objects.get(name=request.POST['entitytype'])
            input_validation_dict['Entity'] = entity
            input_validation_dict['EntityName'] = request.POST['entitytype']
            validation_group = ValidationGroup.objects.create(company=request.user.profile.company, name=request.POST['validation-group-name'], entity=entity)
            input_validation_dict['ValidationGroupId'] = validation_group.id
            input_validation_dict['ValidationGroup'] = validation_group
            entity_attributes = at.new(input_validation_dict['EntityName'])
            return redirect('edit_validation_group', id, input_validation_dict['ValidationGroupId'])
            # return render(request, 'input_validation.html', {"page": page, "entitytypes": entitytypes, "OPERATORS": OPERATORS, "step": step, "entity_attributes": entity_attributes, "values": values, "selected_key": selected_key, "existing_validations": existing_validations, "input_validation_dict": input_validation_dict, "existing_validation_groups": existing_validation_groups})
    return render(request, 'input_validation.html', {"existing_validation_group_rules": existing_validation_group_rules, "page": page, "entitytypes": entitytypes, "OPERATORS": OPERATORS, "step": step, "entity_attributes": entity_attributes, "existing_validations": existing_validations, "input_validation_dict": input_validation_dict, "existing_validation_groups": existing_validation_groups})

def edit_validation_group(request, id, validation_group_id):
    if request.user:
        at = autotask_login_function(request, request.user.profile.autotask_username, request.user.profile.autotask_password)
    validation_group = ValidationGroup.objects.get(id=validation_group_id)
    existing_validations = Validation.objects.filter(validation_group=validation_group_id)
    entity_attributes = at.new(validation_group.entity.name)
    try:
        validation_group_rule = ValidationGroupRule.objects.get(validation_group=validation_group)
    except:
        validation_group_rule = None
    values = None
    selected_key = None
    key = None
    if request.method == "POST":
        if request.POST.get('validation-group-rule-select', False):
            key = request.POST['key']
            selected_key = key
            values = Picklist.objects.filter(company=request.user.profile.company, key__icontains=validation_group.entity.name + "_" + key)
            return render(request, 'edit_validation_group.html', {"validation_group_rule": validation_group_rule, "OPERATORS": OPERATORS, "step": step, "entity_attributes": entity_attributes, "values": values, "selected_key": selected_key, "existing_validations": existing_validations, "validation_group": validation_group})
        if request.POST.get('step1-keyselect', False):
            key = request.POST['key']
            selected_key = key
            values = Picklist.objects.filter(company=request.user.profile.company, key__icontains=validation_group.entity.name + "_" + key)
            return render(request, 'edit_validation_group.html', {"validation_group_rule": validation_group_rule, "OPERATORS": OPERATORS, "step": step, "entity_attributes": entity_attributes, "values": values, "selected_key": selected_key, "existing_validations": existing_validations, "validation_group": validation_group})
        if request.POST.get('step2', False):
            key = request.POST['selected_key']
            value = request.POST['value']
            operator = request.POST['operator']
            mandatory = request.POST.get('mandatory', False)
            # We have to find the picklist from atvar to associate the right number to the validation
            # Validation object "value" should match the result of Picklist "key". ie. (atvar.)Ticket_Status_New on Validation should equal 1 on Picklist
            try:
                picklist_object = Picklist.objects.get(key=value)
                picklist = picklist_object.value
            except:
                picklist = -100
            validation = Validation.objects.create(key=key, value=value, operator=operator, entity=validation_group.entity, picklist_number=picklist, validation_group=validation_group, mandatory=mandatory)
            return render(request, 'edit_validation_group.html', {"validation_group_rule": validation_group_rule, "OPERATORS": OPERATORS, "step": step, "entity_attributes": entity_attributes, "values": values, "selected_key": selected_key, "existing_validations": existing_validations, "validation_group": validation_group})
        if request.POST.get('validationgrouprulesubmit', False):
            key = request.POST['selected_key']
            value = request.POST['value']
            operator = request.POST['operator']
            # We have to find the picklist from atvar to associate the right number to the validation
            # Validation object "value" should match the result of Picklist "key". ie. (atvar.)Ticket_Status_New on Validation should equal 1 on Picklist
            try:
                picklist_object = Picklist.objects.get(key=value)
                picklist = picklist_object.value
            except:
                picklist = -100
            validation_group_rule = ValidationGroupRule.objects.create(key=key, value=value, operator=operator, entity=validation_group.entity, picklist_number=picklist, validation_group=validation_group, company=request.user.profile.company)
            return render(request, 'edit_validation_group.html', {"validation_group_rule": validation_group_rule, "OPERATORS": OPERATORS, "step": step, "entity_attributes": entity_attributes, "values": values, "selected_key": selected_key, "existing_validations": existing_validations, "validation_group": validation_group})

    return render(request, 'edit_validation_group.html', {"validation_group_rule": validation_group_rule, "OPERATORS": OPERATORS, "step": step, "entity_attributes": entity_attributes, "values": values, "selected_key": selected_key, "existing_validations": existing_validations, "validation_group": validation_group})

def delete_validation_group(request, id):
    userid = request.user.id
    validation_group = ValidationGroup.objects.get(id=id)
    # We must validate that the validation group belongs to this user
    if validation_group.company == request.user.profile.company:
        validation_group.delete()
        messages.add_message(request, messages.SUCCESS, '{} validation group deleted.'.format(validation_group.name))
    else:
        messages.add_message(request, messages.ERROR, '{} is not your validation group.'.format(validation_group.name))
    return redirect('input_validation', userid)

def delete_validation(request, id):
    userid = request.user.id
    validation = Validation.objects.get(id=id)
    validation_group = ValidationGroup.objects.get(id=validation.validation_group.id)
    # We must validate that the validation belongs to this user
    if validation.validation_group == validation_group:
        validation.delete()
        messages.add_message(request, messages.SUCCESS, '{} validation deleted.'.format(validation.key + " " + validation.operator + " " + validation.value))
    else:
        messages.add_message(request, messages.ERROR, '{} is not your validation.'.format(validation.key + " " + validation.operator + " " + validation.value))
    return redirect('edit_validation_group', userid, validation_group.id)

@login_required(login_url='/account/login/')
def profile(request, id):
    page = 'profile'
    if int(request.user.id) != int(id):
        messages.add_message(request, messages.ERROR, "That's not your profile!.")
        return redirect('index')
    # First we must connect to autotask using valid credentials
    if request.method == "POST":
        if request.POST.get('joincompany', False):
            profile = Profile.objects.get(user_id=id)
            company = Company.objects.get(id=request.POST['join-company-id'], name=request.POST['join-company-name'], password=request.POST['join-company-password'])
            profile.company = company
            profile.save()
        if request.POST.get('leavecompany', False):
            profile = Profile.objects.get(user_id=id)
            # Set company to default "No Company"
            company = Company.objects.get(name="No Company")
            profile.company = company
            profile.save()
        if request.POST.get('createcompany', False):
            company = Company.objects.create(name=request.POST['create-company-name'], password=request.POST['create-company-password'])
            company.save()
            profile = Profile.objects.get(user_id=id)
            profile.company = company
            profile.save()
        if request.POST.get('editprofile', False):
            profile = Profile.objects.get(user_id=id)
            profile.first_name = request.POST['profile-firstname']
            profile.last_name = request.POST['profile-lastname']
            profile.about = request.POST['profile-about']
            profile.save()
            return render(request, 'account/profile.html', {"page": page, "profile": profile})
        if request.POST.get('autotasklogin', False):
            at = None
            username = request.POST['username']
            password = request.POST['password']
            at = autotask_login_function(request, username, password)
            user = request.POST['username'].split('@')
            resource = get_resource_from_username(user[0])
            profile = Profile.objects.get(user=request.user)
            profile.atresource_id = resource.id
            profile.save()
            if at:
                messages.add_message(request, messages.SUCCESS, 'Successfully logged in. You may now proceed to create a picklist module.')
                return render(request, 'index.html', {"profile": profile, "page": page, "at": at})
            else:
                return render(request, 'account/profile.html', {"page": page, "at": at, "profile": profile})
    return render(request, 'account/profile.html', {"page": page})

@login_required(login_url='/account/login/')
def index(request):
    try:
        page = 'index'
        accounts = None
        at = None
        if request.user:
            at = autotask_login_function(request, request.user.profile.autotask_username, request.user.profile.autotask_password)

        return render(request, 'index.html', {"accounts": accounts, "page": page, "at": at})
    except AttributeError:
        messages.add_message(request, messages.ERROR, 'No connection with Autotask. Please ensure your Autotask credentials are entered in your profile page.')
        return render(request, 'index.html', {"at": at, })


def ajax_create_ticket(request):
    if request.method == "POST":
        validation_group_rules = ValidationGroupRule.objects.filter(company=request.user.profile.company)
        response_data = {}

        response_data['AllocationCodeID'] = request.POST.get('AllocationCodeID')
        response_data['AssignedResourceID'] = request.POST.get('AssignedResourceID')
        response_data['AssignedResourceRoleID'] = request.POST.get('AssignedResourceRoleID')
        response_data['ContactID'] = request.POST.get('ContactID')
        response_data['Description'] = request.POST.get('Description')
        response_data['DueDateTime'] = request.POST.get('DueDateTime')
        response_data['EstimatedHours'] = request.POST.get('EstimatedHours')
        response_data['IssueType'] = request.POST.get('IssueType')
        response_data['Priority'] = request.POST.get('Priority')
        response_data['QueueID'] = request.POST.get('QueueID')
        response_data['ServiceLevelAgreementID'] = request.POST.get('ServiceLevelAgreementID')
        response_data['Status'] = request.POST.get('Status')
        response_data['SubIssueType'] = request.POST.get('SubIssueType')
        response_data['TicketType'] = request.POST.get('TicketType')
        response_data['Title'] = request.POST.get('Title')
        validated = validate_input(request, validation_group_rules)
        print(validated)
        # if validation fails then return to webpage with an error message (this is handled by function call)
        if not validated:
            django_messages = []

            for message in messages.get_messages(request):
                django_messages.append({
                    "level": message.level_tag,
                    "message": message.message,
                    "extra_tags": message.tags,
            })
            return HttpResponse(json.dumps(django_messages), content_type="application/json")
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        return HttpResponse(json.dumps({"nothing to see": "this isn't happening"}), content_type="application/json")

create_ticket_dict = {}
@login_required(login_url='/account/login/')
def create_ticket(request, id):
    # First we must check we have a logged in user then ensure we're connected to AT
    if request.user:
        at = autotask_login_function(request, request.user.profile.autotask_username, request.user.profile.autotask_password)
    profile = Profile.objects.get(user=request.user)
    account_id = id
    ataccount = get_account(account_id)
    # Get all picklist objects
    contacts = get_contacts_for_account(account_id)
    ticket_types = get_ticket_type_picklist()
    issue_types = get_issue_type_picklist()
    sub_issue_types = get_sub_issue_type_picklist()
    slas = get_sla_picklist()
    account_types = get_account_types_picklist()
    statuses = get_status_picklist()
    priorities = get_priority_picklist()
    queue_ids = get_queueid_picklist()
    ticket_sources = get_ticket_source_picklist()
    resources = get_resources()
    roles = get_roles()
    services = get_contract_services(account_id)
    allocation_codes = get_allocation_codes()
    contracts = get_contracts(account_id)
    # Grab all validation group rules for this users company
    validation_group_rules = ValidationGroupRule.objects.filter(company=request.user.profile.company)
    validated = True
    if request.method == "POST":
        # Lets check if any of our validation groups are triggered
        validated = validate_input(request, validation_group_rules)
        # if validation fails then return to webpage with an error message (this is handled by function call)
        if not validated:
            return render(request, 'create_ticket.html', {"create_ticket_dict": create_ticket_dict, "contacts": contacts, "services": services, "allocation_codes": allocation_codes, "contracts": contracts, "roles": roles, "resources": resources, "account_types": account_types, "statuses": statuses, "priorities": priorities, "queue_ids": queue_ids, "ticket_sources": ticket_sources, "issue_types": issue_types, "sub_issue_types": sub_issue_types, "slas": slas, "ticket_types": ticket_types, "ataccount": ataccount})
        # if we pass validation, previous line of code is not run and a ticket is created
        # but first lets do some custom work
        # 1) logic for determining which contract to validate
        contract_name = request.POST['ContractID'].lower()
        print(contract_name)
        contract = get_contract_for_ticket(account_id, contract_name)
        print(contract)
        if contract:
            contract = contract
        else:
            contract = None
        new_ticket = ticket_create_new(True,
            AccountID = account_id,
            # AEMAlertID = request.POST['AEMAlertID'],
            AllocationCodeID = request.POST['AllocationCodeID'],
            AssignedResourceID = request.POST['AssignedResourceID'],
            AssignedResourceRoleID = request.POST['AssignedResourceRoleID'],
            # ChangeApprovalBoard = request.POST['ChangeApprovalBoard'],
            # ChangeApprovalStatus = request.POST['ChangeApprovalStatus'],
            # ChangeApprovalType = request.POST['ChangeApprovalType'],
            # ChangeInfoField1 = request.POST['ChangeInfoField1'],
            # ChangeInfoField2 = request.POST['ChangeInfoField2'],
            # ChangeInfoField3 = request.POST['ChangeInfoField3'],
            # ChangeInfoField4 = request.POST['ChangeInfoField4'],
            # ChangeInfoField5 = request.POST['ChangeInfoField5'],
            # CompletedDate = request.POST['CompletedDate'],
            ContactID = request.POST['ContactID'],
            # ContractID = contract.id,
            CreatorResourceID = profile.atresource_id,
            Description = request.POST['Description'],
            DueDateTime = request.POST['DueDateTime'],
            EstimatedHours = request.POST['EstimatedHours'],
            # FirstResponseDateTime = request.POST['FirstResponseDateTime'],
            # FirstResponseDueDateTime = request.POST['FirstResponseDueDateTime'],
            # HoursToBeScheduled = request.POST['HoursToBeScheduled'],
            # InstalledProductID = request.POST['InstalledProductID'],
            IssueType = request.POST['IssueType'],
            # LastActivityDate = request.POST['LastActivityDate'],
            # LastCustomerNotificationDateTime = request.POST['LastCustomerNotificationDateTime'],
            # LastCustomerVisibleActivityDateTime = request.POST['LastCustomerVisibleActivityDateTime'],
            # MonitorID = request.POST['MonitorID'],
            # MonitorTypeID = request.POST['MonitorTypeID'],
            # OpportunityId = request.POST['OpportunityId'],
            Priority = request.POST['Priority'],
            # ProblemTicketId = request.POST['ProblemTicketId'],
            # PurchaseOrderNumber = request.POST['PurchaseOrderNumber'],
            QueueID = request.POST['QueueID'],
            # Resolution = request.POST['Resolution'],
            # ResolutionPlanDateTime = request.POST['ResolutionPlanDateTime'],
            # ResolutionPlanDueDateTime = request.POST['ResolutionPlanDueDateTime'],
            # ResolvedDateTime = request.POST['ResolvedDateTime'],
            # ResolvedDueDateTime = request.POST['ResolvedDueDateTime'],
            # ServiceLevelAgreementHasBeenMet = request.POST['ServiceLevelAgreementHasBeenMet'],
            ServiceLevelAgreementID = request.POST['ServiceLevelAgreementID'],
            # Source = request.POST['Source'],
            Status = request.POST['Status'],
            SubIssueType = request.POST['SubIssueType'],
            # TicketNumber = request.POST['TicketNumber'],
            TicketType = request.POST['TicketType'],
            Title = request.POST['Title'],
            )
        messages.add_message(request, messages.SUCCESS, ('Ticket - ' + new_ticket.TicketNumber + ' - ' + new_ticket.Title + ' created.'))
    return render(request, 'create_ticket.html', {"create_ticket_dict": create_ticket_dict, "contacts": contacts, "services": services, "allocation_codes": allocation_codes, "contracts": contracts, "roles": roles, "resources": resources, "account_types": account_types, "statuses": statuses, "priorities": priorities, "queue_ids": queue_ids, "ticket_sources": ticket_sources, "issue_types": issue_types, "sub_issue_types": sub_issue_types, "slas": slas, "ticket_types": ticket_types, "ataccount": ataccount})



############################################################
#
# This is for overriding default user signup behaviour
#
############################################################

class LoginView(account.views.LoginView):

    form_class = account.forms.LoginEmailForm


class SignupView(account.views.SignupView):

   form_class = autotask_web_app.forms.SignupForm
   #
   def after_signup(self, form):
       self.create_profile(form)
       super(SignupView, self).after_signup(form)

   def create_profile(self, form):
       profile = self.created_user.profile  # replace with your reverse one-to-one profile attribute
       profile.first_name = form.cleaned_data["first_name"]
       profile.last_name = form.cleaned_data["last_name"]
       profile.email = form.cleaned_data["email"]
       profile.save()

   def generate_username(self, form):
        # do something to generate a unique username (required by the
        # Django User model, unfortunately)
        username = form.cleaned_data['email']
        return username
