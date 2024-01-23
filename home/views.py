from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from . models import Customer,Loan
from django.views.decorators.csrf import csrf_exempt  #This is only for Development , not for Deployment { Security Issues may Come }
import json
from . serializers import CustomerSerializers ,LoanSerializers
from rest_framework.response import Response
from rest_framework.decorators import api_view
import pandas as pd 
from datetime import datetime
# Create your views here.
def test(request):
    if request.method == "GET":
        return HttpResponse("Test OK")
    else:
        return HttpResponse("WRONG METHOD")

@api_view(["POST"])
@csrf_exempt
def register(request):
    try:
        data = json.loads(request.body)
        first_name = data["first_name"]
        last_name = data["last_name"]
        age = data["age"]
        monthly_income = data["monthly_income"]
        phone_number = data["phone_number"]

        # Approved Limit of New User
        approved_limit = round((36*int(monthly_income))/1000)
        approved_limit = int(((approved_limit / 10) * 10)*1000)

        new_user  = Customer.objects.create(
            first_name = first_name,
            last_name = last_name,
            age = int(age),
            monthly_income = int(monthly_income),
            phone_number = int(phone_number),
            approved_limit = int(approved_limit)
        )          
        serial = CustomerSerializers(new_user)
        return Response(serial.data)
    except Exception as e:
        return JsonResponse({"msg":str(e)})

@csrf_exempt
def upload_customer(request):
    if request.method == "POST":
        if json.loads(request.body)["start"] == "START":
            data = pd.read_excel("customer_data.xlsx")
            try:
                for index,row in data.iterrows():
                    Customer.objects.create(
                        # id = row['Customer ID'],
                        first_name = row["First Name"],
                        last_name = row["Last Name"],
                        age = row["Age"],
                        phone_number = row["Phone Number"],
                        monthly_income = row["Monthly Salary"],
                        approved_limit = row['Approved Limit']
                    )
                return JsonResponse({"msg":"Coustomer Data Uploded"})
            except Exception as e:
                return JsonResponse({"msg":str(e)})
        else:
            return JsonResponse({"msg":"Code Error"})
    else:
        return JsonResponse({"msg":"Method Error"})


@csrf_exempt
def upload_loan(request):
    if request.method == "POST":
        if json.loads(request.body)["start"] == "START":
            data = pd.read_excel("loan_data.xlsx")
            try:
                for index,row in data.iterrows():
                    Loan.objects.create(
                        # id = row['Customer ID'],
                        customer_id = row["Customer ID"],
                        loan_id = row["Loan ID"],
                        loan_amount = row["Loan Amount"],
                        tenure = row["Tenure"],
                        interest_rate = row["Interest Rate"],
                        monthly_payment = row["Monthly payment"],
                        EMI_on_Time = row['EMIs paid on Time'],
                        approvel_date = row['Date of Approval'],
                        end_date = row['End Date']
                    )
                return JsonResponse({"msg":"Loan Data Uploded"})
            except Exception as e:
                return JsonResponse({"msg":str(e)})
        else:
            return JsonResponse({"msg":"Code Error"})
    else:
        return JsonResponse({"msg":"Method Error"})

@api_view(["POST"])  
@csrf_exempt
def check_eligibility(request):
    data  = request.data
    try:
        user = Customer.objects.get(id = data['customer_id'])
        loans = Loan.objects.filter(customer_id = data['customer_id'])
    except:
        return Response({"msg":"Data Not Found"})
    today_date = datetime.now().date()
    credit_score_by_emi = 0
    credit_score_by_loan = 0
    credit_score = 0
    total_emi = 0
    emi_onTime = 0
    total_loan = len(loans)
    total_currunt_loan_amount = 0
    ongoing_loan = 0
    loan_volume = 0
    current_emi = 0
    interest_rate = 0
    lowest_intrest = 100.0
    loan_approved = True
    for i in loans:
        total_emi += int(i.tenure)
        emi_onTime += int(i.EMI_on_Time)
        print(i.end_date)
        if today_date <= i.end_date: #means curruntly ongoing Loans
            total_currunt_loan_amount += i.loan_amount
            current_emi =+ i.monthly_payment
            ongoing_loan += 1   
        loan_volume+=i.loan_amount
        if(lowest_intrest > i.interest_rate):
            lowest_intrest = i.interest_rate
    try:
        credit_score_by_emi = int(((emi_onTime)/(total_emi))*100)   
    except:
        credit_score_by_emi = 10
    if(total_loan >=10):
        credit_score_by_loan = 100
    elif(total_loan < 10):
        credit_score_by_loan = total_loan*10

        
    credit_score = ((credit_score_by_emi + credit_score_by_loan)/2)
    if(user.approved_limit <= total_currunt_loan_amount):
        credit_score = 0

    if(current_emi > ((user.monthly_income)/2)):
        loan_approved = False
    if(credit_score >= 50):
        interest_rate = float(data['interest_rate'])
        if( interest_rate < lowest_intrest ):
            interest_rate = lowest_intrest
                
        total_intrest = ((float(data['tenure']))/12)*interest_rate
        total_amount = ((total_intrest/100)+1)*float(data["loan_amount"])
        monthly_emi = int((total_amount)/int(data["tenure"]))
        return Response({"customer_id":user.id,
                         "credit_score":credit_score,
                         "approval":loan_approved,
                         "interest_rate":float(data["interest_rate"]),
                         "Corrected_interest_rate":interest_rate,
                         "tenure":int(data["tenure"]),
                         "monthly_installment":monthly_emi,

                         })
    elif(credit_score < 50 and credit_score >= 30):
        if(lowest_intrest > 12):
            pass
        else:
            lowest_intrest = 12
        print(interest_rate)
        total_intrest = ((float(data['tenure']))/12)*lowest_intrest
        total_amount = ((total_intrest/100)+1)*float(data["loan_amount"])
        monthly_emi = int((total_amount)/int(data["tenure"]))
        return Response({"customer_id":user.id,
                         "approval":loan_approved,
                         "credit_score":credit_score,
                         "interest_rate":float(data["interest_rate"]),
                         "Corrected_interest_rate":lowest_intrest,
                         "tenure":int(data["tenure"]),
                         "monthly_installment":monthly_emi,

                         })
    elif(credit_score < 30 and credit_score >= 10):
        
        if(lowest_intrest > 16):
            pass
        else:
            lowest_intrest = 16

        total_intrest = ((float(data['tenure']))/12)*lowest_intrest
        total_amount = ((total_intrest/100)+1)*float(data["loan_amount"])
        monthly_emi = int((total_amount)/int(data["tenure"]))
        return Response({"customer_id":user.id,
                         "approval":loan_approved,
                         "credit_score":credit_score,
                         "interest_rate":float(data["interest_rate"]),
                         "Corrected_interest_rate":lowest_intrest,
                         "tenure":int(data["tenure"]),
                         "monthly_installment":monthly_emi,

                         })
    else:
        return Response({"msg":"ok",
                        "Percent of onTime":credit_score_by_emi,
                        "Credit Score":credit_score, 
                        "No. of lons":total_loan,
                        "Currunt amount":total_currunt_loan_amount,
                        "ongoing_loan":ongoing_loan,
                        "Volume":loan_volume,
                        'current_emi':current_emi,
                        "Loan_approved":False
                        })
            

@api_view(["POST"])
@csrf_exempt
def create_loan(request):
    data  = request.data
    try:
        user = Customer.objects.get(id = data['customer_id'])
        loans = Loan.objects.filter(customer_id = data['customer_id'])
    except:
        return Response({"msg":"Data Not Found"})
    today_date = datetime.now().date()
    credit_score_by_emi = 0
    credit_score_by_loan = 0
    credit_score = 0
    total_emi = 0
    emi_onTime = 0
    total_loan = len(loans)
    total_currunt_loan_amount = 0
    ongoing_loan = 0
    loan_volume = 0
    current_emi = 0
    interest_rate = 0
    lowest_intrest = 100.0
    loan_approved = True
    for i in loans:
        total_emi += int(i.tenure)
        try:
            emi_onTime += int(i.EMI_on_Time)
        except:
            emi_onTime = 0
        print(i.end_date)
        if today_date <= i.end_date: #means curruntly ongoing Loans
            total_currunt_loan_amount += i.loan_amount
            current_emi =+ i.monthly_payment
            ongoing_loan += 1   
        loan_volume+=i.loan_amount
        if(lowest_intrest > i.interest_rate):
            lowest_intrest = i.interest_rate
    try:
        credit_score_by_emi = int(((emi_onTime)/(total_emi))*100)   
    except:
        credit_score_by_emi = 10
    if(total_loan >=10):
        credit_score_by_loan = 100
    elif(total_loan < 10):
        credit_score_by_loan = total_loan*10

        
    credit_score = ((credit_score_by_emi + credit_score_by_loan)/2)
    if(user.approved_limit <= total_currunt_loan_amount):
        credit_score = 0

    if(current_emi > ((user.monthly_income)/2)):
        loan_approved = False
    if(credit_score >= 50):
        interest_rate = float(data['interest_rate'])
        if( interest_rate < lowest_intrest ):
            interest_rate = lowest_intrest
                
        total_intrest = ((float(data['tenure']))/12)*interest_rate
        total_amount = ((total_intrest/100)+1)*float(data["loan_amount"])
        monthly_emi = int((total_amount)/int(data["tenure"]))
        loan = Loan.objects.create(
            customer_id= user.id,
            loan_amount = data["loan_amount"],
            interest_rate = interest_rate,
            tenure =  data["tenure"],
            monthly_payment = monthly_emi,
            approvel_date = today_date,
            end_date = today_date,
            EMI_on_Time = 0
            
        )
        return Response({"customer_id":user.id,
                         "loan":loan.id,
                         "credit_score":credit_score,
                         "loan_approved":loan_approved,
                         "interest_rate_applied":float(data["interest_rate"]),
                         "Corrected_interest_rate":interest_rate,
                         "tenure":int(data["tenure"]),
                         "monthly_installment":monthly_emi,
                         })
    elif(credit_score < 50 and credit_score >= 30):
        if(lowest_intrest > 12):
            pass
        else:
            lowest_intrest = 12
        print(interest_rate)
        total_intrest = ((float(data['tenure']))/12)*lowest_intrest
        total_amount = ((total_intrest/100)+1)*float(data["loan_amount"])
        monthly_emi = int((total_amount)/int(data["tenure"]))
        loan = Loan.objects.create(
            customer_id= user.id,
            loan_amount = data["loan_amount"],
            interest_rate = lowest_intrest,
            tenure =  data["tenure"],
            monthly_payment = monthly_emi,
            approvel_date = today_date,
            end_date = today_date,
            EMI_on_Time = 0
            
        )
        return Response({"customer_id":user.id,
                         "loan":loan.id,
                         "credit_score":credit_score,
                         "loan_approved":loan_approved,
                         "interest_rate_applied":float(data["interest_rate"]),
                         "Corrected_interest_rate":lowest_intrest,
                         "tenure":int(data["tenure"]),
                         "monthly_installment":monthly_emi,
                         })
    elif(credit_score < 30 and credit_score >= 10):
        
        if(lowest_intrest > 16):
            pass
        else:
            lowest_intrest = 16

        total_intrest = ((float(data['tenure']))/12)*lowest_intrest
        total_amount = ((total_intrest/100)+1)*float(data["loan_amount"])
        monthly_emi = int((total_amount)/int(data["tenure"]))
        loan = Loan.objects.create(
            customer_id= user.id,
            loan_amount = data["loan_amount"],
            interest_rate = lowest_intrest,
            tenure =  data["tenure"],
            monthly_payment = monthly_emi,
            approvel_date = today_date,
            end_date = today_date,
            EMI_on_Time = 0
            
        )
        return Response({"customer_id":user.id,
                         "loan":loan.id,
                         "credit_score":credit_score,
                         "loan_approved":loan_approved,
                         "interest_rate_applied":float(data["interest_rate"]),
                         "Corrected_interest_rate":lowest_intrest,
                         "tenure":int(data["tenure"]),
                         "monthly_installment":monthly_emi,
                         })
    else:
        return Response({"msg":"ok",
                        "Percent of onTime":credit_score_by_emi,
                        "Credit Score":credit_score, 
                        "No. of lons":total_loan,
                        "Currunt amount":total_currunt_loan_amount,
                        "ongoing_loan":ongoing_loan,
                        "Volume":loan_volume,
                        'current_emi':current_emi,
                        "Loan_approved":False,
                        "message":"Your Past Data is not Enough to Approva this loan"
                        })
    

@api_view(["GET"])
@csrf_exempt
def view_loan(request,id):
    try:
        loan = Loan.objects.get(id = id)
        user = Customer.objects.get(id = loan.customer_id)
    except Exception as e:
        return Response({"msg":str(e)})
    
    user_seriliser = CustomerSerializers(user)
    print((user_seriliser))
    return Response({
        "loan_id":loan.id,
        "loan_amount":loan.loan_amount,
        "interest_rate":loan.interest_rate,
        "monthly_installment":loan.monthly_payment,
        "tenure":loan.tenure,
        "customer":user_seriliser.data
    })


@api_view(["GET"])
@csrf_exempt
def view_loans(request,id):
    try:
        user = Customer.objects.get(id = id)  
        loans = Loan.objects.filter(customer_id = id)
    except Exception as e:
        return Response({"msg":str(e)})
    today_date = datetime.now().date()
    
    list_of_loans = {"total_Loans":len(loans)}
    count = 0
    for i in loans:
        if(today_date < i.end_date):
            list_of_loans[count]  = (LoanSerializers(i).data)
            count+=1
    return Response(list_of_loans)

