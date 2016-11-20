import scipy.stats as stats
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors
import numpy.ma as ma

print 'start'

alpha = 0.001
beta = 0
pp_vs_ht = 0.4


class MidPointNorm(matplotlib.colors.Normalize):
    def __init__(self, midpoint=0., midpoint_out=0.5, vmin=None, vmax=None, clip=False):
        matplotlib.colors.Normalize.__init__(self, vmin, vmax, clip)
        self.midpoint = midpoint
        self.midpoint_out = midpoint_out

    def __call__(self, value, clip=None):
        if clip is None:
            clip = self.clip

        result, is_scalar = self.process_value(value)

        self.autoscale_None(result)
        vmin, vmax, midpoint, midpoint_out = self.vmin, self.vmax, self.midpoint, self.midpoint_out

        if not (vmin < midpoint < vmax):
            raise ValueError("midpoint must be between maxvalue and minvalue.")
        elif vmin == vmax:
            result.fill(0)  # Or should it be all masked? Or 0.5?
        elif vmin > vmax:
            raise ValueError("maxvalue must be bigger than minvalue")
        else:
            vmin = float(vmin)
            vmax = float(vmax)
            if clip:
                mask = ma.getmask(result)
                result = ma.array(np.clip(result.filled(vmax), vmin, vmax),
                                  mask=mask)

            # ma division is very slow; we can take a shortcut
            res_dat = result.data

            # First scale to -1 to 1 range, than to from 0 to 1.
            res_dat -= midpoint
            res_dat[res_dat > 0] /= abs(vmax - midpoint) / (1-midpoint_out)
            res_dat[res_dat < 0] /= abs(vmin - midpoint) / midpoint_out

            # res_dat /= 2.
            res_dat += midpoint_out
            result = ma.array(res_dat, mask=result.mask, copy=False)

        if is_scalar:
            result = result[0]
        return result

    def inverse(self, value):
        if not self.scaled():
            raise ValueError("Not invertible until scaled")
        vmin, vmax, midpoint = self.vmin, self.vmax, self.midpoint

        if matplotlib.cbook.iterable(value):
            val = ma.asarray(value)
            val = 2 * (val-0.5)
            assert isinstance(val, ma.masked_array)
            val[val > 0] *= abs(vmax - midpoint)
            val[val < 0] *= abs(vmin - midpoint)
            val += midpoint
            return val
        else:
            val = 2 * (value - 0.5)
            if val < 0:
                return val*abs(vmin-midpoint) + midpoint
            else:
                return val*abs(vmax-midpoint) + midpoint


def find_ks_score(training, test):
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


if __name__ == '__main__':
    user_data = {
        'Aaron': '/Users/Aaron/Authentype_local/Aaron_2016-11-19_14-47-28_quickbrownfox/'
                 'Aaron_2016-11-19_14-47-28.txt',
        'Christie': '/Users/Aaron/Authentype_local/Christie_2016-11-19_16-04-15_quickbrownfox/'
                    'Christie_2016-11-19_16-04-15.txt',
        'Joe': '/Users/Aaron/Authentype_local/Joe_2016-11-19_16-13-03_quickbrownfox/'
               'Joe_2016-11-19_16-13-03.txt',
        'Omar': '/Users/Aaron/Authentype_local/Omar_2016-11-19_16-07-40_quickbrownfox/'
                'Omar_2016-11-19_16-07-40.txt',
        'Luke': '/Users/Aaron/Authentype_local/LUKE_2016-11-19_17-31-31_quickbrownfox/'
                'LUKE_2016-11-19_17-31-31.txt',
        'Tiffany': '/Users/Aaron/Authentype_local/Tiffany_2016-11-19_17-43-09_quickbrownfox/'
                   'Tiffany_2016-11-19_17-43-09.txt',
        'Leo': '/Users/Aaron/Authentype_local/Leo_2016-11-19_18-09-34_quickbrownfox/'
               'Leo_2016-11-19_18-09-34.txt',
        'Aimee': '/Users/Aaron/Authentype_local/Aimee Pierce_2016-11-19_18-36-44_quickbrownfox/'
               'Aimee Pierce_2016-11-19_18-36-44.txt',
        'garret': '/Users/Aaron/Authentype_local/garret_2016-11-19_18-41-45_quickbrownfox/'
               'garret_2016-11-19_18-41-45.txt'
    }

    # input = pd.read_table('/Users/Aaron/Authentype_local/Aaron_2016-11-19_14-47-28_quickbrownfox/'
    #                       'Aaron_2016-11-19_14-47-28.txt')
    # ix = 3
    # training = input[input['trial'] != ix]
    # test = input[input['trial'] == ix]
    # print training

    for key in user_data.keys():
        user_data[key] = pd.read_table(user_data[key])

    print 'loaded'

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
    plt.pcolormesh(out_arr, cmap='plasma_r', norm=MidPointNorm(midpoint=-0.7, midpoint_out=0.95), vmin=-0.85)
    # plt.pcolormesh(out_arr, cmap='jet_r')

    ax.set_yticks(np.arange(len(save_dict)) + 0.5, minor=False)
    ax.set_xticks(np.arange(len(save_dict[names[0]])) + 0.5, minor=False)

    ax.set_xticklabels(trials, minor=False)
    ax.set_yticklabels(names, minor=False)

    plt.xticks(rotation=90)

    plt.colorbar()

    ax.invert_yaxis()
    fig.tight_layout()
    plt.show()
