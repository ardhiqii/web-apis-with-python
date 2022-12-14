import random
user = {
    'aufa':'yepyepyep',
    'rakha':'hedon',
    'kafi':'player',
    'dafeb':'dafap',
    'dito':'meong'
}

def checkValidation(username,password):
    try:
        pw = user[username]
        if pw == password:
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
