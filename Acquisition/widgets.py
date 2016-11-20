import time
import pandas as pd
import numpy as np
import Tkinter as tk
import os
import errno
import sched
from multiprocessing import *
import httplib
import json
import requests

_repetitions = 5
_dialog_text = 'Type: "the quick brown fox jumped over the lazy dog and ran all the way to wildhacks" {0} times\n' \
               'press enter between each repetition\n'.format(_repetitions)


class DataHandler:
    def __init__(self):
        self.training_data = []
        self.training_instance = []

    def new_instance(self):
        self.training_data.append(self.training_instance)
        self.training_instance = []

    def add_data(self, data):
        self.training_instance.append(data)

    def add_data_to_instance(self, instance_index, data):
        self.training_data[instance_index].append(data)


class Counter:
    def __init__(self):
        self.count = 0

    def inc(self):
        self.count += 1

    def reset(self):
        self.count = 0


class RegistrationWindow:
    return_counter = Counter()
    training_data_handler = DataHandler()
    name = time.strftime("%Y-%m-%d_%H-%M-%S")
    save_name = name
    old_keys_still_down = set()
    keys_still_down = set()

    def __init__(self, user_id, user_name, save_dir=None):
        self.user_id = user_id
        self.user_name = user_name
        self.save_dir = save_dir

        self.root = tk.Tk()
        self.root.title("Authentype registration")

        self.frame = tk.Frame(self.root)
        self.frame.pack()

        self.text1 = tk.Text(self.frame, width=40, height=1)
        self.text1.pack(side=tk.TOP)
        self.text1.insert(tk.END, 'Authentype registration for ' + self.user_name)
        self.text1.tag_configure("center", justify='center')
        self.text1.tag_add("center", 1.0, "end")
        self.text1.config(state=tk.DISABLED)

        self.text = tk.Text(self.root, width=100, height=20)
        self.text.pack()
        self.text.insert(tk.END, _dialog_text)
        self.text.bind("<KeyPress>", self.key_down)
        self.text.bind("<KeyRelease>", self.key_up)
        self.text.bind('<Return>', self.return_press)

        self.text.focus_set()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def key_up(self, e):
        key = e.char
        if key == '\r' or key == '' or key == '\n' or key == '\t':
            return
        if key == '\x7f':
            key = 'del'
        print 'up', key
        if key in self.old_keys_still_down:
            self.training_data_handler.add_data_to_instance(
                len(self.training_data_handler.training_data)-1,
                dict(
                    key=key,
                    time=time.time(),
                    type='u'
                )
            )
            self.old_keys_still_down.discard(key)
        else:
            self.training_data_handler.add_data(dict(
                key=key,
                time=time.time(),
                type='u'
            ))
            self.keys_still_down.discard(key)

    def key_down(self, e):
        key = e.char
        if key == '\r' or key == '' or key == '\n' or key == '\t':
            return
        if key == '\x7f':
            key = 'del'
        self.keys_still_down.add(key)
        print 'down', key
        self.training_data_handler.add_data(dict(
            key=key,
            time=time.time(),
            type='d'
        ))

    def return_press(self, e):
        print 'return'
        self.training_data_handler.new_instance()
        self.old_keys_still_down = self.keys_still_down
        self.keys_still_down = set()
        self.return_counter.inc()
        if self.return_counter.count >= _repetitions:
            self.text.insert(tk.END, '\nRegistration completed!')
            self.text.configure(bg='#CCFFCC')
            self.text.config(state=tk.DISABLED)
            self.root.update()
            s = sched.scheduler(time.time, time.sleep)
            s.enter(1, 1, self.on_closing, ())
            s.run()
            print time.time()

    def on_closing(self):
        print 'close'
        self.training_data_handler.new_instance()
        process_timestamp_data(self.training_data_handler.training_data, name=self.name, save_name=self.save_name,
                               save_dir=self.save_dir)
        self.root.destroy()


class AuthenticationWindow:
    return_counter = Counter()
    training_data_handler = DataHandler()
    name = time.strftime("%Y-%m-%d_%H-%M-%S")
    save_name = name
    old_keys_still_down = set()
    keys_still_down = set()

    def __init__(self, user_id, user_name, server_path, save_dir=None):
        self.user_id = user_id
        self.user_name = user_name
        self.server_address = server_path
        self.save_dir = save_dir

        self.root = tk.Tk()
        print 'test'
        self.root.title("Authentype verification")

        self.frame = tk.Frame(self.root)
        self.frame.pack()

        self.text1 = tk.Text(self.frame, width=100, height=2)
        self.text1.pack(side=tk.TOP)
        self.text1.insert(tk.END, 'Authentypication for ' + self.user_name +
                          '\nType: "the quick brown fox jumped over the lazy dog and ran all the way to wildhacks"')
        self.text1.tag_configure("center", justify='center')
        self.text1.tag_add("center", 1.0, "end")
        self.text1.config(state=tk.DISABLED)

        self.text = tk.Text(self.root, width=80, height=5)
        self.text.pack(side=tk.BOTTOM)
        self.text.bind("<KeyPress>", self.key_down)
        self.text.bind("<KeyRelease>", self.key_up)
        self.text.bind('<Return>', self.return_press)

        self.text.focus_set()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def key_up(self, e):
        key = e.char
        if key == '\r' or key == '' or key == '\n' or key == '\t':
            return
        if key == '\x7f':
            key = 'del'
        print 'up', key
        if key in self.old_keys_still_down:
            self.training_data_handler.add_data_to_instance(
                len(self.training_data_handler.training_data) - 1,
                dict(
                    key=key,
                    time=time.time(),
                    type='u'
                )
            )
            self.old_keys_still_down.discard(key)
        else:
            self.training_data_handler.add_data(dict(
                key=key,
                time=time.time(),
                type='u'
            ))
            self.keys_still_down.discard(key)

    def key_down(self, e):
        key = e.char
        if key == '\r' or key == '' or key == '\n' or key == '\t':
            return
        if key == '\x7f':
            key = 'del'
        self.keys_still_down.add(key)
        print 'down', key
        self.training_data_handler.add_data(dict(
            key=key,
            time=time.time(),
            type='d'
        ))

    def return_press(self, e):
        print 'return'
        self.training_data_handler.new_instance()
        self.text.delete('1.0', tk.END)
        self.text.insert(tk.END, 'Sending data')
        self.send_and_check()
        self.training_data_handler = DataHandler()
        self.text.configure(bg='#CCFFCC')
        # self.text.config(state=tk.DISABLED)
        self.root.update()
        # s = sched.scheduler(time.time, time.sleep)
        # s.enter(1, 1, self.on_closing, ())
        # s.run()

    def send_and_check(self):
        print 'send'
        json_data = json.dumps(self.training_data_handler.training_data[-1])
        print json_data

        # connection = httplib.HTTPSConnection(self.serv_address)
        headers = {'Content-type': 'application/json'}
        # connection.request('POST', '/auth', json_data, headers)
        # response = connection.getresponse()
        # response.read()

        r = requests.post(self.server_address + '/auth', headers=headers, data=json_data)
        print r
        print r.text

    def on_closing(self):
        print 'close'
        self.training_data_handler.new_instance()
        process_timestamp_data(self.training_data_handler.training_data, name=self.name, save_name=self.save_name,
                               save_dir=self.save_dir)
        self.root.destroy()


def process_timestamp_data(data, name=None, save_name=None, save_dir='/Users/Aaron/Authentype_local/'):
    run_dfs = []
    for i, run in enumerate(data):
        print 'run', i
        if len(run) == 0:
            continue
        # print run
        run_df = pd.DataFrame(run)
        # print run_df
        run_df = run_df.sort_values(by=['key', 'time'])
        # print run_df
        for key in run_df['key'].drop_duplicates():  # drop trailing down events if they occur
            ix = len(run_df)-np.argmax((run_df['key'] == key).values[::-1])-1
            ix = (run_df['key'] == key).index[ix]
            if run_df.loc[ix, 'type'] == 'd':
                print 'drop', key, 'at', ix
                run_df = run_df.drop([ix], axis=0)
        run_df['ix'] = np.floor(np.arange(len(run_df))/2)*2
        # print run_df
        run_df = pd.pivot_table(run_df, index=['key', 'ix'], columns='type', values='time')
        run_df = run_df.sort_values(by='d')
        run_df['pp'] = run_df['d'].diff()
        run_df['ht'] = run_df['u'] - run_df['d']
        run_df['ft'] = run_df['pp'] - run_df['ht']
        run_df.reset_index(drop=False, inplace=True)
        run_df = run_df.drop('ix', 1)
        run_df['digraph'] = run_df['key'].shift(1).str.cat(run_df['key'], sep='-')
        run_df['trial'] = i
        # print run_df
        run_dfs.append(run_df)

    if len(run_dfs) == 0:
        return

    merged_run_dfs = run_dfs[0]
    if len(run_dfs) > 1:
        for df in run_dfs[1:]:
            merged_run_dfs = merged_run_dfs.append(df)
    merged_run_dfs['name'] = name
    print
    print "merged"
    print merged_run_dfs
    if save_name is not None and len(save_name) > 0:
        print 'save as:', save_name
        try:
            os.makedirs(os.path.join(save_dir, save_name))
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        merged_run_dfs.to_csv(os.path.join(save_dir, save_name, save_name + '.txt'),
                              index=False, sep='\t')

    return merged_run_dfs

if __name__ == "__main__":
    serv_address = "http://127.0.0.1:5000"

    aw = AuthenticationWindow(user_id='aaron', user_name='aaron', server_path=serv_address,
                              save_dir='/Users/Aaron/Authentype_local/')

    # aw = RegistrationWindow(user_id='aaron', user_name='aaron', save_dir='/Users/Aaron/Authentype_local/')
    # print training_data.training_data
    # process_timestamp_data(training_data.training_data, save_name=name)

    # import ast
    # process_timestamp_data(
    #     ast.literal_eval("[[]]"))
