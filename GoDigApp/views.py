from django.shortcuts import render
# from datetime 
import datetime
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.views import APIView
from django.http import Http404
# from .models import Rates, User
import pyotp
import json
import uuid,re
import base64
import smtplib
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from .src.generate_key import GenerateKey
import requests
from .src.data import Data
import os
import pathlib


@csrf_exempt
def getPasscode(request):
    if request.method != 'POST':
        return JsonResponse({'msg':'Method not allowed'})
    data = json.loads(request.body)
    email = data["email"]
    keygen = GenerateKey()
    validEmail = keygen.isValidemail(email)
    if not validEmail:
        return JsonResponse({'message':'Sorry! Email is invalid.'})
    try:
        pass
    except ObjectDoesNotExist:
        pass
        # created Data
    key = base64.b32encode(keygen.returnValue(email).encode())  # Key is generated
    subject = "Enquest Login Id"
    message = f"""
        {key} to your mail \n\n{email} 
        \nby enquest login system"""
    
    keygen.send(subject=subject,message=message, recipients=[email])
    try:
    #     DataBase connection in case of storing the uuid with email
        keygen.send(subject=subject,message=message, recipients=[email])
    except:
        return JsonResponse({'message':'Sorry! Code was not shared due to server side.'})
    
    return JsonResponse({"message": f"Data sent to you email id - {email}", "status":200})

@csrf_exempt
def saveCurrentPetroliumPrices(request):
    configDir = os.path.join(pathlib.Path(__file__).parents[1], "config")
    with open(os.path.join(configDir, "config.json")) as configFile:
        config = json.load(configFile)

    with open(os.path.join(configDir, config["secretsJson"])) as secretsJson:
        config["secrets"] = json.load(secretsJson)
    
    prices= dict()
    data=Data(config = config)
    base_currency = 'USD'
    symbol = ['BRENTOIL','NG']
    petroliumType = ["CrudeRate", "GasRate", "CBMRate", "CondensateRate"]
    endpoint = 'latest'
    access_key = config["comodityAccessKey"]
    prices["Date"] = datetime.date.today()
    for idx, sym in enumerate(symbol):
        resp = requests.get(
            'https://commodities-api.com/api/'+endpoint+'?access_key='+access_key+'&base='+base_currency+'&symbols='+sym)
        if resp.status_code != 200:
            # This means something went wrong.
            raise KeyError('GET /'+endpoint+'/ {}'.format(resp.status_code))
        # print(f'::::{sym}::: {resp.json()["data"]["rates"][sym]}::')
        symData = (1/ resp.json()["data"]["rates"][sym])
        prices[petroliumType[idx]]=round(symData,2)
    
    prices["CBMRate"] = 49.7
    prices["CondensateRate"] = 44.7
    data.addNewRowInTable(tableName="petrolium_rates", values=prices, schema = "digipi")
    print(prices)
    return JsonResponse({"message": "Petrolium Price uploaded", "status":200})
    

