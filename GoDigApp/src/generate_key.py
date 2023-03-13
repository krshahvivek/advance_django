import re
from django.core.mail import send_mail
from django.conf import settings
import base64
import smtplib


class GenerateKey:
    @staticmethod
    def isValidemail(email):
        # pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]$+\.[A-Z|a-z]$\b'
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        print(email)
        if re.fullmatch(pattern, email):
            return True
        else:
            return False
    @staticmethod
    def returnValue(email):
        return str(email) +  "Some Random Secret Key"
    @staticmethod
    def send(email, recipients):
        key = base64.b32encode(GenerateKey.returnValue(email).encode())  # Key is generated
        print('\n', key, '\n')
        subject = "Enquest Login Id"
        message = f"""
            {key} to your mail \n\n{email} 
            \nby enquest login system"""        
        try:
        #     DataBase connection in case of storing the uuid with email
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=recipients)
        except:
            return 0
        return key
        

