from rest_framework import serializers
from .models import User, Loan, Payment
from datetime import datetime
import uuid
from decimal import Decimal
# Change any min_value=0.01 to:
min_value=Decimal('0.01')
class UserRegistrationSerializer(serializers.ModelSerializer):
    aadhar_id = serializers.CharField(max_length=12)
    email_id = serializers.EmailField(source='email')
    
    class Meta:
        model = User
        fields = ['aadhar_id', 'username', 'email_id', 'annual_income']  # Changed 'name' to 'username'
        extra_kwargs = {
            'annual_income': {'required': True},
            'username': {'required': True}  # Add this line
        }
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=str(uuid.uuid4()),  # Random password
            aadhar_id=validated_data['aadhar_id'],
            annual_income=validated_data['annual_income']
        )
        return user

class LoanApplicationSerializer(serializers.Serializer):
    unique_user_id = serializers.UUIDField()
    loan_type = serializers.CharField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    term_period = serializers.IntegerField(min_value=1)
    disbursement_date = serializers.DateField()
    
    def validate_disbursement_date(self, value):
        if value < datetime.now().date():
            raise serializers.ValidationError("Disbursement date cannot be in the past")
        return value

class PaymentSerializer(serializers.Serializer):
    loan_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)

class StatementSerializer(serializers.Serializer):
    loan_id = serializers.UUIDField()