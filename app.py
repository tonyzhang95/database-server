from flask import Flask, render_template, request, json, redirect, session, url_for
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
mysql = MySQL()

app.secret_key = 'simple-server-database'

# MySQL config
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Supern0va'
app.config['MYSQL_DATABASE_DB'] = 'WDS'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


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

            if len(data) is 0:
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
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = 'SELECT * FROM WDS.user join WDS.customer on user.user_id=customer.user_id WHERE user_username = {}'.format('"' + str(session.get('user')) + '"')
        cursor.execute(sql)
        result = cursor.fetchall()
        if not result:
            cursor.execute('select * from wds.user where user_username = {}'.format('"' + str(session.get('user')) + '"'))
            result = cursor.fetchall()
        # conn.commit()
        cursor.close()
        conn.close()

        print(result)

        if len(result[0]) < 10:
            user_account = "Username: " + str(result[0][1]) + "\n" + "Accunt/Email: " + str(result[0][2])
        else:
            user_account = "Username: " + str(result[0][1]) + "\n" + "Accunt/Email: " + str(result[0][2]) + "\n" + "Fullname: " + str(result[0][5]) + str(result[0][6]) + "\n" + "Gender: " + str(result[0][7]) + "\n" + "Maritality: " + str(result[0][8]) + "\n" + "Insurance type: " + str(result[0][9]) + "\n"+ "Address: " + str(result[0][10]) + ", " + str(result[0][11]) + ", " + str(result[0][12]) + ", " + str(result[0][13]) + ", " + str(result[0][14])

        return render_template('userHome.html', user_info = user_account, user_insurance = 'car insurance 001')
    else:
        return render_template('error.html', error = 'Unauthorized Access')


"""
Process submitted user info form.
Pass in parameters with RESTful query POST request.
For example:
http://0.0.0.0:5000/processUserInfo?firstname=david&lastname=beckham&gender=M&maritality=S&instype=A&house=500&street=Man St&city=manchester&state=NY&zipcode=10003
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

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_insertCustomerInfo', (firstname,lastname,gender,maritality,instype,house,street,city,state,zipcode,username))
            conn.commit()
            cursor.close()
            conn.close()
            return "Successfully entered this record to the database."
        else:
            return "Error: must fill all fields."
    except Exception as e:
        print(str(e))
        return str(e)


# interface for user info edit
@app.route('/userInfo')
def userInfo():
    # if session.get('user'):
    return render_template('userinfo.html')
    # else:
    #     return render_template('error.html', error = 'You need to log-in to access this page.')


# display products and pricing
@app.route('/product')
def product():
    return render_template('product.html')


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
