from rest_framework import serializers
from . models import Customer, Loan

class CustomerSerializers(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class LoanSerializers(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'