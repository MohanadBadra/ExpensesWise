from django.contrib import admin
from .models import Expense, Category
# Register your models here.


class TransactionAdmin(admin.ModelAdmin):
    list_display = ['amount', 'transaction_type', 'owner', 'category', 'description', 'date']
    search_fields = ['amount', 'transaction_type', 'category', 'description', 'date']
    
    list_per_page = 8


admin.site.register(Expense, TransactionAdmin)
admin.site.register(Category)