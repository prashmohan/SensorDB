from pylab import *
from scipy.cluster.vq import vq, kmeans2
import scipy.spatial.distance as dist
import scipy.cluster.hierarchy as hier
import scipy.interpolate
from time import mktime

COLORS = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

def get_clean(data):
    return [x for x in data if not isnan(x)]

def cluster(data, buckets=5):
    new_data = array(get_clean(data))
    c, l = kmeans2(new_data, buckets, minit='random')
    x_indices = array(range(len(new_data)))
    ret_vals = []
    for index, color in enumerate(COLORS):
        if index >= buckets:
            break

        indices = find(l == index)
        ret_vals.append((x_indices[indices], new_data[indices],))
    return ret_vals

def plot_data(data, buckets=5):
    data_plot = cluster(data, buckets)
    for index, color in enumerate(COLORS):
        if index >= buckets:
            break
        print 'Plotting color', color
        plot(data_plot[index][0], data_plot[index][1], color=color, marker='o', linestyle='None')
    

def hier_cluster(data):
    new_data = get_clean(data)
    new_data = array([array([1, x]) for x in new_data])
    d = dist.pdist(new_data)
    return hier.linkage(d)


def interpolate(signals, sampling_freq=1):
    start_time = min(signals[0][0])
    stop_time = max(signals[0][0])
    interpols = []
    
    for signal in signals:
        start_time = max(start_time, min(signal[0]))
        stop_time = min(stop_time, max(signal[0]))

        interpols.append(scipy.interpolate.interp1d(signal[0], signal[1]))

    x_new = range(start_time, stop_time, sampling_freq)
    y_vals = []
    for interpolator in interpols:
        y_vals.append(interpolator(x_new))

    return x_new, y_vals

def conv_time(dt):
    return mktime(dt.timetuple())
