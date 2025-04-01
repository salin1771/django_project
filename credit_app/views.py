from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db import transaction
from decimal import Decimal
from datetime import datetime, timedelta
from .models import User, Loan, BillingCycle, Payment, Transaction
from .serializers import (
    UserRegistrationSerializer,
    LoanApplicationSerializer,
    PaymentSerializer,
    StatementSerializer
)
from .tasks import calculate_credit_score
import uuid
import csv
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import JsonResponse

def home(request):
    return JsonResponse({
        "message": "Credit Service API",
        "endpoints": {
            "register": "/api/register-user/",
            "apply_loan": "/api/apply-loan/",
            "make_payment": "/api/make-payment/",
            "get_statement": "/api/get-statement/"
        }
    })
class RegisterUserView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()
                    
                    # Start async task to calculate credit score
                    calculate_credit_score.delay(user.aadhar_id)
                    
                    return Response({
                        'error': None,
                        'unique_user_id': user.id
                    }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class ApplyLoanView(APIView):
    def post(self, request):
        serializer = LoanApplicationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    data = serializer.validated_data
                    user = User.objects.get(id=data['unique_user_id'])
                    
                    # Check eligibility
                    if user.credit_score is None:
                        return Response({
                            'error': 'Credit score not calculated yet'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    if user.credit_score < 450:
                        return Response({
                            'error': 'Credit score too low'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    if user.annual_income < Decimal('150000'):
                        return Response({
                            'error': 'Annual income too low'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    if data['loan_amount'] > Decimal('5000'):
                        return Response({
                            'error': 'Loan amount exceeds maximum limit'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    if data['interest_rate'] < Decimal('12'):
                        return Response({
                            'error': 'Interest rate too low'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Create loan
                    loan = Loan.objects.create(
                        user=user,
                        loan_type=data['loan_type'],
                        loan_amount=data['loan_amount'],
                        principal_balance=data['loan_amount'],
                        interest_rate=data['interest_rate'],
                        term_period=data['term_period'],
                        disbursement_date=data['disbursement_date']
                    )
                    
                    # Calculate EMI schedule
                    due_dates = self.calculate_emi_schedule(loan)
                    
                    return Response({
                        'error': None,
                        'loan_id': loan.id,
                        'due_dates': due_dates
                    }, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({
                    'error': 'User not found'
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def calculate_emi_schedule(self, loan):
        # Implement EMI calculation logic here
        # This is a simplified version - you'll need to implement the actual formula
        due_dates = []
        monthly_interest_rate = loan.interest_rate / Decimal('1200')
        term = loan.term_period
        
        # EMI formula: P * r * (1+r)^n / ((1+r)^n - 1)
        emi = (loan.loan_amount * monthly_interest_rate * 
              (1 + monthly_interest_rate)**term) / ((1 + monthly_interest_rate)**term - 1)
        
        current_date = loan.disbursement_date
        for i in range(1, term + 1):
            # Add 30 days for each billing cycle
            current_date += timedelta(days=30)
            due_dates.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'amount_due': round(emi, 2)
            })
        
        return due_dates

class MakePaymentView(APIView):
    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    data = serializer.validated_data
                    loan = Loan.objects.get(id=data['loan_id'], is_active=True)
                    
                    # Get the earliest unpaid billing cycle
                    billing_cycle = BillingCycle.objects.filter(
                        loan=loan,
                        is_paid=False
                    ).order_by('billing_date').first()
                    
                    if not billing_cycle:
                        return Response({
                            'error': 'No pending payments for this loan'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    amount_paid = data['amount']
                    
                    # Check if payment covers past due first
                    if billing_cycle.past_due > 0:
                        if amount_paid < billing_cycle.past_due:
                            return Response({
                                'error': 'Payment must cover past due amount first'
                            }, status=status.HTTP_400_BAD_REQUEST)
                        
                        amount_paid -= billing_cycle.past_due
                        billing_cycle.past_due = Decimal('0')
                    
                    # Check if payment covers current min due
                    if amount_paid < billing_cycle.min_due:
                        # Partial payment - update past due
                        billing_cycle.past_due = billing_cycle.min_due - amount_paid
                        amount_paid = Decimal('0')
                    else:
                        amount_paid -= billing_cycle.min_due
                    
                    # Update billing cycle
                    billing_cycle.is_paid = True
                    billing_cycle.save()
                    
                    # Create payment record
                    Payment.objects.create(
                        billing_cycle=billing_cycle,
                        amount=data['amount'],
                        is_principal_payment=(amount_paid > 0)
                    )
                    
                    # If there's extra payment, reduce principal
                    if amount_paid > 0:
                        loan.principal_balance -= amount_paid
                        loan.save()
                    
                    # Check if loan is fully paid
                    if loan.principal_balance <= Decimal('0'):
                        loan.is_active = False
                        loan.save()
                    
                    return Response({
                        'error': None
                    }, status=status.HTTP_200_OK)
            except Loan.DoesNotExist:
                return Response({
                    'error': 'Loan not found or already closed'
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class GetStatementView(APIView):
    def get(self, request):
        serializer = StatementSerializer(data=request.GET)
        if serializer.is_valid():
            try:
                data = serializer.validated_data
                loan = Loan.objects.get(id=data['loan_id'])
                
                past_transactions = []
                payments = Payment.objects.filter(billing_cycle__loan=loan).select_related('billing_cycle')
                
                for payment in payments:
                    past_transactions.append({
                        'date': payment.payment_date.strftime('%Y-%m-%d'),
                        'principal': payment.billing_cycle.principal_portion,
                        'interest': payment.billing_cycle.interest_portion,
                        'amount_paid': payment.amount
                    })
                
                upcoming_transactions = []
                unpaid_billing = BillingCycle.objects.filter(
                    loan=loan,
                    is_paid=False
                ).order_by('billing_date')
                
                for billing in unpaid_billing:
                    upcoming_transactions.append({
                        'date': billing.due_date.strftime('%Y-%m-%d'),
                        'amount_due': billing.min_due + billing.past_due
                    })
                
                return Response({
                    'error': None,
                    'past_transactions': past_transactions,
                    'upcoming_transactions': upcoming_transactions
                }, status=status.HTTP_200_OK)
            except Loan.DoesNotExist:
                return Response({
                    'error': 'Loan not found'
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)