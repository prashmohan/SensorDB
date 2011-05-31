#!/usr/bin/env python
"""
Author:  prashmohan@gmail.com
         http://www.cs.berkeley.edu/~prmohan
        
Copyright (c) 2011, Prashanth Mohan
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of University of California, Berkeley nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL PRASHANTH MOHAN BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from pylab import *
from scipy.cluster.vq import vq, kmeans2, whiten
import scipy.spatial.distance as dist
import scipy.cluster.hierarchy as hier
import scipy.interpolate
from time import mktime
import fastcluster
import types

COLORS = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

def get_clean(data):
    return [x for x in data if not isnan(x)]

def kmeans_cluster(data, buckets=5):
    if type(data) != types.ListType and type(data) != type(array([])):
        new_data = array(get_clean(data))
    else:
        new_data = get_multid_data(data)
    new_data = whiten(new_data)
    c, l = kmeans2(new_data, buckets, minit='random')
    # x_indices = array(range(len(new_data)))
    # ret_vals = []
    # for index, color in enumerate(COLORS):
    #     if index >= buckets:
    #         break

    #     indices = find(l == index)
    #     ret_vals.append((x_indices[indices], new_data[indices],))
    return c, l

def plot_data(data, buckets=5):
    data_plot = cluster(data, buckets)
    for index, color in enumerate(COLORS):
        if index >= buckets:
            break
        print 'Plotting color', color
        plot(data_plot[index][0], data_plot[index][1], \
                 color=color, marker='o', linestyle='None')

def get_data(data, normalize=True):
    ts = array(map(conv_time, data.get_data().get_ts()))
    if normalize:
        return ts - min(ts), data.get_data().get_data()
    else:
        return ts, data.get_data().get_data()

def get_multid_data(data):
    data_data = [get_data(d) for d in data]
    x_vals, y_vals = interpolate(data_data, sampling_freq=3600)
    out_data = y_vals
    ret_data = []

    for index in range(len(out_data[0])):
        found_nan = False
        for x in out_data:
            if isnan(x[index]):
                found_nan = True
                break
        if found_nan:
            continue
        ret_data.append([x[index] for x in out_data])
    return ret_data

def hier_cluster(data):
    if type(data) != types.ListType and type(data) != type(array([])):
        trans_data = get_clean(data)
        trans_data = array([array([1, x]) for x in new_data])
    else:
        trans_data = get_multid_data(data)
    d = dist.pdist(trans_data)
    return fastcluster.linkage(d, method='centroid')

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
