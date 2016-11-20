import flask
from flask import Flask, jsonify
from flask import json
from flask import render_template
from flask import request
import multiprocessing


app = Flask(__name__)
users = {'Joe': {'pw': 'Kirkland'}}

@app.route('/hello' , methods=['POST'])
def hello():
    usrname = flask.request.form['username']
    pw = flask.request.form['pw']
    if request.form['submit'] == 'login':
        if usrname in users.keys():
            if flask.request.form['pw'] == users[usrname]['pw']:
                return render_template('index.html', match=1)
        return render_template('index.html', no_match=1)
    elif request.form['submit'] == 'register':
        if usrname in users.keys():
            return render_template('index.html', user_taken=1)
        else:
            users[usrname] = {'pw': pw}
            return render_template('index.html', registered=1)
    return "You should not be here. Sorry 'bout that"

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()

@app.route('/auth' , methods=['POST'])
def auth():
    return "Thanks Comrade!"
    #received_json_data = json.loads(flask.request.)
    #pw = flask.request.form['pw']