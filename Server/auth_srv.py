import flask
import flask_login
from flask import Flask, jsonify
from flask import json
from flask import render_template
from flask import request
import multiprocessing
import data_processing
import pandas as pd
import editdistance

app = Flask(__name__)
users = {'Joe': {'pw': 'Kirkland'}}
training_auth_string = "the quick brown fox jumped over the lazy dog and ran all the way to wildhacks"

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
    
@app.route('/auth' , methods=['POST'])
def auth():
    recv_data = json.loads(request.data)
    auth_data = recv_data['data']
    test_auth_string = recv_data['string']
    print test_auth_string
    lev_dist = editdistance.eval(training_auth_string, test_auth_string)
    if lev_dist > round(len(training_auth_string) / 10):
        return "rejected"
    auth_df = data_processing.process_timestamp_data(
        auth_data, name=None, save_name=None, save_dir=None)
    if len(auth_df) == 0:
        return "rejected"
    training_df = pd.read_table('/Users/Aaron/Authentype_local/Aaron_2016-11-19_14-47-28_quickbrownfox/'
                                'Aaron_2016-11-19_14-47-28.txt')
    auth_score, _, _ = data_processing.find_ks_score(auth_df, training_df)
    print auth_score
    if auth_score < -0.7:
        return "approved"
    else:
        return "rejected"
    #render_template('index.html', registered=1)
    #received_json_data = json.loads(flask.request.)
    #pw = flask.request.form['pw']
    
@app.route('/reg' , methods=['POST'])
def reg():
    recv_data = json.loads(request.data)
    auth_data = recv_data['data']
    
    return 'many thanks!'

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
