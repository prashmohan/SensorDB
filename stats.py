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

import types
import datetime
from collections import defaultdict
import numpy as np

def conv_epoch_to_datetime(timestamps):
    """Convert a list of UNIX timestamps, i.e. the number of seconds
    from epoch into a datetime object"""
    return [datetime.datetime.fromtimestamp(ts) for ts in timestamps \
                if type(ts) != datetime.datetime]

def get_distrib(timestamps, data, key_gen):
    """Generic function to aggregate distribution of values"""
    if timestamps and np.iterable(timestamps) and \
            type(timestamps[0]) == types.IntType:
        timestamps = conv_epoch_to_datetime(timestamps)
    vals = defaultdict(list)
    avg_vals = defaultdict(float)
    sd_vals = defaultdict(float)
    trapz_vals = defaultdict(float)
    count = defaultdict(int)
    
    for ts, data_val in zip(timestamps, data):
        vals[key_gen(ts)].append(data_val)
        count[key_gen(ts)] += 1

    for key in count:
        avg_vals[key] = np.sum(vals[key]) / count[key]
        sd_vals[key] = np.std(vals[key])
        trapz_vals[key] = np.trapz(vals[key]) / count[key] # Not returned as of now

    return avg_vals, sd_vals
    
def get_monthly_distrib(timestamps, data):
    """Return the average value of data for each month of the year"""
    return get_distrib(timestamps, data, lambda ts: ts.month)

def get_hourly_distrib(timestamps, data):
    """Return the average value of data for each hour of the day"""
    return get_distrib(timestamps, data, lambda ts: ts.hour)

def get_yearly_distrib(timestamps, data):
    """Return the average value of data for each year"""
    return get_distrib(timestamps, data, lambda ts: ts.year)

def get_weekly_distrib(timestamps, data):
    """Return the average value of data for each week of the year"""
    return get_distrib(timestamps, data, lambda ts: ts.isocalendar()[1])

def get_daily_distrib(timestamps, data):
    """Return the average value of data for each day of the year"""
    return get_distrib(timestamps, data, lambda ts: ts.timetuple()[7])

def get_diurnal_distrib(timestamps, data):
    """Return the average value of data for day and night"""
    return get_distrib(timestamps, data, lambda ts: 'nighttime' if ts.hour > 18 or ts.hour < 6 else 'daytime')

