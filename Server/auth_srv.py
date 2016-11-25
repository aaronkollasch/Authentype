import flask
from flask import Flask, jsonify, json, render_template, request, url_for
from celery import Celery
import data_processing
import pandas as pd
import editdistance
import subprocess
import sys

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# def make_celery(app):
#     celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
#                     broker=app.config['CELERY_BROKER_URL'])
#     celery.conf.update(app.config)
#     TaskBase = celery.Task
#     class ContextTask(TaskBase):
#         abstract = True
#         def __call__(self, *args, **kwargs):
#             with app.app_context():
#                 return TaskBase.__call__(self, *args, **kwargs)
#     celery.Task = ContextTask
#     return celery
#
# celery = make_celery(app)

users = {'Joe': {'pw': 'Kirkland'}}
training_auth_string = "the quick brown fox jumped over the lazy dog and ran all the way to wildhacks"


def println(text):
    pass
    # sys.stderr.write(text)
    # sys.stderr.write('\n')
    # sys.stderr.flush()


@app.route('/hello', methods=['POST'])
def hello():
    usrname = flask.request.form['username']
    pw = flask.request.form['pw']
    submit = flask.request.form['submit']
    task = long_task.apply_async(args=(usrname, pw, submit))
    # println(url_for('taskstatus', task_id=task.id))
    return render_template('index.html'), 202, {'Location':  url_for('taskstatus', task_id=task.id)}  # '/status/{0}'.format(task.id)}  #


@app.route('/status/<task_id>')
def taskstatus(task_id):
    println('test1')
    task = long_task.AsyncResult(task_id)
    println('test2')
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        println(task.state)
        response = {
            'state': task.state,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


@celery.task(bind=False)
def long_task(usr_name, password, submit_type):
    println('start')
    if submit_type == 'login':
        if usr_name in users.keys():
            if password == users[usr_name]['pw']:
                subprocess.Popen('python {0} -a -u {usrname} -i {usrid} -s {srv}'.format(
                    '/Users/Aaron/git/Authentype/Acquisition/widgets.py',
                    usrid=usr_name, usrname=usr_name,
                    srv='"http://127.0.0.1:5000"'
                ), shell=True)
                return 'login'  # render_template('index.html', match=1)
        return 'incorrect login'  # render_template('index.html', no_match=1)
    elif submit_type == 'register':
        if usr_name in users.keys():
            return 'taken warning'  # render_template('index.html', user_taken=1)
        else:
            users[usr_name] = {'pw': password}
            subprocess.Popen('python {0} -r -u {usrname} -i {usrid} -s {srv}'.format(
                '/Users/Aaron/git/Authentype/Acquisition/widgets.py',
                usrid=usr_name, usrname=usr_name,
                srv='"http://127.0.0.1:5000"'
            ), shell=True)
            return 'registered'  # render_template('index.html', registered=1)
    return "You should not be here. Sorry 'bout that"

    
@app.route('/auth', methods=['POST'])
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
    # sys.stderr.write(auth_score + '\n')
    # sys.stderr.flush()

    if auth_score < -0.5:
        return "approved"
    else:
        return "rejected"
    #render_template('index.html', registered=1)
    #received_json_data = json.loads(flask.request.)
    #pw = flask.request.form['pw']


@app.route('/reg', methods=['POST'])
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
