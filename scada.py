#!/usr/bin/env python
"""
Summary:

Author:  prashmohan@gmail.com
         http://www.cs.berkeley.edu/~prmohan
        
License: Licensed under the CRAPL non-license -
         http://matt.might.net/articles/crapl/CRAPL-LICENSE.txt
         
         This code is provided "as-is" and is available for
         modification. If you have any questions do mail
         me.  I will _try_ to get back to you as soon as possible.
"""

import sys
import os
import time
import datetime
import clustering
from pylab import *

class DataRecord(object):
    def __init__(self, date, timestamp, data):
        st = time.strptime(date.strip() + ' ' + timestamp.strip(), '%Y-%m-%d %H:%M:%S')
        self.ts = datetime.datetime(st.tm_year, st.tm_mon, st.tm_mday, \
                                        st.tm_hour, st.tm_min, st.tm_sec)
        try:
            self.data = float(data.strip())
        except:
            print 'Error', data, date, timestamp
            raise

    def __cmp__(self, other):
        if self.ts < other.ts:
            return -1
        elif self.ts == other.ts:
            return 0
        else:
            return 1

    def __repr__(self):
        return str(self.ts) + '\t' + self.data

    def __str__(self):
        return repr(self)

class DataCollection(object):
    def __init__(self, limit=None):
        self.records = []
        self.limit = limit

    def append(self, record):
        self.records.append(record)

    def get_data(self):
        if not self.limit:
            return [rec.data for rec in self.records]
        else:
            return [rec.data for rec in self.records[:self.limit]]

    def get_ts(self):
        if not self.limit:
            return [rec.ts for rec in self.records]
        else:
            return [rec.ts for rec in self.records[:self.limit]]
        
    def extend(self, col):
        self.records.extend(col.records)

    def sort(self):
        self.records.sort()
    
class TraceFile(object):
    def __init__(self, location):
        self.loc = location
        self.initialize()
        
    def initialize(self):
        file_name = os.path.basename(self.loc)
        date_str = file_name[file_name.rfind('$') + 1 : file_name.rfind('H')]
        self.date = datetime.datetime(int(date_str[:4]), int(date_str[-2:]), 1)
        self.data_cache = None
        
    def get_date(self):
        return self.date

    def get_data(self):
        data = DataCollection()
        for line in open(self.loc, 'r'):
            parts = line.split(',')
            data.append(DataRecord(parts[1], parts[2], parts[4]))
        return data

    def __repr__(self):
        return 'Trace type: ' + os.path.dirname(self.loc) + '\tTrace Date: ' + str(self.date)

    def __str__(self):
        return repr(self)    

class Name(object):
    def __init__(self, name):
        file_name = os.path.basename(name)
        self.name = file_name
        self.room_no = file_name[file_name.find('R') + 1 : file_name.find('_')]
        self.floor = self.room_no[0] if len(self.room_no) > 0 else 'None'
        self.type = file_name[file_name.rfind('_') + 1 : ]
        self.prefix = file_name[ : file_name.find('R')]
        
    def __repr__(self):
        return 'Prefix: ' + self.prefix + ', Type: ' + self.type + ', Room No: ' + self.room_no + ', Floor: '+ self.floor + ', Full Name: ' + self.name

    def __str__(self):
        return repr(self)         

class Trace(object):
    def __init__(self, location, limit=None):
        self.loc = location
        self.trace_files = []
        self.initialize()
        self.limit = limit
    
    def initialize(self):
        for file_name in os.listdir(self.loc):
            if not file_name.endswith('H.DAT.csv'): # Ignore the 'M' files
                continue
            self.trace_files.append(TraceFile(os.path.join(self.loc, file_name)))
            
    def __repr__(self):
        return repr(Name(self.loc))

    def get_name(self):
        return Name(self.loc)

    def __str__(self):
        return repr(self)
    
    def get_length(self):
        """Returns the trace length in months"""
        dates = [trace.get_date() for trace in self.trace_files]
        return ((max(dates) - min(dates)) / 30).days
        
    def get_type(self):
        file_name = os.path.basename(self.loc)
        type = file_name[file_name.rfind('_') + 1 : ]
        while len(type) > 0 and str.isdigit(type[0]):
            type = type[1:]
        return type        

    def get_data(self, start_time = None, end_time = None):
        data = DataCollection(self.limit)
        for trace in self.trace_files:
            if start_time and trace.get_date() < start_time:
                continue
            if end_time and trace.get_date() > end_time:
                continue
            data.extend(trace.get_data())
        data.sort()
        return data
            
class SodaTrace(object):
    def __init__(self, directory, limit=None):
        self.dir = directory
        self.traces = []
        self.limit = limit
        self.initialize()
        
    def initialize(self):
        for obj_name in os.listdir(self.dir):
            self.traces.append(Trace(os.path.join(self.dir, obj_name), self.limit))

    def get_trace_types(self):
        return set([trace.get_type() for trace in self.traces])

    def get_traces(self, type):
        return [trace for trace in self.traces if trace.get_type() == type]

    def get_trace(self, sensor_name):
        for trace in self.traces:
            if trace.get_name().name == sensor_name:
                return trace

    def get_sensor_names(self):
        return [trace.get_name() for trace in self.traces]

def get_datetime(year, month):
    return datetime(year, month, 1)

def clean_name(name):
    return name.replace('_', '')


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
    sensors = ['SODC1C1____SWT', 'SODC1C1__CDRWT', 'SODC1C2____SWT', 'SODC1C2__CDRWT', 'SODC1S_____SWT', 'SODC1S_____RWT', 'SODC1C1_____KW', 'SODC1C2_____KW', 'SODC2______SWT', 'SODC1C2____SWS']
    return [t for t in trace.traces if t.get_name().name in sensors]

    
if __name__ == '__main__':
    pass
