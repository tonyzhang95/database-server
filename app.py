from flask import Flask, render_template, request, json, redirect, session, url_for
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


app = Flask(__name__)
mysql = MySQL()

app.secret_key = 'simple-server-database'

# MySQL config
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '2020DB!!'
app.config['MYSQL_DATABASE_DB'] = 'WDS'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
print("-----Established Database Connection-----")


@app.route('/')
def index():
    if session.get('user'):
        return redirect('/userHome')
    else:
        return render_template('index.html')


@app.route('/showSignIn')
def showSignIn():
    return render_template('signin.html')


@app.route('/validateLogIn', methods=['POST'])
def validateLogIn():
    try:
        print(request.url)
        print(request.form)

        _username = request.form['inputEmail']
        _password = request.form['inputPassword']

        # connect to MySQL
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_validateLogin',(_username,)) # check if user email is stored in the user table in DB with sp_validateLogin procedure.
        data = cursor.fetchall()

        if len(data) > 0:
            print(str(data[0]))
            if check_password_hash(str(data[0][3]),_password):
                session['user'] = data[0][2]
                return redirect('/userHome')
            else:
                return render_template('error.html',error = 'Wrong Email address or Password.')
        else:
            return render_template('error.html',error = 'Wrong Email address or Password.')

    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        conn.close()


@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')


@app.route('/signUp',methods=['POST','GET'])
def signUp():
    try:
        print(request.url)
        print(request.args)

        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        if _name and _email and _password:

            conn = mysql.connect()
            cursor = conn.cursor()
            _hashed_password = generate_password_hash(_password)
            cursor.callproc('sp_createUser',(_name,_email,_hashed_password))
            data = cursor.fetchall()

            if len(data) == 0:
                conn.commit()
                cursor.close()
                conn.close()

                session['user'] = _email

                if '@' in _email:
                    if _email.split('@')[1] == 'wds.com':
                        return json.dumps({'response': "employee"}) # redirects to employee home
                    else:
                        return json.dumps({'response': "user"})
                else:
                    return json.dumps({'response': "user"}) # redirects to user info page.
            else:
                return json.dumps({'response':'Email existed, please sign in or try with another email.'})
        else:
            return json.dumps({'response':'Enter the required fields'})

    except Exception as e:
        return json.dumps({'error':str(e)})



@app.route('/userHome')
def userHome():
    if session.get('user'):

        print("user: ", session.get('user'))

        cid = 0
        auto_ins = []
        home_ins = []

        conn = mysql.connect()
        cursor = conn.cursor()

        # fetch user account info from mysql
        cursor.execute('select * from wds.user join wds.customer on user.user_id=customer.user_id where user_username = {}'.format('"' + str(session.get('user')) + '"'))
        account = cursor.fetchall()
        if account:
            cid = str(account[0][4])
        else:
            cursor.execute('select * from wds.user where user_username = {}'.format('"' + str(session.get('user')) + '"'))
            account = cursor.fetchall()

        # fetch customer insurances info from mysql
        if cid:
            cursor.execute('select * from wds.insurance i join wds.auto_ins a on i.insid=a.insid where i.cid = {}'.format('"' + cid + '"'))
            auto_ins = cursor.fetchall()
            cursor.execute('select * from wds.insurance i join wds.home_ins h on i.insid=h.insid where i.cid = {}'.format('"' + cid + '"'))
            home_ins = cursor.fetchall()
        # conn.commit()
        cursor.close()
        conn.close()

        print("account:  ", str(account[0]))
        if auto_ins:
            print("auto_ins:  ", str(auto_ins))
        if home_ins:
            print("home_ins:  ", str(home_ins))

        # display account info
        if len(account[0]) < 10:
            user_account = "Username: " + str(account[0][1]) + "\n" + "Accunt/Email: " + str(account[0][2])
        else:
            name = str(account[0][5]) + " " + str(account[0][6])
            if str(account[0][7])=='M':
                gender = "Male"
            elif str(account[0][7])=="Female":
                gender = "Female"
            else:
                gender = "Non-binary"

            if str(account[0][8]) == 'S':
                mari = 'Single'
            elif str(account[0][8]) == 'M':
                mari = 'Married'
            else:
                mari = 'Widow'

            address = " ".join([str(account[0][10]),str(account[0][11]),str(account[0][12]),str(account[0][13]),str(account[0][14])])

            user_info = ", ".join([name, gender, mari, address])


        # display insurances info
        insurances = []
        if auto_ins:
            ins = auto_ins[0]
            insurances.append("Car insurance no." + str(ins[0]) + " from " + str(ins[1].date()) + " to " + str(ins[2].date()) + " for $" + str(ins[3]) + ", for my " + str(ins[9]) + " " + str(ins[7]) + " " + str(ins[8]) + ", with primary driver: " + str(ins[11]) +" "+ str(ins[12]) + " with driver's lisence numbdered " + str(ins[13]) + " born on " + str(ins[14].date()))

        if home_ins:
            ins = home_ins[0]
            print(ins)
            insurances.append("Home insurances no.{} from {} to {} for ${} for my {} squared feet, ${} home, which is purchased/moved-in on {} .".format(str(ins[0]),str(ins[1].date()),str(ins[2].date()),str(ins[3]),str(ins[8]),str(ins[7]),str(ins[6].date())))
        return render_template('userHome.html', user_info = user_info, user_insurance = insurances)
    else:
        return render_template('error.html', error = 'Unauthorized Access')


"""
Process submitted user info form.
"""
@app.route('/processUserInfo', methods = ['POST'])
def processUserInfo():
    try:
        # print("url:", request.url)
        # print("form:", request.form)

        firstname = request.form['firstname']
        lastname = request.form['lastname']
        gender = request.form['gender']
        maritality = request.form['maritality']
        instype = request.form['instype']
        house = request.form['house']
        street = request.form['street']
        city = request.form['city']
        state = request.form['state']
        zipcode = request.form['zipcode']
        username = session['user']

        print(firstname, lastname, gender, maritality, instype, house, street, city, state, zipcode,username)

        if firstname and lastname and gender and maritality and instype and house and street and city and state and zipcode: # check all fields filled
            if gender == "U":
                gender = ""
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_insertCustomerInfo', (firstname, lastname, gender, maritality, instype, house, street, city, state, zipcode, username))
            conn.commit()
            cursor.close()
            conn.close()
            return json.dumps({'response': "success"})
        else:
            return "Error: must fill all fields."
    except Exception as e:
        print(str(e))
        return str(e)


# interface for user info edit
@app.route('/userInfo')
def userInfo():
    if session.get('user'):
        return render_template('userinfo.html')
    else:
        return render_template('error.html', error = 'You need to log-in to access this page.')


# display products and pricing
@app.route('/product')
def product():
    return render_template('product.html')


# interface for car insurance information
@app.route("/carIns")
def carIns():
    if session.get('user'):
        return render_template('carIns.html')
    else:
        return redirect(url_for('index'))


@app.route("/processCarIns", methods=["POST"])
def processCarIns():
    try:
        print("url:", request.url)
        print("form:", request.form)

        # insurance
        start = request.form['insStartDate']
        end = request.form['insEndDate']
        premium = request.form['insPremium']
        type = "A" # for auto

        # car
        vin = request.form['VIN']
        make = request.form['make']
        model = request.form['model']
        year = request.form['year']
        ownership = request.form['ownership']

        #driver
        firstname = request.form['driverFirstName']
        lastname = request.form['driverLastName']
        lisence = request.form['driverLisence']
        birthdate = request.form['DOB']

        # session user
        username = session['user']

        car_ins = [start, end, premium, vin, make, model, year, firstname, lastname, lisence, birthdate]
        print(car_ins)


        if start and end and premium and vin and make and model and year and ownership and firstname and lastname and lisence and birthdate: # check all fields filled

            # check dates

            # MySQL ops
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_insertCarIns', (start, end, premium, vin, make, model, year, ownership, firstname, lastname, lisence, birthdate, username))
            conn.commit()
            cursor.close()
            conn.close()
            return json.dumps({'response': "success {}".format(car_ins)})
        else:
            return "Error: must fill all fields."
    except Exception as e:
        print(str(e))
        return str(e)


# interface for car insurance information
@app.route("/homeIns")
def homeIns():
    if session.get('user'):
        return render_template('homeIns.html')
    else:
        return redirect(url_for('index'))


@app.route("/processHomeIns", methods=["POST"])
def processHomeIns():
    try:
        print("url:", request.url)
        print("form:", request.form)

        # insurance
        start = request.form['insStartDate']
        end = request.form['insEndDate']
        premium = request.form['insPremium']
        type = "H" # for home

        # home
        date = request.form['date']
        value = request.form['value']
        area = request.form['area']
        home_type = request.form['type']
        fire = request.form['fire']
        security = request.form['security']
        pool = request.form['pool']
        basement = request.form['basement']

        # session user
        username = session['user']

        home_ins = [start, end, premium, date, value, area, home_type, fire, security, pool, basement]
        print(home_ins)

        if start and end and premium and date and value and area and home_type and fire and security and pool and basement: # check all fields filled

            # check dates

            # MySQL ops
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_insertHomeIns', (start, end, premium, date, value, area, home_type, fire, security, pool, basement, username))
            conn.commit()
            cursor.close()
            conn.close()
            return json.dumps({'response': "success {}".format(home_ins)})
        else:
            return "Error: must fill all fields."
    except Exception as e:
        print(str(e))
        return str(e)


@app.route('/showPay', methods=['POST'])
def showPay():
    if session.get('user'):
        print("url:", request.url)
        print("form:", request.form)

        number = request.form['invoice_number']
        amount = request.form['invoice_amount']

        return render_template('pay.html', invoice_number = number, invoice_amount = amount)
    else:
        return redirect(url_for('index'))


@app.route('/processPay', methods=['POST'])
def processPay():
    try:
        pay_method = request.form['pay_method']
        amount = request.form['amount']

        payment = ["success", pay_method, amount]

        # SQL INSERT into payment table
        # SQL UPDATE on invoice table, (paid, outstanding)

        return json.dumps({'response': payment})
    except Exception as e:
        return str(e)


@app.route('/showInvoice')
def showInvoice():
    if session.get('user'):

        # retrieve user invoices from DB
        # fake invoice
        invoice1 = {"number":103, "paid":0, "amount":200, "outstanding":200}
        invoice2 = {"number":105, "paid":1, "amount":1000, "outstanding":500}
        invoices = [invoice1, invoice2]

        return render_template('invoice.html', invoices = invoices)
    else:
        return redirect(url_for('index'))


# log out current user
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


# temporary page for todos
@app.route('/todos')
def todo():
    return render_template('todos.html')


# documentation page for this project
@app.route('/about')
def about():
    # return redirect('/userInfo')
    return render_template('about.html')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
