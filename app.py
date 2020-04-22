from flask import Flask, render_template, request, json, redirect, session
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash

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
                session['user'] = data[0][1]
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
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate the received values
        if _name and _email and _password:

            # All Good, let's call MySQL
            print('------sign up info received')
            conn = mysql.connect()
            print('------connection established')
            cursor = conn.cursor()
            print('------cursor created')
            _hashed_password = generate_password_hash(_password)
            cursor.callproc('sp_createUser',(_name,_email,_hashed_password))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                print('------created user: ',_name,_email,_password)
                return json.dumps({'message':'User created successfully !'})
            else:
                return json.dumps({'error':str(data[0])})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/success')
def success():
    return render_template('success.html')


@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html',error = 'Unauthorized User')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


@app.route('/todos')
def todo():
    return render_template('todos.html')


@app.route('/about')
def about():
    return render_template('about.html')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
