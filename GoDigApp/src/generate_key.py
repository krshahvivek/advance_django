import re
from django.core.mail import send_mail
from django.conf import settings


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
    def send(subject, message, recipients):
        send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=recipients)

