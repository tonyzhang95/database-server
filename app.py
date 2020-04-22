from flask import Flask, render_template, request, json
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showLogIn')
def showLogIn():
    return render_template('login.html')


@app.route('/LogIn')
def logIn():
    return 'Log in'


@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')


@app.route('/signUp',methods=['POST'])
def signUp():

    # read the posted values from the UI
    _name = request.form['inputName']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']

    # validate the received values
    if _name and _email and _password:
        return json.dumps({'html':'<span>All fields good !!</span>'})
    else:
        return json.dumps({'html':'<span>Enter the required fields</span>'})


@app.route('/todos')
def todo():
    return render_template('todos.html')


@app.route('/about')
def about():
    return render_template('about.html')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000')
