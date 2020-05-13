from flask import Flask, render_template, request, json, redirect, session, url_for, jsonify
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import html


app = Flask(__name__)
mysql = MySQL()

app.secret_key = 'simple-server-database'

# MySQL config
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '2020DB!!'
app.config['MYSQL_DATABASE_DB'] = 'WDS'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)
mysql.init_app(app)
print("-----Initializing App-----")

# could use this sanitize function to clean user input if not using stored procedures.
def sanitize(string):
    sanitized = str(string)
    bad_strings = [';','$','&&','../','<','>','"','%3E','\'','--','1,2','\x00','`','(',')','file://','input://']
    for bad_str in bad_strings:
        if bad_str in sanitized:
            sanitized = sanitized.replace(bad_str, '')
    return sanitized


@app.route('/')
def index():
    if session.get('user'):
        if session.get('user').split("@")[1].lower() == "wds.com":
            return redirect('/employeeHome')
        else:
            return redirect('/userHome')
    else:
        return render_template('index.html')


@app.route('/showSignIn')
def showSignIn():
    return render_template('signin.html')


@app.route('/validateLogIn', methods=['POST'])
def validateLogIn():
    try:
        # print(request.url)
        # print(request.form)

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
                session.permanent = True
                session['user'] = data[0][2] # log user into session
                if session.get('user').split("@")[1].lower() == "wds.com": # redirect user and employee to their home page
                    return redirect('/employeeHome')
                else:
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
        # print(request.url)
        # print(request.args)

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
        if session.get('user').split("@")[1].lower() == "wds.com":
            redirect('/')

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
            elif str(account[0][7])=="F":
                gender = "Female"
            else:
                gender = "Not to provide"

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
            for ins in auto_ins:
                insurances.append("Car insurance no." + str(ins[0]) + " from " + str(ins[1].date()) + " to " + str(ins[2].date()) + " for $" + str(ins[3]) + "/year for my " + str(ins[9]) + " " + str(ins[7]) + " " + str(ins[8]) + ", with primary driver: " + str(ins[11]) +" "+ str(ins[12]) + " with driver's lisence numbdered " + str(ins[13]) + " born on " + str(ins[14].date()))

        if home_ins:
            for ins in home_ins:
                insurances.append("Home insurances no.{} from {} to {} for ${}/year for my {} squared feet, ${} home, which is purchased/moved-in on {} .".format(str(ins[0]),str(ins[1].date()),str(ins[2].date()),str(ins[3]),str(ins[8]),str(ins[7]),str(ins[6].date())))

        return render_template('userHome.html', user_info = user_info, user_insurance = insurances)
    else:
        return render_template('error.html', error = 'Unauthorized Access')


@app.route('/employeeHome')
def employeeHome():
    if session.get('user'):
        if session.get('user').split("@")[-1].lower() == "wds.com": # only employee have access to employee page
            print("----employee home-----")
            return render_template('employeeHome.html')
        else:
            return redirect('/')
    else:
        return redirect('/')


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


        if start and end and premium and vin and make and model and year and ownership and firstname and lastname and lisence and birthdate: # check all fields filled

            # MySQL ops
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_insertCarIns', (start, end, premium, vin, make, model, year, ownership, firstname, lastname, lisence, birthdate, username))
            conn.commit()
            cursor.close()
            conn.close()

            car_ins = "You have successfully purchased a insurance for ${}/year for your {} {} {} with VIN {} starting {} and ending {}. The driver is {} {} with DL no.{} born on {}.".format(premium, year, make, model, vin, start, end, firstname, lastname, lisence, birthdate)

            return json.dumps({'response': "{}".format(car_ins)})
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

        if start and end and premium and date and value and area and home_type and fire and security and pool and basement: # check all fields filled

            # check dates

            # MySQL ops
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_insertHomeIns', (start, end, premium, date, value, area, home_type, fire, security, pool, basement, username))
            conn.commit()
            cursor.close()
            conn.close()

            home_ins = "You have successfully purchased an insurance of ${}/year for your ${}, {} square feet home starting {} and ending {}.".format(premium, value, area, start, end)

            return json.dumps({'response': "{}".format(home_ins)})
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
        invoice_number = request.form['invoice_number']
        pay_method = request.form['pay_method']
        amount = request.form['amount']

        payment = ["success", pay_method, amount]

        # SQL INSERT into payment table and UPDATE invoice table
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_insertPayment',(pay_method, amount, invoice_number))
        conn.commit()
        cursor.close()
        conn.close()

        return json.dumps({'response': payment})
    except Exception as e:
        return str(e)


@app.route('/showInvoice')
def showInvoice():
    if session.get('user'):

        # retrieve user invoices from DB
        cid = 0
        auto_ins = []
        home_ins = []

        conn = mysql.connect()
        cursor = conn.cursor()

        # fetch customer id info from mysql
        cursor.execute(
            'select cid from wds.customer c join wds.user u on c.user_id = u.user_id where user_username = {}'.format('"' + str(session.get('user')) + '"'))
        cid = str(cursor.fetchone()[0])
        print(cid)
        # fetch insurances number from mysql
        if cid:
            cursor.execute(
                'select i.insid from wds.insurance i join wds.auto_ins a on i.insid=a.insid where i.cid = {}'.format('"' + cid + '"'))
            auto_ins = cursor.fetchall()
            cursor.execute(
                'select i.insid from wds.insurance i join wds.home_ins h on i.insid=h.insid where i.cid = {}'.format('"' + cid + '"'))
            home_ins = cursor.fetchall()
            all_ins = auto_ins + home_ins

        # fetch invoice info from mysql
        if all_ins:
            invoice_info = []
            for ins in all_ins:
                insid = str(ins[0])
                cursor.execute(
                    'select * from wds.invoice where invoice.insid = {}'.format('"' + insid + '"'))
                i = cursor.fetchone()
                invoice_info.append(i)
            print("All info：", invoice_info)
        else:
            invoice_info = []
        cursor.close()
        conn.close()

        # display insurances info
        invoices = []
        for info in invoice_info:
            if info[4]>0:
                pflag = 0
            else:
                pflag = 1
            invoices.append({"number":info[0], "paid":pflag, "duedate":info[2], "amount":info[3], "outstanding":info[4]})

        print("invoices:", invoices)
        return render_template('invoice.html', invoices = invoices)
    else:
        return redirect(url_for('index'))

@app.route('/showPay')
def showPayment():
    if session.get('user'):

        conn = mysql.connect()
        cursor = conn.cursor()

        # fetch customer id info from mysql
        cursor.execute(
            'select cid from wds.customer c join wds.user u on c.user_id = u.user_id where user_username = {}'.format(
                '"' + str(session.get('user')) + '"'))
        cid = str(cursor.fetchone()[0])
        print(cid)
        # fetch payments details from mysql
        if cid:
            cursor.execute(
                'select n.invno from invoice n join insurance i on n.insid = i.insid where i.cid = {}'.format(
                    '"' + cid + '"'))
            invoices = cursor.fetchall()
        print(invoices)
        if invoices:
            payments = []
            for inv in invoices:
                invno = str(inv[0])
                cursor.execute(
                    'select * from payment where invno={}'.format('"' + invno + '"'))
                i = cursor.fetchall()
                payments.append(i)
            print("All info：", payments)
        else:
            payments = []
        cursor.close()
        conn.close()

        # display payments info
        showpay = []
        for pay_of_one_invoice in payments:
            for pay in pay_of_one_invoice:
                showpay.append(
                    {"number": pay[0], "date": pay[1], "method": pay[2], "amount": pay[3], "invno": pay[4]})

        print("showpay:", showpay)
        return render_template('showPay.html', showpay=showpay)
    else:
        return redirect(url_for('index'))

@app.route('/retrieveIns', methods=['POST'])
def retrieveIns():
    try:
        print('-------{}'.format(request.url))
        print('-------{}'.format(request.form))
        ins_number = request.form['ins_number']
        print("OK")

        conn = mysql.connect()
        cursor = conn.cursor()
        # fetch customer insurance info from mysql
        cursor.execute(
            'SELECT * FROM WDS.insurance a JOIN WDS.customer b ON a.cid=b.cid JOIN WDS.invoice n ON n.insid=a.insid WHERE a.insid="{}"'.format(str(ins_number)))
        ins = cursor.fetchall()[0]
        print(str(ins))

        number = str(ins[0])
        start = str(ins[1].date())
        end = str(ins[2].date())
        pre = str(ins[3])
        customer = str(ins[4])
        first = ins[6]
        last = ins[7]
        gender = ins[8]
        mari = ins[9]
        type = ins[10]
        house = str(ins[11])
        street = str(ins[12])
        city = str(ins[13])
        state = str(ins[14])
        zip = str(ins[15])
        invno = str(ins[17])
        invdate = str(ins[18].date())
        duedate = str(ins[19].date())
        amount = str(ins[20])
        outstanding = str(ins[21])

        insre = "Insurance number {}, starts on {}, ends on {}, preminum ${}, for customer id {}: {} {}, gender: {}, maritual: {}, " \
                "address: {} {}, {}, {}, {}.  Corresponding invoice number {}, issued on {}, due on {}, total amount ${}, outstanding ${}"\
            .format(number, start, end, pre, customer, first, last, gender, mari, house, street, city, state, zip,
                    invno, invdate, duedate, amount, outstanding)

        cursor.close()
        conn.close()

        return json.dumps({'response':insre, 'ins_number':ins[0]})

    except Exception as e:
        #return "Please enter a valid insurance number! "
        return e


@app.route('/deleteIns', methods=['POST'])
def deleteIns():
    if not session.get('user'):
        return render_template('error.html', error = 'Unauthorized Access')
    if session.get('user').split("@")[-1].lower() != "wds.com":
        return render_template('error.html', error = 'Unauthorized Access')
    try:
        ins_number = int(request.form['delete_number'])

        # SQL delete insurance, auto_ins/home_ins, invoice and payment
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_deleteInsurance',(ins_number,))
        conn.commit()
        cursor.close()
        conn.close()

        return json.dumps({'response': "Deleted insurance {}".format(ins_number) })
    except Exception as e:
        return "Please enter a valid insurance number! "


@app.route('/editIns')
def editIns():
    if not session.get('user'):
        return render_template('error.html', error = 'Unauthorized Access')
    if session.get('user').split("@")[-1].lower() != "wds.com":
        return render_template('error.html', error = 'Unauthorized Access')
    try:
        return render_template('editIns.html')
    except Exception as e:
        return redirect('/')


@app.route('/processEdit', methods=['POST'])
def processEdit():
    try:
        print(request.url)
        print(request.form)

        number = request.form['ins_num']
        start = request.form['insStartDate']
        end = request.form['insEndDate']
        premium = request.form['ins_premium']

        res = ", ".join([number, start, end, premium])
        print(res)

        # SQL update insurance and invoice tables
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_editInsurance',(number, start, end, premium))
        conn.commit()
        cursor.close()
        conn.close()


        return res
    except Exception as e:
        return str(e)



# log out current user
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')



# documentation page for this project
@app.route('/about')
def about():
    # return redirect('/userInfo')
    return render_template('about.html')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
