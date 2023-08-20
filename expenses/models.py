from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# Create your models here.
class Expense(models.Model):
    TRANSACTION_CHOICES = [
        ('Income', 'Income'),
        ('Expense', 'Expense'),
    ]


    amount = models.FloatField()
    transaction_type = models.CharField(max_length=16, choices=TRANSACTION_CHOICES, default='Expense', blank=True, null=True)
    date = models.DateField(default=now)
    description = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    category = models.CharField(max_length=256)

    def __str__(self):
        return f'{self.transaction_type}: {self.category} - {self.amount}'
    
    class Meta:
        verbose_name = 'transaction'
        ordering = ['-date']

class Category(models.Model):
    name = models.CharField(max_length=256)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name