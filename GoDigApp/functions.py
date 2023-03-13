import re

def RegisterAsAdmin(**kwargs):
    # if not (Name and Number and Email and Password and EnterAdminID and RegisterAs):
    #         return JsonResponse({"status_code": 400,"title": "Bad Request","success": False,"msg":"Please Define Name, Number, Email, AdminID, Register AS"})
    pass
def valid_mobile(mobile):
    if (not mobile):
        return False
    elif (len(mobile) != 13):
        return False
    elif (not re.search('^\+91', mobile)):
        return False
    else:
        return True

def validate_password(password):
    alphanumeric_pattern = r'\w'
    special_character_pattern = r'[^\w\s]'
    # Check if the password contains at least one alphanumeric character and one special character
    if re.search(alphanumeric_pattern, password) and re.search(special_character_pattern, password):
        return True
    else:
        return False