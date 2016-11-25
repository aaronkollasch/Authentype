import time
import pandas as pd
import numpy as np
import Tkinter as tk
import os
import errno

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


class AcquisitionWindow:
    return_counter = Counter()
    training_data_handler = DataHandler()
    name = time.strftime("%Y-%m-%d_%H-%M-%S")
    save_name = name
    old_keys_still_down = set()
    keys_still_down = set()

    def __init__(self):    
        self.root = tk.Tk()
        self.root.title("Authentype trainer")

        self.frame = tk.Frame(self.root)
        self.frame.pack()

        self.text1 = tk.Text(self.frame, width=25, height=1)
        self.text1.pack(side=tk.LEFT)
        self.text1.insert(tk.END, 'Please enter your name')
        self.text1.config(state=tk.DISABLED)

        self.text2 = tk.Entry(self.frame, width=15)
        self.text2.pack(side=tk.RIGHT)
        self.text2.bind('<Return>', self.set_name)

        self.text = tk.Text(self.root, width=100, height=20)
        self.text.pack(side=tk.BOTTOM)
        self.text.insert(tk.END, _dialog_text)
        self.text.bind("<KeyPress>", self.key_down)
        self.text.bind("<KeyRelease>", self.key_up)
        self.text.bind('<Return>', self.return_press)

        self.reset_button = tk.Button(self.root, command=self.reset, text='save and clear')
        self.reset_button.pack(side=tk.BOTTOM)

        self.text2.focus_set()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def set_name(self, e):
        self.update_name()
        self.text.focus_set()

    def update_name(self):
        self.name = self.text2.get()
        if len(self.name) == 0:
            self.name = time.strftime("%Y-%m-%d_%H-%M-%S")
            self.save_name = self.name
        else:
            self.save_name = self.name + "_" + time.strftime("%Y-%m-%d_%H-%M-%S")
        print 'set_name:', self.name

    def key_up(self, e):
        key = e.char
        if key == '\r' or key == '' or key == '\n' or key == '\t':
            return
        if key == '\x7f':
            key = 'del'
        # print 'up', key
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
        # print 'down', key
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
            self.text.insert(tk.END, '\nThanks! Press the save and clear button to finish or start again')
            self.text.config(state=tk.DISABLED)

    def on_closing(self):
        print 'close'
        self.training_data_handler.new_instance()
        self.update_name()
        process_timestamp_data(self.training_data_handler.training_data, name=self.name, save_name=self.save_name)
        # root.quit()
        self.root.destroy()

    def reset(self):
        self.update_name()
        process_timestamp_data(self.training_data_handler.training_data, name=self.name, save_name=self.save_name)
        print 'reset'
        self.training_data_handler = DataHandler()
        self.text.config(state=tk.NORMAL)
        self.text.delete('1.0', tk.END)
        self.text.insert(tk.END, _dialog_text)
        self.text2.delete(0, "end")
        self.root.update()
        self.text2.focus_set()
        self.return_counter.reset()

    # import curses
    # scr = curses.initscr()
    # curses.cbreak()
    # scr.keypad(1)
    #
    # scr.addstr(0, 0, "I love wildhacks")  # and the quick brown fox jumped over the lazy dog")
    # scr.addstr(1, 0, "Hit enter to finish")
    # scr.addstr(2, 0, "")
    # scr.refresh()
    #
    # key_data = []
    #
    # key = ''
    # cur_time = time.time()
    # while key != ord('\n'):
    #     key = scr.getch()
    #     # if key == curses.KEY_UP:
    #     #     print "up", chr(key)
    #     # elif key == curses.KEY_DOWN:
    #     #     print "down", chr(key)
    #     el_time = time.time() - cur_time  # round((time.time() - cur_time)*1000),
    #     cur_time = time.time()
    #     key_data.append(dict(
    #         # key=key,
    #         char=chr(key),
    #         el_time=el_time
    #     ))
    #     # scr.addch(20, 25, chr(key))
    #     # scr.refresh()
    #
    # curses.endwin()
    #
    # key_data = pd.DataFrame(key_data)
    # print key_data




def process_timestamp_data(data, name=None, save_name=None):
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
            os.makedirs('/Users/Aaron/Authentype_local/' + save_name + '/')
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        merged_run_dfs.to_csv('/Users/Aaron/Authentype_local/' + save_name + '/' + save_name + '.txt',
                              index=False, sep='\t')

    # import matplotlib.pyplot as plt
    # fig, ax = plt.subplots(figsize=(10, 5))
    # for df in run_dfs:
    #     df.plot(y='pp', ax=ax, legend=False)
    # fig.suptitle('press to press time')
    #
    # fig, ax = plt.subplots(figsize=(10, 5))
    # for df in run_dfs:
    #     df.plot(y='ht', ax=ax, legend=False)
    # fig.suptitle('hold time')
    # plt.show()

if __name__ == "__main__":
    aw = AcquisitionWindow()
    # print training_data.training_data
    # process_timestamp_data(training_data.training_data, save_name=name)

    # import ast
    # process_timestamp_data(
    #     ast.literal_eval("[[]]"))


