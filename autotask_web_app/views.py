from django.shortcuts import render, redirect
from django.shortcuts import render_to_response
from django.contrib import messages
from django.http import HttpResponse

import atws
from autotask_api_app import atvar

at = None
accounts = None

def autotask_login(username, password):
    return login

def login(request):
    # First we must connect to autotask using valid credentials
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        global at
        at = atws.connect(username=username,password=password)
        messages.add_message(request, messages.SUCCESS, 'Successfully logged in.')
        return redirect("/", successMessage="Success!")
    else:
        messages.add_message(request, messages.ERROR, 'Something went wrong.')
        return render(request, 'login.html', {})



# Create your views here.
def index(request):
    accounts = None
    # Once an account name/id is entered
    if request.method == "POST":
        # map account_id to the inputted value
        account_name = request.POST['account-name']
        accounts = resolve_account_name(account_name)
        #account_id = resolve_account_id(account_name)
        # then get autotask account using that ID
    else:
        accounts = None

    return render(request, 'index.html', {"accounts": accounts})


def account(request, id):
    account_id = id
    account = get_account(account_id)
    tickets = get_tickets_for_account(account_id)
    ticket_account_name = resolve_account_name_from_id(account_id)
    ticket_info = get_ticket_info(tickets)

    account_types = {
        "Lead": atvar.Account_AccountType_Lead,
        "Dead": atvar.Account_AccountType_Dead,
        "Vendor": atvar.Account_AccountType_Vendor,
        "Partner": atvar.Account_AccountType_Partner,
        "Prospect": atvar.Account_AccountType_Prospect,
        "Customer": atvar.Account_AccountType_Customer,
        "Cancellation": atvar.Account_AccountType_Cancellation,
    }
    return render(request, 'account.html', {"account": account, "tickets": tickets, "ticket_account_name": ticket_account_name, "account_types": account_types})


def edit_account(request, id):
    account_id = id
    account = get_account(account_id)
    if request.method == "POST":
        new_account_name = request.POST['account-name']
        new_address_1 = request.POST['address1']
        new_address_2 = request.POST['address2']
        new_state = request.POST['state']
        new_city = request.POST['city']
        new_postalcode = request.POST['postcode']
        new_phone = request.POST['phone']
        account.AccountName = new_account_name
        account.Address1 = new_address_1
        account.Address2 = new_address_2
        account.State = new_state
        account.City = new_city
        account.PostalCode = new_postalcode
        account.Phone = new_phone
        account.update()
        messages.add_message(request, messages.SUCCESS, 'Successfully edited.')

    return redirect("/account/" + account_id, successMessage="Success!")



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
