from celery import shared_task
from django.db import transaction
from .models import User, Transaction
from decimal import Decimal

@shared_task
def calculate_credit_score(aadhar_id):
    try:
        with transaction.atomic():
            # Get all transactions for this user
            transactions = Transaction.objects.filter(aadhar_id=aadhar_id)
            
            total_balance = Decimal('0')
            
            for txn in transactions:
                if txn.transaction_type == 'CREDIT':
                    total_balance += txn.amount
                else:
                    total_balance -= txn.amount
            
            # Calculate credit score based on rules
            if total_balance >= Decimal('1000000'):
                credit_score = 900
            elif total_balance <= Decimal('10000'):
                credit_score = 300
            else:
                # Calculate based on 10 points per Rs. 15,000
                difference = total_balance - Decimal('10000')
                points = (difference / Decimal('15000')) * 10
                credit_score = 300 + int(points)
                credit_score = min(credit_score, 900)  # Cap at 900
            
            # Update user's credit score
            user = User.objects.get(aadhar_id=aadhar_id)
            user.credit_score = credit_score
            user.save()
            
            return True
    except Exception as e:
        # Log error
        return False