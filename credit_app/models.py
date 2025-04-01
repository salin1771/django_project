from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid

class User(AbstractUser):
    aadhar_id = models.CharField(max_length=12, unique=True)
    annual_income = models.DecimalField(max_digits=12, decimal_places=2)
    credit_score = models.IntegerField(null=True, blank=True)
    
    # Add these to resolve the conflicts
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='credit_app_user_groups',  # Unique related_name
        related_query_name='credit_app_user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='credit_app_user_permissions',  # Unique related_name
        related_query_name='credit_app_user',
    )
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class Loan(models.Model):
    LOAN_TYPES = (
        ('CREDIT_CARD', 'Credit Card'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    loan_type = models.CharField(max_length=20, choices=LOAN_TYPES)
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    principal_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # APR
    term_period = models.PositiveIntegerField()  # in months
    disbursement_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s {self.loan_type} Loan"

class BillingCycle(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    billing_date = models.DateField()
    due_date = models.DateField()
    min_due = models.DecimalField(max_digits=12, decimal_places=2)
    principal_portion = models.DecimalField(max_digits=12, decimal_places=2)
    interest_portion = models.DecimalField(max_digits=12, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    past_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['billing_date']

class Payment(models.Model):
    billing_cycle = models.ForeignKey(BillingCycle, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    is_principal_payment = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Payment of {self.amount} for {self.billing_cycle}"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('DEBIT', 'Debit'),
        ('CREDIT', 'Credit'),
    )
    
    aadhar_id = models.CharField(max_length=12)
    date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPES)
    
    class Meta:
        ordering = ['date']