import flask
from flask import Flask, jsonify, json, render_template, request, url_for
from celery import Celery
import data_processing
import pandas as pd
import editdistance
import subprocess
import sys

app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)

def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = make_celery(app)

users = {'Joe': {'pw': 'Kirkland'}}
training_auth_string = "the quick brown fox jumped over the lazy dog and ran all the way to wildhacks"


def println(text):
    sys.stderr.write(text + '\n')
    sys.stderr.flush()

@app.route('/hello' , methods=['POST'])
def hello():
    task = long_task.apply_async()
    return jsonify({}), 202, {'Location': url_for('taskstatus',
                                                  task_id=task.id)}

@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = long_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)

@celery.task
def long_task():
    usrname = flask.request.form['username']
    pw = flask.request.form['pw']
    if request.form['submit'] == 'login':
        if usrname in users.keys():
            if flask.request.form['pw'] == users[usrname]['pw']:
                subprocess.Popen('python {0} -a -u {usrname} -i {usrid} -s {srv}'.format(
                    '/Users/Aaron/git/Authentype/Acquisition/widgets.py',
                    usrid=usrname, usrname=usrname,
                    srv='"http://127.0.0.1:5000"'
                ), shell=True)
                return render_template('index.html', match=1)
        return render_template('index.html', no_match=1)
    elif request.form['submit'] == 'register':
        if usrname in users.keys():
            return render_template('index.html', user_taken=1)
        else:
            users[usrname] = {'pw': pw}
            subprocess.Popen('python {0} -r -u {usrname} -i {usrid} -s {srv}'.format(
                '/Users/Aaron/git/Authentype/Acquisition/widgets.py',
                usrid=usrname, usrname=usrname,
                srv='"http://127.0.0.1:5000"'
            ), shell=True)
            return render_template('index.html', registered=1)
    return "You should not be here. Sorry 'bout that"
    
@app.route('/auth' , methods=['POST'])
def auth():
    recv_data = json.loads(request.data)
    auth_data = recv_data['data']
    test_auth_string = recv_data['string']
    user_id = recv_data['user_id']
    println(test_auth_string)
    lev_dist = editdistance.eval(training_auth_string, test_auth_string)
    if lev_dist > round(len(training_auth_string) / 10):
        return "rejected"
    auth_df = data_processing.process_timestamp_data(
        auth_data, name=None, save_name=None, save_dir=None)
    if len(auth_df) == 0:
        return "rejected"
    training_df = pd.read_table('/Users/Aaron/Authentype_local/Server/{0}_store.txt'.format(user_id))
    println(training_df)
    auth_score, _, _ = data_processing.find_ks_score(auth_df, training_df)
    sys.stderr.write(auth_score + '\n')
    sys.stderr.flush()

    if auth_score < -0.5:
        return "approved"
    else:
        return "rejected"
    #render_template('index.html', registered=1)
    #received_json_data = json.loads(flask.request.)
    #pw = flask.request.form['pw']
    
@app.route('/reg' , methods=['POST'])
def reg():
    recv_data = json.loads(request.data)
    train_data = recv_data['data']
    user_id = recv_data['user_id']
    train_df = data_processing.process_timestamp_data(
        train_data, name=None, save_name=None, save_dir=None)
    train_df.to_csv('/Users/Aaron/Authentype_local/Server/{0}_store.txt'.format(user_id), index=False, sep='\t')
    return 'many thanks!'

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
