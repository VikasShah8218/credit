from django.urls import path
from . import views

urlpatterns = [
    path('test', views.test),
    path('register', views. register),
    path('upload-customer',views.upload_customer),
    path('upload-loan',views.upload_loan),
    path('check-eligibility',views.check_eligibility),
    path('create-loan',views.create_loan),
    path('view-loan/<int:id>',views.view_loan),
    path('view-loans/<int:id>',views.view_loans),
]
