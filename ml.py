#!/usr/bin/env python
"""
Author:  prashmohan@gmail.com
         http://www.cs.berkeley.edu/~prmohan
        
Copyright (c) 2011, University of California at Berkeley
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

import sys
import os
import logging

def get_anomolies(start_limit, stop_limit, limit_percentile=0.95, dist_threshold=0.7):
    trace = SodaTrace('UCProject_UCB_SODAHALL', start_limit, stop_limit)
    if len(trace.traces[-1].get_data().get_data()) == 0:
        raise Exception("No more data")
    art4 = [art for art in trace.traces if art.get_name().name.endswith('ART') and art.get_name().name.find('R4') != -1 and art.get_name().name != 'SODA1R438__ART']
    multid_data, clust = clustering.hier_cluster(art4)
    percentile = sort(clust[:,2])
    percentile = percentile[int(len(percentile) * limit_percentile)]
    d = clustering.hier.dendrogram(clust,
                                   color_threshold = dist_threshold * percentile,
                                   no_plot=True)
    # c, l = clustering.kmeans_cluster(art4, 3)
    
    subplot(211)
    for art in art4:
        plot(clustering.get_clean(art.get_data().get_data()))

    xlim(0, stop_limit - start_limit)
        
    subplot(212)
    y_len = 1
    for color in set(d['color_list']):
        x_vals = array(d['leaves'])[find(array(d['color_list']) == color)]
        y_vals = [y_len] * len(x_vals)
        y_len += 1
        scatter(x_vals, y_vals, c=color)
    # scatter (range(len(l)), 1 + array(l))
    xlim(0, stop_limit - start_limit)
    ylim(0, y_len)
    # ylim(-1, len(c) + 1)
    
def euclidean_dist(pt1, pt2):
    total = 0
    for index in range(len(pt1)):
        total += (pt2[index] - pt1[index]) ** 2
    return math.sqrt(total) 

def plot_mean_anomoly(data, wnd_size=24):
    clf()
    subplot(411)
    title('Data')
    for x in data:
        plot(clustering.get_clean(x.get_data().get_data()))
    subplot(412)
    cdv, odv, an = mean_anomoly(data, wnd_size)
    scatter(an, [1] * len(an))
    xlim(0, len(data[0].get_data().get_data()))
    title('Anomolies')
    subplot(413)
    plot(cdv, label='Distance from Moving Window Mean')
    legend()
    subplot(414)
    plot(odv, label='Distance from Overall Mean')
    legend()

def mean_anomoly(data, wnd_size):
    overall_dist_vals = [0] * wnd_size
    cur_dist_vals = [0] * wnd_size
    anomolies = []
    cur_win = []
    cur_means = []
    multid_data = clustering.get_multid_data(data)
    total = array([0.0] * len(data))
    start_time = time.time()
    overall_mean = [average(clustering.get_clean(x.get_data().get_data())) for x in data]
    print 'Time to calculate overall average', time.time() - start_time

    for pt_index, cur_pt in enumerate(multid_data):
        mean_pt = total / wnd_size
        cur_means.append(mean_pt)
        dist = map(lambda pt: euclidean_dist(mean_pt, pt),
                   cur_win)
        sigma = std(dist)
        mean = average(dist)
        if len(cur_win) >= wnd_size:
            for index in range(len(total)):
                total[index] -= cur_win[0][index]
            del cur_win[0]
        for index in range(len(cur_pt)):
            total[index] += cur_pt[index]

        cur_win.append(cur_pt)
        # print 10 * '-'
        # print 'Current Pt', cur_pt
        # print 'Total', total
        # print 'Mean Pt', mean_pt
        # raw_input()
        if len(cur_win) < wnd_size:
            continue

        cur_pt_dist = euclidean_dist(mean_pt, cur_pt)
        cur_dist_vals.append(cur_pt_dist)
        overall_dist_vals.append(euclidean_dist(overall_mean, cur_pt))

        if cur_pt_dist < mean - 4 * sigma or \
                cur_pt_dist > mean + 4 * sigma:
            anomolies.append(pt_index)
    return cur_dist_vals, overall_dist_vals, anomolies

def write_data_to_file(data, data_file, field_file):
    f_fields = open(field_file, 'w')
    f_fields.write('\n'.join([d.get_name().name for d in data]))
    f_fields.close()
    
    f_data = open(data_file, 'w')
    data_data = clustering.get_multid_data(data)
    for entry in data_data:
        f_data.write('\t'.join([str(x[index]) for x in entry]) + '\n')
    f_data.close()

    # data_data = [get_data(d) for d in data]
    # x_vals, y_vals = clustering.interpolate(data_data, sampling_freq=3600)
    # out_data = [x_vals]
    # out_data.extend(y_vals)

    # for index in range(len(out_data[0])):
    #     found_nan = False
    #     for x in out_data:
    #         if isnan(x[index]):
    #             found_nan = True
    #             break
    #     if found_nan:
    #         continue
        
    #     f_data.write('\t'.join([str(x[index]) for x in out_data]) + '\n')
    # f_data.close()

def enum(data):
    for i, x in enumerate(data):
        print i, x.get_name().name

def get_chiler_traces(trace):
    temp_sensors = ['SODC1C1____SWT', 'SODC1C1__CDRWT', 'SODC1C2____SWT', 'SODC1C2__CDRWT', 'SODC1S_____SWT', 'SODC1S_____RWT', 'SODC2______SWT', 'SODC1C2____SWS']
    kw_sensors = ['SODC1C1_____KW', 'SODC1C2_____KW']
    return [t for t in trace.traces if t.get_name().name in temp_sensors], [t for t in trace.traces if t.get_name().name in kw_sensors]

    
def get_clean(data):
    return [x for x in data if not isnan(x)]
