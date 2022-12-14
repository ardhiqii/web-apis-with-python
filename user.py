import random
user = {
    'aufa':{
        "password":"sunardi",
        'email':'ardhiqi@gmail.com',
        "role":"user"
    },
    'dito':{
        "password":"leo",
        "email":'ammarditoshafaat2001@gmail.com',
        "role":"admin"
    }
}

def checkValidation(username,password):
    try:
        pw = user[username]['password']
        if pw == password:
            # currentUser['name'] = username
            # currentUser['email'] = user[username]['email']
            # currentUser['role'] = user[username]['role']
            return True
        else:
            return False
    except:
        return False
def generateOTP():
    finalOTP= ''
    for i in range (4):
        finalOTP = finalOTP + str(random.randint(0,9))
    return finalOTP
