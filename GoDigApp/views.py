from django.shortcuts import render
import datetime
# from rest_framework.response import Response
from django.http import JsonResponse
# from rest_framework.views import APIView
from django.http import Http404
from .utils import EmailValidate
# import pyotp
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
from GoDigApp.functions import valid_mobile, validate_password
from .models import AuthUserEmails, User, LoginUuids, GroupAdmins, Groups


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
    
@csrf_exempt
def EnrollUser(request):
    if request.method != 'POST':
        return JsonResponse({'message':'Method not allowed'})
    email = None
    data = json.loads(request.body)
    Email = data["Email"]
    adminId = data["AdminID"]
    groupId = data["GroupID"]
    if not (Email and groupId and adminId): return JsonResponse({'message':'Please Enter your Admin Id, Email and group id', 'status_code':406,"title":"NOT ACCEPTABLE"}, safe=False)
    email = Email.lower()
    validEmail = EmailValidate(email=email)
    if not validEmail: return JsonResponse({'message':'Please Enter Valid Email ID', 'status_code':406,"title":"NOT ACCEPTABLE"}, safe=False)
    try:
        groupAdmin = GroupAdmins.objects.filter(adminemailid=adminId)
        authUserEmails = AuthUserEmails()
        authUserEmails.emailid=email
        authUserEmails.permitas=groupId
        authUserEmails.adminid=groupAdmin[0]
        authUserEmails.save()
    except:
        return JsonResponse({'status_code':500,'title': 'Bad Request','message':'Sorry! Error from server end.'}, safe=False)
    return JsonResponse({"message": f"Email id {email} successfully has been saved", "status":200}, safe=False)

@csrf_exempt
def getPasscode(request):

    if request.method != 'POST':
        return JsonResponse({'message':'Method not allowed'})
    email,adminEmail,key = (None,)*3
    data = json.loads(request.body)
    Email = data["Email"]
    adminID = data.get("AdminID")
    groupID = data["GroupID"]
    if not (Email and groupID):
        return JsonResponse({'message':'Please Enter Email and group id', 'status_code':406,"title":"NOT ACCEPTABLE"}, safe=False)
    if Email and adminID:
        email = Email.lower()
        adminEmail = adminID.lower()
        validEmail = EmailValidate(email=email)
        validAdminEmail = EmailValidate(email=adminEmail)
        if not (validEmail and validAdminEmail): 
            return JsonResponse({'message':'Please Enter Valid Email ID', 'status_code':406,"title":"NOT ACCEPTABLE"}, safe=False)
    else:
        email = Email.lower()
        validEmail = EmailValidate(email=email)
        if not validEmail: 
            return JsonResponse({'message':'Please Enter Valid Email ID', 'status_code':406,"title":"NOT ACCEPTABLE"}, safe=False)
    keygen = GenerateKey()
    # validEmail = keygen.isValidemail(email)
    # if not validEmail:
    #     return JsonResponse({'message':'Sorry! Email is invalid.'})
    try:
        key = keygen.send(email, recipients=[email])
    except:
        return JsonResponse({'message':'Sorry! Code was not shared due to server side.'})
    if groupID == 4:
        try:
            """Send Email connection """
            create_date = datetime.datetime.today()
            login = LoginUuids(uuid=key,emailid=email,createdon=create_date)
            login.save()
        except ObjectDoesNotExist:
            return JsonResponse({'status_code':500,'title': 'Internal server Error','message':'Sorry! Code was not shared due to server side.'})
    else:
        try:
            if not adminID: return JsonResponse({'message':'Please Enter Admin id', 'status_code':406,"title":"NOT ACCEPTABLE"}, safe=False)
            auth_user = AuthUserEmails.objects.filter(emailid=email)
            tableAdminId = auth_user[0].adminid.adminid
            groupAdmintable = GroupAdmins.objects.get(adminid=tableAdminId)
            tableAdminEmail = groupAdmintable.adminemailid
            if not (tableAdminEmail == adminEmail) : return JsonResponse({'status_code':400,'title': 'Bad Request','message':'Sorry! You are not authorized to Register.'})
            tablePermitAs = auth_user[0].permitas
            if not (tablePermitAs == groupID): return JsonResponse({'status_code':400,'title': 'Bad Request','message':'Sorry! You are not authorized to  Register as you want.'})
            emailid = auth_user[0].emailid
            if emailid == email:
                create_date = datetime.datetime.today()
                login = LoginUuids(uuid=key,emailid=email,createdon=create_date)
                login.save()
            else:
                return JsonResponse({'status_code':400,'title': 'Bad Request','message':'Sorry! You are not authorized to get passcode.'})
        except:
            return JsonResponse({'status_code':500,'title': 'Bad Request','message':'Sorry! Error from server end.'})
    return JsonResponse({"message": f"Data sent to you email id - {email}", "status":200})

#resend otp
# @csrf_exempt
# def resendPasscode(request):
#     import pdb
#     pdb.set_trace()
#     if request.method != 'POST':
#         return JsonResponse({'message':'Method not allowed'})
#     data = json.loads(request.body)
#     email = data["email"]
#     keygen = GenerateKey()
#     try:
#         """Send Email connection"""
#         key = keygen.send(email, recipients=[email])
#     except:
#         return JsonResponse({'status_code':500,'title': 'Internal server Error','message':'Sorry! Code was not shared due to email server side.'})
#     try:
#         """DataBase connection in case of storing the uuid with email"""
#         create_date = datetime.datetime.today()
#         auth_user = AuthUserEmails.objects.filter(emailid=email)
#         email_key = auth_user[0].emailkey
#         login = LoginUuids(uuid='giogfintwiotuynisougbnoisbng',emailkey=email_key,createdon=create_date)
#         login.save()
#     except ObjectDoesNotExist:
#         return JsonResponse({'status_code':500,'title': 'Internal server Error','message':'Sorry! Code was not shared due to server side.'})
#     return JsonResponse({"message": f"Data sent to you email id - {email}", "status":200})

@csrf_exempt
def getVerifiedAllField(request):
    request_body = json.loads(request.body)
    Name = request_body["Name"]
    Number = request_body["Number"]
    Email = request_body["Email"]
    Password = request_body["Password"]
    EnterAdminID = request_body.get("AdminID")
    RegisterAs = request_body["GroupID"]
    EnterPassCode = request_body["Passcode"]
    
    validEmail = GenerateKey.isValidemail(Email)
    validMobile = valid_mobile(Number)
    validPassword = validate_password(Password)

    if not RegisterAs: return JsonResponse({"status_code": 400,"title": "Bad Request","success": False,"message":"Please Define! How would you like to Register AS"})
    if not validEmail: return JsonResponse({"status_code": 400,"title": "Bad Request","success": False,"message":"Please Enter Correct Email ID"})
    if not validMobile: return JsonResponse({"status_code": 400,"title": "Bad Request","success": False,"message":"Please Enter Correct Number '+91XXXX"})
    if not validPassword: return JsonResponse({"status_code": 400,"title": "Bad Request","success": False,"message":"Password must contain 1 numeric, character and special character"})
    
    if RegisterAs != 4:
        if not (Name and Number and Email and Password and EnterPassCode and EnterAdminID):
            return JsonResponse({"status_code": 400,"title": "Bad Request","success": False,"message":"Please Define Name, Number, Email, Password and Register AS, All"})        
    else:
        if not (Name and Number and Email and Password and EnterPassCode):
            return JsonResponse({"status_code": 400,"title": "Bad Request","success": False,"message":"Please Define Name, Number, Email, Password and Register AS, All"})
    return JsonResponse({"status":200, "success": True, "message": "Your all field verified successfully"})

@csrf_exempt
def verifyPasscode(request):
    if request.method != 'POST':
        return JsonResponse({"status_code": 405, "title":"Method not allowed", "message": f"{request.method} method not allowed."}, safe=False)
    auth_email,email,loginPasscode,adminEmail = (None,)*4
    data = json.loads(request.body)
    Email = data["Email"]
    adminID = data["AdminID"]
    groupID = data["GroupID"]
    EnterPassCode = data["Passcode"]
    if not EnterPassCode:
        return JsonResponse({"status_code":400,"title": "Bad Request", 'message':'Please enter your passcode'}, safe=False)
    if Email and adminID:
        email = Email.lower()
        adminEmail = adminID.lower()
        validEmail = EmailValidate(email=email)
        validAdminEmail = EmailValidate(email=adminEmail)
        if not (validEmail and validAdminEmail): 
            return JsonResponse({'message':'Please Enter Both Valid Email IDs', 'status_code':406,"title":"NOT ACCEPTABLE"}, safe=False)
    else:
        email = Email.lower()
        validEmail = EmailValidate(email=email)
        if not validEmail: 
            return JsonResponse({'message':'Please Enter Valid Email ID', 'status_code':406,"title":"NOT ACCEPTABLE"}, safe=False)
    if groupID == 4:
        loginTable = LoginUuids.objects.filter(emailid=email)
        if not loginTable: return JsonResponse({"status_code":400,"title": "Bad Request", 'message':'You have entered wrong passcode'}, safe=False)
        loginPasscode = loginTable[0].uuid
    else:
        try:
            auth_email = AuthUserEmails.objects.filter(emailid=email)
            admin_id = auth_email[0].adminid.adminid
            group_admin = GroupAdmins.objects.get(adminid=admin_id)
            if adminEmail == group_admin.adminemailid:
                loginTable = LoginUuids.objects.filter(emailid=email)
                loginPasscode = loginTable[0].uuid
        except Exception as e:
            return JsonResponse({"status_code": 500,"title": "Internal server Error","success": False,"message":"sorry you are not authorized to register","error": e},safe=False)
    if EnterPassCode != loginPasscode:
        return JsonResponse({"status_code":400,"title": "Bad Request", 'message':'You have entered wrong passcode'}, safe=False)
    return JsonResponse({"status":200, "success": True, "message": "Your Passcode has been matched successfully"})
   
@csrf_exempt
def Registration(request):
    if request.method != 'POST':
        return JsonResponse({"status_code": 405, "title":"Method not allowed", "message": f"{request.method} method not allowed."}, safe=False)
    auth_user,email,loginPasscode,tableGroups,adminEmail = (None,)*5
    request_body = json.loads(request.body)
    Name = request_body["Name"]
    Number = request_body["Number"]
    Email = request_body["Email"]
    Password = request_body["Password"]
    EnterAdminID = request_body.get("AdminID")
    RegisterAs = request_body["GroupID"]
    EnterPassCode = request_body["Passcode"]
    validMobile = valid_mobile(Number)
    validPasswork = validate_password(Password)

    if not (Name and Number and Email and Password):
        return JsonResponse({"status_code": 400,"title": "Bad Request","success": False,"message":"Please Define Name, Number, Email, Password"})
    if not validMobile: return JsonResponse({"status_code": 400,"title": "Bad Request","success": False,"message":"Please Enter Correnct Number '+91XXXX"})
    if not validPasswork: return JsonResponse({"status_code": 400,"title": "Bad Request","success": False,"message":"Password must contain 1 numeric, character and special character"})
    if not RegisterAs: return JsonResponse({"status_code": 400,"title": "Bad Request","success": False,"message":"Please Define! How would you like to Register AS"})
    if Email and EnterAdminID:
        email = Email.lower()
        adminEmail = EnterAdminID.lower()
        validEmail = EmailValidate(email=email)
        validAdminEmail = EmailValidate(email=adminEmail)
        if not (validEmail and validAdminEmail): 
            return JsonResponse({'message':'Please Enter Valid Email ID', 'status_code':406,"title":"NOT ACCEPTABLE"}, safe=False)
    else:
        email = Email.lower()
        validEmail = EmailValidate(email=email)
        if not validEmail: 
            return JsonResponse({'message':'Please Enter Valid Email ID', 'status_code':406,"title":"NOT ACCEPTABLE"}, safe=False)
    if RegisterAs != 4:
        try:
            if not EnterAdminID: return JsonResponse({"status_code": 400,"title": "Bad Request","success": False,"message":"Please Enter admin id"})
            auth_user = AuthUserEmails.objects.filter(emailid=email)
            tableAdminId = auth_user[0].adminid.adminid
            groupAdmintable = GroupAdmins.objects.get(adminid=tableAdminId)
            tableAdminEmail = groupAdmintable.adminemailid
            if not (tableAdminEmail == adminEmail) : return JsonResponse({'status_code':400,'title': 'Bad Request','message':'Sorry! You are not authorized to Register.'})
            tablePermitAs = auth_user[0].permitas
            tableGroups = Groups.objects.get(groupid=tablePermitAs)
            if not (tablePermitAs == RegisterAs): return JsonResponse({'status_code':400,'title': 'Bad Request','message':'Sorry! You are not authorized to  Register as you want.'})
            emailid = auth_user[0].emailid
            if emailid == email:
                loginID = LoginUuids.objects.filter(emailid=email).order_by('-id')
                loginPasscode = loginID[0].uuid
        except:
            return JsonResponse({"status_code": 500,"title": "Internal server Error","success": False,"message":"sorry, Something happened to the server side","error": e},safe=False)
    if EnterPassCode != loginPasscode: return JsonResponse({"status_code":400,"title": "Bad Request", 'message':'You have entered wrong passcode'}, safe=False)

    if RegisterAs == 1:
        """If User will register as a Adminstrator"""
        DateTime = datetime.datetime.today()
        try:
            User.objects.get_or_create(username=Name,password=Password,groupid=tableGroups,emailid=email,isadmin=1,datecreated=DateTime)
        except  Exception as e:
            return JsonResponse({"status_code": 500,"title": "Internal server Error","success": False,"message":"sorry you are not authorized to register","error": e},safe=False)
    elif RegisterAs == 2:
        """If User will register as a Contractor"""
        DateTime = datetime.datetime.today()
        try:
            User.objects.get_or_create(username=Name,password=Password,groupid=tableGroups,emailid=email,isadmin=0,datecreated=DateTime)
        except Exception as e:
            return JsonResponse({"status_code": 500,"title": "Internal server Error","success": False,"message":"sorry you are not authorized to register","error": e},safe=False) 
    elif RegisterAs == 3:
        """If User will register as a Lisence holder"""
        DateTime = datetime.datetime.today()
        try:
            User.objects.get_or_create(username=Name,password=Password,groupid=tableGroups,emailid=email,isadmin=0,datecreated=DateTime)
        except Exception as e:
            return JsonResponse({"status_code": 500,"title": "Internal server Error","success": False,"message":"sorry you are not authorized to register","error": e},safe=False)               
    elif RegisterAs == 4:
        """If User will register as a User"""
        try:
            loginID = LoginUuids.objects.filter(emailid=email).order_by('-id')
            loginPasscode = loginID[0].uuid
        except:
            return JsonResponse({"status_code": 500,"title": "Internal server Error","success": False,"message":"sorry, Something happened to the server side","error": e},safe=False)
        DateTime = datetime.datetime.today()
        try:
            tableGroups = Groups.objects.get(groupid=RegisterAs)
            User.objects.get_or_create(username=Name,password=Password,groupid=tableGroups,emailid=email,isadmin=0,datecreated=DateTime)
        except Exception as e:
            return JsonResponse({"status_code": 500,"title": "Internal server Error","success": False,"message":"Something happened to the server side","error": e},safe=False)
    else:
        return JsonResponse({"status_code":400,"title": "Bad Request", 'message':'You are registring wrong user type'}, safe=False)
    return JsonResponse({"status_code":200,"title": "OK", 'message':'Registered Successfully.'}, safe=False)

@csrf_exempt
def login(request):
    if request.method != 'POST':
        return JsonResponse({"status_code": 405, "title":"Method not allowed", "message": f"{request.method} method not allowed."}, safe=False)
    email,getPassword = (None,)*2
    request_body = json.loads(request.body)
    # Name = request_body["Name"]
    # Number = request_body["Number"]
    Email = request_body["Email"]
    Password = request_body["Password"]
    if Email:
        email = Email.lower()
        validEmail = EmailValidate(email=email)
        if not validEmail: return JsonResponse({'message':'Please Enter Valid Email ID', 'status_code':406,"title":"NOT ACCEPTABLE"}, safe=False)
    try:
        auth_user = AuthUserEmails.objects.filter(emailid=email)
        if auth_user:
            tableEmailId = auth_user[0].emailid
            userEmail = User.objects.filter(emailid=tableEmailId)
        else:
            return JsonResponse({'message':'Please Enter Correct Email ID', 'status_code':406,"title":"NOT ACCEPTABLE"}, safe=False)        
    except Exception as e:
        return JsonResponse({"status_code": 500,"title": "Internal server Error","success": False,"message":"sorry you are not authorized to register","error": e},safe=False)
    if userEmail: 
        getPassword = userEmail[0].password
        if Password != getPassword: return JsonResponse({'message':'Entered Password is wrong', 'status_code':406,"title":"NOT ACCEPTABLE"}, safe=False)
    else:
        return JsonResponse({"status_code": 500,"title": "Internal server Error","success": False,"message":"sorry you are not authorized to register","error": e},safe=False)
    return JsonResponse({"status_code":200,"title":"OK","success": True,"message":'Login successfully'}, safe=False)


def valid_mobile(mobile):
    if (not mobile):
        return 0
    elif (len(mobile) != 13):
        return 0
    elif (not re.search('^\+91', mobile)):
        return 0
    else:
        return 1

