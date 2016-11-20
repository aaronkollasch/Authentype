import time
import pandas as pd
import numpy as np
import Tkinter as tk
import os
import errno
import scipy.stats as stats

alpha = 0.001
beta = 0
pp_vs_ht = 0.4

def process_timestamp_data(data, name=None, save_name=None, save_dir='/Users/Aaron/Authentype_local/'):
    run_dfs = []
    for i, run in enumerate(data):
        print 'run', i
        if len(run) == 0:
            continue
        print run
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
        if len(run_df) == 0:
            continue
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
    # print
    # print "merged"
    # print merged_run_dfs
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
    

def find_ks_score(test, training):
    intersect_digraphs = set(training['digraph']).intersection(set(test['digraph']))
    intersect_digraphs.discard(np.nan)
    intersect_digraphs = sorted(intersect_digraphs)
    num_digraphs = len(intersect_digraphs)
    # print intersect_digraphs

    ds = []
    for digraph in intersect_digraphs:
        data1 = training.loc[training['digraph'] == digraph, 'pp']
        data2 = test.loc[test['digraph'] == digraph, 'pp']
        if len(data1) < beta or len(data2) < beta:
            num_digraphs -= 1
            continue
        D, _ = stats.ks_2samp(data1=data1, data2=data2)
        if D < alpha:
            D = alpha
        ds.append(D)

    ds = np.array(ds)
    ds_prod = ds.prod()
    # print 'ds_prod=', ds_prod

    score_pp = np.log(ds_prod)/num_digraphs
    # print 'score_pp=', score_pp

    intersect_key = set(training['key']).intersection(set(test['key']))
    intersect_key.discard(np.nan)
    intersect_key = sorted(intersect_key)
    num_keys = len(intersect_key)
    # print intersect_key

    ds = []
    for key in intersect_key:
        data1 = training.loc[training['key'] == key, 'ht']
        data2 = test.loc[test['key'] == key, 'ht']
        if len(data1) < beta or len(data2) < beta:
            num_keys -= 1
            continue
        D, _ = stats.ks_2samp(data1=data1, data2=data2)
        if D < alpha:
            D = alpha
        ds.append(D)

    ds = np.array(ds)
    ds_prod = ds.prod()
    # print 'ds_prod=', ds_prod

    score_ht = np.log(ds_prod)/num_keys
    # print 'score_ht=', score_ht

    score_combined = pp_vs_ht * score_pp + score_ht
    # print 'score_combined=', score_combined

    return score_combined, score_pp, score_ht
    
