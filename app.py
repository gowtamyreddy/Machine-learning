import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pickle
from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__) #Initialize the flask App
#model = pickle.load(open('model.pkl', 'rb'))
dataset = pd.read_csv('spg.csv')
X = dataset.iloc[:, :-1]
y = dataset.iloc[:, -1]

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import VotingRegressor
from sklearn.neighbors import KNeighborsRegressor
r1 = LinearRegression()
r2 = RandomForestRegressor(n_estimators=10, random_state=1)
r3 = KNeighborsRegressor()

er = VotingRegressor([('lr', r1), ('rf', r2), ('r3', r3)])
#y=y.reshape(-1,1)
er.fit(X, y)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/logon')
def logon():
	return render_template('signup.html')

@app.route('/login')
def login():
	return render_template('signin.html')

@app.route("/signup")
def signup():

    username = request.args.get('user','')
    name = request.args.get('name','')
    email = request.args.get('email','')
    number = request.args.get('mobile','')
    password = request.args.get('password','')
    con = sqlite3.connect('signup.db')
    cur = con.cursor()
    cur.execute("insert into `info` (`user`,`email`, `password`,`mobile`,`name`) VALUES (?, ?, ?, ?, ?)",(username,email,password,number,name))
    con.commit()
    con.close()
    return render_template("signin.html")

@app.route("/signin")
def signin():

    mail1 = request.args.get('user','')
    password1 = request.args.get('password','')
    con = sqlite3.connect('signup.db')
    cur = con.cursor()
    cur.execute("select `user`, `password` from info where `user` = ? AND `password` = ?",(mail1,password1,))
    data = cur.fetchone()

    if data == None:
        return render_template("signin.html")    

    elif mail1 == 'admin' and password1 == 'admin':
        return render_template("index.html")

    elif mail1 == str(data[0]) and password1 == str(data[1]):
        return render_template("index.html")
    else:
        return render_template("signup.html")

@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/predict',methods=['POST'])
def predict():
    '''
    For rendering results on HTML GUI
    '''
    int_features = [float(x) for x in request.form.values()]
    final_features = [np.array(int_features)]
    prediction = er.predict(final_features)

    output = prediction

    return render_template('result.html', prediction_text=output[0])

@app.route('/api/', methods=['POST'])
def makecalc():
	data = request.get_json()
	prediction = np.array2string(er.predict(data))

	return jsonify(prediction)

@app.route('/notebook')
def notebook():
	return render_template('Notebook.html')

@app.route('/about')
def about():
	return render_template('about.html')

if __name__ == "__main__":
    app.run()