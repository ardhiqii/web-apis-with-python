from flask import Flask, jsonify, request, render_template, make_response, url_for,redirect
import json
import jwt # Perlu install pip3 install PyJWT diawal
import datetime
from functools import wraps
from flask_mysqldb import MySQL
from flask_mail import Mail,Message #pip install Flask-Mail
from user import *
# Intitialise the app
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'testtst'

mysql = MySQL(app)
table = 'estimated_crimes_1979_2019'

app.config.from_pyfile('config.cfg')
mail = Mail(app)

app.config['SECRET_KEY'] ='needbucin'
storage = []
userData = {
    "email" : '',
    "otp": ''
}

# Token Required
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if len(storage) == 0:
            return jsonify({'message':'Tokekn is missing'}),403
        try:
            data = jwt.decode(storage[0],app.config['SECRET_KEY'],algorithms=['HS256'])
        except:
            return jsonify({'message':'Token is invalid'}),403
        return f(*args,**kwargs)
    return decorated
# API KEY Required
def api_key_required(f) :
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.args.get('apiid')
        if key != app.config['API_KEY']:
            print(key)
            print(app.config['API_KEY'])
            print(key != app.config['API_KEY'])
            return jsonify({'message':'API KEY tidak ada atau tidak valid'})
        return f(*args,**kwargs)
    return decorated
#Login
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        form = request.form
        username = form['username']
        password = form['password']
        if checkValidation(username,password):
            token = jwt.encode({'user':username, 'exp':datetime.datetime.utcnow()+datetime.timedelta(seconds=10)},app.config['SECRET_KEY'])
            storage.append(token)
            return render_template('login.html',token=token)
        else:
            return('Password atau username salah')
    return render_template('login.html')
# # Define what the app does
@app.route("/",methods=['GET','POST'])
def index():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        form = request.form
        year = form['year']
        if not year:
            cur.execute(f'''select * from {table} limit 10''')
            data = cur.fetchall()
            return render_template('index.html',data = data)
        cur.execute(f'select * from {table} where year = {year} limit 10')
        data = cur.fetchall()
        return render_template('index.html',data = data)
    cur.execute(f'''select * from {table} limit 10''')
    data = cur.fetchall()
    print(f'storage: {storage}')
    return render_template('index.html',data = data)

@app.route('/create',methods=['GET','POST'])
@api_key_required
def create():
    return ('butuh api key')
# Test Email
# https://stackoverflow.com/questions/72547853/unable-to-send-email-in-c-sharp-less-secure-app-access-not-longer-available/72553362#72553362
@app.route('/email',methods=['GET'])
def sendEmail():
    return render_template('email.html')

@app.route('/verify',methods=['GET','POST'])
def verify():
    email = request.form['email']
    userData['emai'] = email
    msg = Message('Confirm Email',sender='test@fuck.com',recipients=[email])
    otp = generateOTP()
    userData['otp'] = otp
    msg.body = f'Hello your OTP is: {otp}'
    print(email)
    # print(userData['emai'])
    print(otp)
    mail.send(msg)
    return render_template('verify.html')

@app.route('/validate',methods=['POST'])
def validate():
    userOTP = request.form['otp']
    if userData['otp'] == userOTP:
        token = jwt.encode({'user':userData['emai'], 'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=10)},app.config['SECRET_KEY'])
        storage.append(token)
        return 'OTP valid'
    else:
        return 'OTP salah'
if __name__ == "__main__":
    app.run(debug=True)
