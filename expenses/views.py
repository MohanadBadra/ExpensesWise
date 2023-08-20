from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from userpreferences.models import UserPreferences
import datetime
import json

# Create your views here.
@login_required(login_url='/auth/login')
def index(request, type=''):
    if type not in ['expense', 'income', 'Expense', '']:
        raise Http404('Types allowed: \'income\' or \'expense\'')
    
    if type == 'expense':
        type2 = 'Expense'
    elif type == 'income':
        type2 = 'Income'
    else: type2 = type

    expenses = Expense.objects.filter(transaction_type__icontains=type2, owner=request.user)
    try:
        currency = UserPreferences.objects.get(user=request.user).currency
    except:
        UserPreferences.objects.create(user=request.user, currency='USD')
        currency = UserPreferences.objects.get(user=request.user).currency

    paginator = Paginator(expenses, 4)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)

    if type == '': 
        type = 'transaction'

    context = {
        'expenses': expenses,
        'expenses': page_obj,
        'currency': currency,
        'type': type,
        'pages_range': paginator.page_range,
    }
    print('-----------', list(paginator.page_range))
    return render(request, 'expenses/index.html', context)

@login_required(login_url='/auth/login')
def add_expense(request, type):
    if type not in ['expense', 'income']:
        raise Http404('Types allowed: \'income\' or \'expense\'')

    categories = Category.objects.all()
    context = {
        'categories': categories,
        'type': type,
    }

    if request.method == 'POST':
        transaction_type = type
        amount = request.POST['amount']
        description = request.POST['description']
        category = request.POST['category']
        date = request.POST['expense-date']
        
        if transaction_type == 'expense':
            transaction_type = 'Expense'

        elif transaction_type == 'income':
            transaction_type = 'Income'

        new_expense = Expense.objects.create(owner=request.user, amount=amount, transaction_type=transaction_type, category=category)

        if date != '':
            new_expense.date = date
            new_expense.save()
        
        if description:
            new_expense.description = description
            new_expense.save()


        messages.success(request, 'Expense Saved Successfully')

        return redirect('transactions')


    return render(request, 'expenses/add_expense.html', context)


def edit_expense(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'categories': categories,
    }

    if request.method == 'GET':
        return render(request, 'expenses/edit-expense.html', context)
    
    if request.method == 'POST':
        amount = request.POST['amount']
        transaction_type = request.POST['type']
        description = request.POST['description']
        category = request.POST['category']
        date = request.POST['expense-date']

        expense.amount = amount
        expense.transaction_type = transaction_type
        expense.category = category

        if date != '':
            expense.date = date
        
        if description:
            expense.description = description
            
        expense.save()

        messages.success(request, 'Transaction Updated successfully')

        return redirect('transactions')
    

def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    if expense.owner == request.user:
        expense.delete()
        messages.success(request, 'Expense Deleted')
    return redirect('transactions')

@csrf_exempt
def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        transaction_type = json.loads(request.body).get('type')
        
        if transaction_type == 'transaction':
            transaction_type = ''

        expenses = Expense.objects.filter(transaction_type__icontains=transaction_type, owner=request.user, amount__istartswith=search_str) | Expense.objects.filter(transaction_type__icontains=transaction_type, owner=request.user, category__icontains=search_str) | Expense.objects.filter(transaction_type__icontains=transaction_type, owner=request.user, description__icontains=search_str) | Expense.objects.filter(transaction_type__icontains=transaction_type, owner=request.user, date__icontains=search_str)

        data = expenses.values()

        return JsonResponse(list(data), safe=False)
    
        
def transactions_summary(request, type):
    if type in ['expenses', 'expense']: 
        type = 'Expense'
    if type in ['income', 'incomes']: 
        type = 'Income'
    today = datetime.date.today()
    ago = today-datetime.timedelta(days=30*6)

    transactions = Expense.objects.filter(owner=request.user, transaction_type=type, date__gte=ago, date__lte=today)

    summary = {}

    def get_category(expense):
        return expense.category
    categories_list = list(set(map(get_category, transactions)))
    
    def category_amount(category):
        amount = 0

        category_trans = transactions.filter(category=category)
        for transaction in category_trans:
            amount += int(transaction.amount)

        return amount

    for expense in transactions:
        for category in categories_list:
            summary[category] = category_amount(category)
    print('sum', print(Expense.objects.filter(owner=request.user, transaction_type=type), type))
    
    if request.method == 'POST':
        print(summary)
        return JsonResponse({'categories_amount_summary': summary}, safe=False)


    return render(request, 'expenses/stats.html', {'type': type})

