from django.db import models

class Customer(models.Model):
    class Meta:
        db_table = 'customer'
    first_name = models.CharField(max_length = 255 , null = True)
    last_name = models.CharField(max_length = 255 , null = True)
    age = models.IntegerField(null=True)
    monthly_income = models.IntegerField(null=True)
    approved_limit = models.BigIntegerField(null=True)
    phone_number = models.BigIntegerField(unique = True, null=True)
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)
    

# {
#     "first_name":"Vikas",
#     "last_name":"shah",
#     "age":"22",
#     "monthly_income":"11236",
#     "phone_number":"9817730229"
# }
    
class Loan(models.Model):
    class Meta:
        db_table = 'loan'
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,related_name='loan_data')
    loan_id = models.IntegerField(null=True)
    loan_amount = models.BigIntegerField(null=True)
    tenure = models.IntegerField(null=True)
    interest_rate = models.IntegerField(null=True)
    monthly_payment = models.IntegerField(null=True)
    EMI_on_Time = models.IntegerField(null=True)
    approvel_date = models.DateField(max_length=255,null=True)
    end_date = models.DateField(max_length=255,null=True)
    created_on = models.DateTimeField(auto_now_add=True)
