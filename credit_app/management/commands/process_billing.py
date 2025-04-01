from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import date, timedelta
from decimal import Decimal
from ...models import Loan, BillingCycle

class Command(BaseCommand):
    help = 'Process billing for loans'
    
    def handle(self, *args, **options):
        today = date.today()
        
        # Get loans that need billing today
        loans_to_bill = Loan.objects.filter(
            is_active=True,
            disbursement_date__lte=today - timedelta(days=30)
        ).select_related('user')
        
        for loan in loans_to_bill:
            try:
                with transaction.atomic():
                    # Calculate days since last billing or disbursement
                    last_billing = BillingCycle.objects.filter(
                        loan=loan
                    ).order_by('-billing_date').first()
                    
                    if last_billing:
                        days_since_last_billing = (today - last_billing.billing_date).days
                        billing_date = last_billing.billing_date + timedelta(days=30)
                    else:
                        days_since_last_billing = (today - loan.disbursement_date).days
                        billing_date = loan.disbursement_date + timedelta(days=30)
                    
                    # Calculate daily interest
                    daily_interest_rate = round(loan.interest_rate / Decimal('365'), 3)
                    daily_interest_accrued = (loan.principal_balance * daily_interest_rate) / Decimal('100')
                    
                    # Calculate interest for the billing cycle
                    interest_accrued = daily_interest_accrued * days_since_last_billing
                    
                    # Calculate min due (3% of principal + interest)
                    min_due = (loan.principal_balance * Decimal('0.03')) + interest_accrued
                    
                    # Create new billing cycle
                    due_date = billing_date + timedelta(days=15)
                    
                    billing_cycle = BillingCycle.objects.create(
                        loan=loan,
                        billing_date=billing_date,
                        due_date=due_date,
                        min_due=min_due,
                        principal_portion=loan.principal_balance * Decimal('0.03'),
                        interest_portion=interest_accrued
                    )
                    
                    self.stdout.write(self.style.SUCCESS(
                        f'Created billing cycle for loan {loan.id}: '
                        f'Min Due: {min_due}, Due Date: {due_date}'
                    ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'Error processing billing for loan {loan.id}: {str(e)}'
                ))