from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
import psycopg2
            

app = Flask(__name__)

logged = False
user = ''
ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:DataBase01@localhost/yachtCharter'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
try:
    con = psycopg2.connect(
        host = 'localhost',
        database = 'yachtCharter',
        user = 'postgres',
        password = 'DataBase01',
    )

    con.autocommit(True)
except:
    print("ISSUES")





@app.route('/') #Solo / perché è per la home
def index():
    global user
    if logged:
        return render_template('index.html', username=user, reg=1)
    return render_template('index.html', reg=0)

@app.route('/query/') # questo gestisce la richiesta post
def querozzalaprima():
    print('collegami tutto')
    return render_template('success.html')

@app.route('/insertboat/', methods=['POST'])
def insertboat():
    global user
    boat_hull_number = request.form['hull_number']
    boat_name = request.form['boat_name']
    boat_sail_number = request.form['sail']
    boat_maker = request.form['maker']
    boat_construction_year = request.form['year']
    boat_launching = request.form['launching']
    located_seaport_ID = request.form['seaport']
    model_name = request.form['model_name']
    
    cur = con.cursor()
    cur.execute('INSERT INTO Boat (boat_hull_number, boat_name, boat_sail_number, boat_maker, boat_construction_year, boat_launching, located_seaport_ID, model_name) values (%s,%s,%s,%s,%s,%s,%s,%s)', (boat_hull_number, boat_name,boat_sail_number, boat_maker,boat_construction_year,boat_launching,located_seaport_ID,model_name))
    con.commit()
    cur.close()
    if logged:
        return render_template('success.html', username=user, reg=1)
    return render_template('success.html')

@app.route('/insertemployee/', methods=['POST'])
def insertemp():
    emp_id              = request.form['emp_id']
    emp_start_date      = request.form['emp_start_date']
    emp_end_date        = request.form['emp_end_date']
    emp_position_id     = request.form['emp_position_id']
    emp_mail            = request.form['emp_mail']
    emp_work_schedule   = request.form['emp_work_schedule']
    emp_role            = request.form['emp_role']
    person_ID_num       = request.form['person_ID_num']
    company_phone       = request.form['company_phone']
    phone_country_code  = request.form['phone_country_code']
    login_ID            = request.form['login_ID']
    contract_number     = request.form['contract_number']
    off_code            = request.form['off_code']
    
    cur = con.cursor()
    cur.execute('INSERT INTO Employee (emp_id, emp_start_date, emp_end_date, emp_position_id, emp_mail, emp_work_schedule, emp_role, person_ID_num, company_phone, phone_country_code, login_ID, contract_number, off_code) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', (emp_id, emp_start_date, emp_end_date, emp_position_id, emp_mail, emp_work_schedule, emp_role, person_ID_num, company_phone,phone_country_code, login_ID, contract_number, off_code))
    con.commit()
    cur.close()
    if logged:
        return render_template('success.html', username=user, reg=1)
    return render_template('success.html')

@app.route('/insertcust/', methods=['POST'])
def insertcust():
    person_name              = request.form['name']
    person_surname      = request.form['surname']
    login_username        = request.form['username']
    login_password     = request.form['password']
    person_email            = request.form['email']
    person_address   = request.form['address']
    person_birth_date            = request.form['birthdate']
    person_ID_num       = request.form['ID_num']
    document_release_date = request.form['ID_release']
    phone_country_code = request.form['phone_country_code']
    phone_number = request.form['phone_number']
    print(login_password)
    cur = con.cursor()
    cur.execute('''INSERT INTO Person 
                (person_ID_num, person_name, person_surname, person_birth_date, person_address, person_email) 
                values (%s,%s,%s,%s,%s,%s)''', 
                (person_ID_num, person_name, person_surname, person_birth_date, person_address, person_email))
    
    

    cur.execute('''INSERT INTO Customer 
                (cust_ID_num, ins_id, login_username) 
                values (%s,%s,%s)''', 
                (person_ID_num, 0, login_username))
    

    
    cur.execute('''INSERT INTO Login_Credential 
                (login_username, login_password) 
                values (%s,%s)''', 
                (login_username, login_password))
    
    cur.execute('''INSERT INTO Document
                (document_number ,document_type, document_release_date, person_ID_num) 
                values (%s,%s,%s,%s)''', 
                (person_ID_num, "ID-Card", document_release_date, person_ID_num))
    

    if phone_country_code and phone_number:
        cur.execute('''INSERT INTO Phone 
                (phone_country_code ,phone_number,  person_ID_num) 
                values (%s,%s,%s)''', 
                (phone_country_code, phone_number,  person_ID_num))
    con.commit()
    cur.close()
    print(user)
    logged = True
    user = login_username
    return render_template('index.html', reg=1, username=login_username)

@app.route('/login/', methods = ['POST'])
def login():
    global user
    global logged
    login_username = request.form['username']
    pwd = request.form['pwd']
    
    
    
    cur = con.cursor()
    cur.execute('SELECT login_username from login_credential')
    usernames = cur.fetchall()
    usernames = [el[0] for el in usernames]
    # cur.close()
    # cur = con.cursor()
    
    
    if login_username not in usernames:
        print("esco qui")
        flash("piatelo piatelo, questo non sta nel nostro database")
        return render_template("createcust.html")
    
    
    cur.execute('SELECT login_password from login_credential where login_username = %s', (login_username,))
    real_pwd = cur.fetchall()[0][0]
    if real_pwd != pwd:
        flash("wrong password")
        print("o qui")
        return render_template("login.html")
    
    logged = True
    user = login_username
    return render_template('index.html', reg=1, username=user)
    

@app.route('/queryboat1/', methods = ['POST'])
def queryboat():
    boat_name = request.form['boat_name']
    print(boat_name)
    cur = con.cursor()
    cur.execute('SELECT boat_hull_number,model_name FROM Boat WHERE boat_name = %s', (boat_name,))
    con.commit()
    tutto = cur.fetchall()
    print(tutto)
    hull = tutto[0][0]
    model = tutto[0][1]
    
    cur.close()
    if logged:
        return render_template('success.html', username=user, reg=1,hull=hull, model=model, inp=boat_name)
    return render_template('boats.html', hull=hull, model=model, inp=boat_name, reg=0)

@app.route('/queryemp1/', methods = ['POST'])
def queryemp1():
    off_code = request.form['off_code']
    
    cur = con.cursor()
    cur.execute('SELECT phone_country_code  FROM Employee WHERE off_code = %s', (off_code,))
    con.commit()
    tutto = cur.fetchall()
    print(tutto)
    
    
    cur.close()
    if logged:
        return render_template('crew.html', username=user, reg=1, ccs=tutto, inp=off_code)
    return render_template('crew.html', ccs=tutto, inp=off_code)


@app.route('/changeb')
def changeb():
    if logged:
        return render_template('boats.html', username=user, reg=1)
    return render_template('boats.html', reg=0)

@app.route('/changec')
def changec():
    if logged:
        return render_template('crew.html', username=user, reg=1)
    return render_template('crew.html',reg=0)

@app.route('/changelogin')
def changelogin():
    if logged:
        return render_template('login.html', username=user, reg=1)
    return render_template('login.html' ,reg=0)

@app.route('/createcust')
def createcust():
    if logged:
        return render_template('createcust.html', username=user, reg=1)
    return render_template('createcust.html', reg=0)

@app.route('/success')
def success():
    global user
    global logged
    user = ""
    logged = False
    flash("Logged out successfully")
    if logged:
        return render_template('index.html', username=user, reg=1)
    return render_template('index.html' ,reg=0)

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run()
    