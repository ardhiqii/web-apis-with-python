from flask import Flask, jsonify, request, render_template, make_response, url_for,redirect,session
import json
import jwt # Perlu install pip3 install PyJWT diawal
import datetime
import urllib.request, json
from functools import wraps
from flask_mysqldb import MySQL
from flask_mail import Mail,Message #pip install Flask-Mail
from user import *
from data.crimes import *
# Intitialise the app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'tubes-tst'

mysql = MySQL(app)
table = 'estimated_crimes'

app.config.from_pyfile('config.cfg')
mail = Mail(app)

app.config['SECRET_KEY'] ='needbucin'
# Token Required
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'token' not in session:
            return redirect('/login')
        try:
            data = jwt.decode(session['token'],app.config['SECRET_KEY'],algorithms=['HS256'])
        except:
            session.pop('token',None)
            session.pop('user',None)
            return jsonify({'message':'Token is invalid'}),403
        return f(*args,**kwargs)
    return decorated
def authorization_Admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        data = jwt.decode(session['token'],app.config['SECRET_KEY'],algorithms=['HS256'])
        if data['role'] != 'admin':
            return ({'message':'you do not permission to access '})
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
# Login
@app.route('/login',methods=['GET','POST'])
def login():
    if 'user' in session:
        return redirect('/')
    if request.method == 'POST':
        form = request.form
        username = form['username']
        password = form['password']
        if checkValidation(username,password):
            print('VALIDASI')
            session['user'] = username
            session['email'] = user[username]['email']
            return redirect('/verify')
        else:
            return('Password atau username salah')
    return render_template('login.html')

@app.get('/logout')
def test():
    session.pop('user',None)
    session.pop('token',None)
    return('pusing')


@app.route('/verify',methods=['GET','POST'])
def verify():
    email = session['email']
    msg = Message('Code OTP',sender='tst@bismsillah.com',recipients=[email])
    otp = generateOTP()
    session['otp'] = otp
    msg.body = f'Hello your OTP is: {otp}'
    print(session['user'])
    print(email)
    # print(userData['emai'])
    print(otp)
    # mail.send(msg)
    return render_template('verify.html')

@app.route('/validate',methods=['POST'])
def validate():
    userOTP = request.form['otp']
    if session['otp'] == userOTP:
        username = session['user']
        token = jwt.encode({'user':username,'role':user[username]['role'], 'exp':datetime.datetime.utcnow()+datetime.timedelta(seconds=30)},app.config['SECRET_KEY'])
        session['token'] = token
        
        return 'OTP valid'
    else:
        return 'OTP salah'

# # Define what the app does
@app.get("/")
def home():
    return ('Home Page API Crime :D')

@app.route("/show",methods=['GET','POST'])
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
    return render_template('index.html',data = data)

@app.route("/create",methods=['GET','POST'])
@token_required
@authorization_Admin
def create():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        form = request.form
        year = form['year']
        stateAbbr = form['state_abbr']
        stateName = form['state_name']
        query = f'insert into {table} (year,state_abbr,state_name) values ({year},"{stateAbbr}","{stateName}")'
        cur.execute(query)
        print(query)
        mysql.connection.commit()
        return 'success'

    return render_template('create.html')
@app.route('/update',methods=['GET','POST','PUT'])
@token_required
@authorization_Admin
def update():
    cur = mysql.connection.cursor()
    if request.method == 'PUT':
        payload = request.get_json()
        year = payload['year']
        stateAbbr = payload['state_abbr']
        stateName = payload['state_name']
        query = f'update {table} set state_name = "{stateName}" where year = {year} and state_abbr ="{stateAbbr}"'
        cur.execute(query)
        print(query)
        mysql.connection.commit()
    return render_template('update.html')
@app.route('/delete',methods=['GET','POST','DELETE'])
@token_required
@authorization_Admin
def delete():
    cur = mysql.connection.cursor()
    if request.method == 'DELETE':
        payload = request.get_json()
        year = payload['year']
        query = f'delete from {table} where year = {year}'
        cur.execute(query)
        mysql.connection.commit()
    return render_template('delete.html')


########### Core API ############
def calculateCrimeRate(population,crime):
    crimeRate = crime/population
    crimeRate = crimeRate * 100000
    return round(crimeRate,2)

@app.route('/core-api',methods=['GET','POST'])
@token_required
def CoreApi():
    cur = mysql.connection.cursor()
    state_name = request.args.get("stnam")
    theMostCrime = request.args.get('maxCrime')
    allTotal = 0
    cur.execute(f'''select population from {table} where state_name != "" and state_name = "{state_name}" and year = 2019 ''')
    population = cur.fetchall()
    population = int(population[0][0])
    for c in crimes:
        query = f'''select {c['crime']} from {table} where state_name != "" and state_name = "{state_name}" and year = 2019 '''
        cur.execute(query)
        total = cur.fetchall()
        total = total[0][0]
        if total is not None:
            total = int (total)
        else:
            total = 0
        c['total'] = total
        allTotal += total
        if maxCrime['total'] < total:
            maxCrime['total'] = total
            maxCrime['crime'] = c['crime']    
    if theMostCrime == 'true':
        return(maxCrime)
    crimeRate = calculateCrimeRate(population,allTotal)
    return ({"state":state_name,
    "population":population,
    "totalCrime":allTotal,
        "crimeRate":crimeRate})


########### Support Data for Dito ############
@app.route('/data/crimesRate',methods=['GET','POST'])
def dataCrimesRate():
    cur = mysql.connection.cursor()
    supportData = []
    average = request.args.get('average')
    cur.execute('select distinct state_name from estimated_crimes ec where state_name != "" order by state_name')
    stateName = cur.fetchall()
    count = 0
    totalCrimeRate = 0
    for s in stateName:
        count+=1
        totalCrime = 0
        state = s[0]
        # Get Population
        cur.execute(f'''select population from {table} where state_name != "" and state_name = "{state}" and year = 2019 ''')
        population = cur.fetchall()
        population = int(population[0][0])
        # Get Total Crime
        for c in crimes:
            query = f'''select {c['crime']} from {table} where state_name != "" and state_name = "{state}" and year = 2019 '''
            cur.execute(query)
            total = cur.fetchall()
            total = total[0][0]
            if total is not None:
                total = int (total)
            else:
                total = 0
            totalCrime += total
        crimeRate = calculateCrimeRate(population,totalCrime)
        totalCrimeRate += crimeRate
        tmp = {
            "count":count,
            "state":state,
            "crimeRate":crimeRate,
            "population":population,
            "totalCrime":totalCrime
        }
        # tmp = {
        #     "state":state,
        #     "population":population,
        #     "total":totalCrime
        # }
        supportData.append(tmp)
    if average == 'true':
        value = totalCrimeRate/count
        return({"average":value,
        "count":count,
        "totalCrimeRate":totalCrimeRate})
    return(supportData)


if __name__ == "__main__":
    app.run(debug=True)
