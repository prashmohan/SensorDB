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

class TraceFile(object):
    def __init__(self, location):
        self.loc = location
        self.initialize()
        
    def initialize(self):
        file_name = os.path.basename(self.loc)
        date_str = file_name[file_name.rfind('$') + 1 : file_name.rfind('H')]
        self.date = datetime.datetime(int(date_str[:4]), int(date_str[-2:]), 1)
        
    def get_date(self):
        return self.date

class Trace(object):
    def __init__(self, location):
        self.loc = location
        self.trace_files = []
        self.initialize()
    
    def initialize(self):
        for file_name in os.listdir(self.loc):
            if not file_name.endswith('H.DAT.csv'): # Ignore the 'M' files
                continue
            self.trace_files.append(TraceFile(os.path.join(self.loc, file_name)))
            
    def get_name(self):
        file_name = os.path.basename(location)
        if file_name.find('_') != -1:
            return file_name[ : file_name.rfind('_')]
        return file_name
        
    def get_length(self):
        """Returns the trace length in months"""
        dates = [trace.get_date() for trace in self.trace_files]
        return ((max(dates) - min(dates)) / 30).days
        
    def get_type(self):
        file_name = os.path.basename(location)
        return file_name[file_name.rfind('_') + 1 : ]
    
        
class SodaTrace(object):
    def __init__(self, directory):
        self.dir = directory
        self.traces = []
        self.initialize()
        
    def initialize(self):
        for obj_name in os.listdir(self.dir):
            self.traces.append(Trace(os.path.join(self.dir, obj_name)))

    def get_trace_types(self):
        return set([trace.get_type() for trace in self.traces])

    def get_traces(self, type):
        return [trace for trace in self.traces if trace.get_type() == type]
        
if __name__ == '__main__':
    pass
