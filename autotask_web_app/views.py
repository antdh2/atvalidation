from django.shortcuts import render
from django.shortcuts import render_to_response

import atws



# First we must connect to autotask using valid credentials
at = atws.connect(username='ant.horner@eye-techit.com',password='Mnschnaap1!')

# Create your views here.
def index(request):
    # Once an account name/id is entered
    if request.method == "POST":
        # map account_id to the inputted value
        account_name = request.POST['account-name']
        accounts = resolve_account_name(account_name)
        account_id = resolve_account_id(account_name)
        # then get autotask account using that ID
        # accounts = get_account(account_id)
        tickets = get_tickets_for_account(account_id)
        ticket_account_name = resolve_account_name_from_id(account_id)
        ticket_info = get_ticket_info(tickets)

    else:
        account_id = None
        accounts = None
        tickets = None
        ticket_account_name = None
        ticket_info = None

    return render(request, 'index.html', {"account_id": account_id, "accounts": accounts, "tickets": tickets, "ticket_account_name": ticket_account_name, "ticket_info": ticket_info})


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
    aquery.WHERE('AccountName',aquery.Equals,string)
    accounts = at.query(aquery).fetch_one()
    for field, value in accounts:
        if field == "AccountName" and value == string:
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
