from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views

urlpatterns = [
    path('', views.index, name='transactions'),
    path('add-<str:type>', views.add_expense, name='add-expense'),
    path('edit-expense/<int:id>', views.edit_expense, name='edit-expense'),
    path('delete-expense/<int:id>', views.delete_expense, name='delete-expense'),
    path('search-expenses', csrf_exempt(views.search_expenses), name='search-expenses'),
    
    path('summary/<str:type>', csrf_exempt(views.transactions_summary), name='transactions-summary'),
    
    path('<str:type>', views.index, name='expenses'),
    path('<str:type>', views.index, name='incomes'),
]