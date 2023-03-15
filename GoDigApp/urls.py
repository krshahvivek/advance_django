from django.shortcuts import render
from django.urls import path
# from GoDigApp import views
from . import views


app_name = "GoDigApp"

urlpatterns=[
  path('savePetroliumPrice/', views.saveCurrentPetroliumPrices),
  path('enrollUser/',views.enrollUser),
  # path('getPasscode/',views.getPasscode),
  path('verifyAllFields/',views.verifyAllFields,name='verifyAllFields'),
  # path('verifyPasscode/',views.verify_passcode,name='verifyPasscode'),
  path('registration/',views.registration,name='registration'),
  path('login/',views.login,name='login'),
  path('csvToTable/',views.CSVIntoProductionTable,name='CSVIntoProductionTable'),
  path('getOilData/',views.getOilProductionData,name='getOilProductionData'),
  path('getGasData/',views.getOilProductionData,name='getGasProductionData'),
  path('getCBMData/',views.getOilProductionData,name='getCBMProductionData'),
  path('getCondensateData/',views.getOilProductionData,name='getCondensateProductionData'),
  
]