import scipy.stats as stats
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

print 'start'

alpha = 0.001

def find_ks_score(training, test):
    intersect_digraphs = set(training['digraph']).intersection(set(test['digraph']))
    intersect_digraphs.discard(np.nan)
    intersect_digraphs = sorted(intersect_digraphs)
    # print intersect_digraphs

    ds = []
    for digraph in intersect_digraphs:
        data1 = training.loc[training['digraph'] == digraph, 'pp']
        data2 = test.loc[test['digraph'] == digraph, 'pp']
        D, _ = stats.ks_2samp(data1=data1, data2=data2)
        if D < alpha:
            D = alpha
        ds.append(D)

    ds = np.array(ds)
    ds_prod = ds.prod()
    # print 'ds_prod=', ds_prod

    score_pp = np.log(ds_prod)/len(intersect_digraphs)
    # print 'score_pp=', score_pp


    intersect_key = set(training['key']).intersection(set(test['key']))
    intersect_key.discard(np.nan)
    intersect_key = sorted(intersect_key)
    # print intersect_key

    ds = []
    for key in intersect_key:
        data1 = training.loc[training['key'] == key, 'ht']
        data2 = test.loc[test['key'] == key, 'ht']
        D, _ = stats.ks_2samp(data1=data1, data2=data2)
        if D < alpha:
            D = alpha
        ds.append(D)

    ds = np.array(ds)
    ds_prod = ds.prod()
    # print 'ds_prod=', ds_prod

    score_ht = np.log(ds_prod)/len(intersect_digraphs)
    # print 'score_ht=', score_ht

    score_combined = score_pp + score_ht
    # print 'score_combined=', score_combined

    return score_combined, score_pp, score_ht


if __name__ == '__main__':
    user_data = {
        'Aaron': '/Users/Aaron/Authentype_local/Aaron_2016-11-19_14-47-28_quickbrownfox/'
                 'Aaron_2016-11-19_14-47-28.txt',
        'Christie': '/Users/Aaron/Authentype_local/Christie_2016-11-19_16-04-15_quickbrownfox/'
                    'Christie_2016-11-19_16-04-15.txt',
        'Joe': '/Users/Aaron/Authentype_local/Joe_2016-11-19_16-13-03_quickbrownfox/'
               'Joe_2016-11-19_16-13-03.txt',
        'Omar': '/Users/Aaron/Authentype_local/Omar_2016-11-19_16-07-40_quickbrownfox/'
                'Omar_2016-11-19_16-07-40.txt'
    }

    # input = pd.read_table('/Users/Aaron/Authentype_local/Aaron_2016-11-19_14-47-28_quickbrownfox/'
    #                       'Aaron_2016-11-19_14-47-28.txt')
    # ix = 3
    # training = input[input['trial'] != ix]
    # test = input[input['trial'] == ix]
    # print training

    for key in user_data.keys():
        user_data[key] = pd.read_table(user_data[key])

    save_dict = {}

    for i_key, i_item in user_data.items():  # for each subject
        assert isinstance(i_item, pd.DataFrame)
        save_dict[i_key] = {}
        for j_key, j_item in user_data.items():
            assert isinstance(j_item, pd.DataFrame)
            for trial in sorted(set(j_item['trial'])):
                test_data = j_item[j_item['trial'] == trial]
                if i_key == j_key:
                    training_data = i_item[i_item['trial'] != trial]
                else:
                    training_data = i_item
                score_combined, score_pp, score_ht = find_ks_score(training=training_data, test=test_data)
                save_dict[i_key][j_key + repr(trial)] = score_combined

    print save_dict

    out_arr = np.zeros(shape=(len(save_dict), len(save_dict[save_dict.keys()[0]])))
    for i, name in enumerate(sorted(save_dict.keys())):
        for j, trial in enumerate(sorted(save_dict[name].keys())):
            out_arr[i, j] = save_dict[name][trial]

    print out_arr

    names = sorted(save_dict.keys())
    trials = sorted(save_dict['Joe'].keys())

    fig, ax = plt.subplots()
    plt.pcolormesh(out_arr)

    ax.set_yticks(np.arange(len(save_dict)) + 0.5, minor=False)
    ax.set_xticks(np.arange(len(save_dict[names[0]])) + 0.5, minor=False)

    ax.set_xticklabels(trials, minor=False)
    ax.set_yticklabels(names, minor=False)

    plt.xticks(rotation=90)

    plt.colorbar()

    ax.invert_yaxis()
    fig.tight_layout()
    plt.show()
