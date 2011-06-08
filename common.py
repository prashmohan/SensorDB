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

import sys
import os
import time
import datetime
import logging
import types
import string

log = logging.getLogger(__name__)

class DataRecord(object):
    """Python representation for each individual record in the Trace"""
    
    def __init__(self, data, date, timestamp=None):
        if timestamp:
            st = time.strptime(date.strip() + ' ' + timestamp.strip(), '%Y-%m-%d %H:%M:%S')
            self.ts = datetime.datetime(st.tm_year, st.tm_mon, st.tm_mday, \
                                        st.tm_hour, st.tm_min, st.tm_sec)
        else:
            self.ts = datetime.datetime.fromtimestamp(date)
            
        self.data = float(data.strip())

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
    """Python representation of a set of records. Typically a trace
    file or a part of a trace"""
    
    def __init__(self, start_limit=None, stop_limit=None):
        """start_limit and stop_limit are optional arguments that
        describe the subsection of the trace to operate on."""
        self.records = []
        self.start_limit = start_limit
        self.stop_limit = stop_limit
        self.sorted = True

    def append(self, record):
        """Add a record or a list of records to the collection"""
        if type(record) == types.ListType:
            self.__extend(record)
        elif type(record) == type(self):
            self.__extend(record.records)
        else:
            self.records.append(record)
        self.sorted = False

    def get_data_tuples(self, start_limit=None, stop_limit=None):
        """Retrieve data and timestamps from the data collection.

        start_limit and stop_limit are optional arguments that
        describe the subsection of the trace to operate on. If these
        options are not provided, then any arguments provided on
        object intialization will be used."""

        start_index, stop_index = self.__get_start_stop_indexes(start_limit, stop_limit)
        return np.array([rec.ts for rec in self.records[start_index : stop_index]]), \
            np.array([rec.data for rec in self.records[start_index : stop_index]])
            

    def get_data(self, start_limit=None, stop_limit=None):
        """Retrieve data from the data collection.

        start_limit and stop_limit are optional arguments that
        describe the subsection of the trace to operate on. If these
        options are not provided, then any arguments provided on
        object intialization will be used."""

        start_index, stop_index = self.__get_start_stop_indexes(start_limit, stop_limit)
        return np.array([rec.data for rec in self.records[start_index : stop_index]])

    def get_ts(self, start_limit=None, stop_limit=None):
        """Retrieve timestamps from the data collection.

        start_limit and stop_limit are optional arguments that
        describe the subsection of the trace to operate on. If these
        options are not provided, then any arguments provided on
        object intialization will be used."""
        
        start_index, stop_index = self.__get_start_stop_indexes(start_limit, stop_limit)
        return np.array([rec.ts for rec in self.records[start_index : stop_index]])

    def get_length(self):
        """Returns the length of the trace as a timedelta object"""
        self.__sort()
        if not self.records:
            return 0
        return self.records.ts[-1] - self.records.ts[0]
        
    def __get_start_stop_indexes(self, start_limit, stop_limit):
        self.__sort()
        if not start_limit:
            start_limit = self.start_limit
        if not stop_limit:
            stop_limit = self.stop_limit

        start_index = 0
        stop_index = len(self.records)
        for index, record in enumerate(self.records):
            if start_limit and record.ts < start_limit:
                start_index = index
            if stop_limit and record.ts < stop_limit:
                stop_limit = index

        return start_index, stop_index                
        
    def __extend(self, records):
        self.records.extend(records)

    def __sort(self):
        if not self.sorted:
            self.records.sort()
        self.sorted = True


class Name(object):
    def __init__(self, name):
        self.name = name
        self.room_no = self.name[self.name.find('R') + 1 :
                                     self.name.find('_')]
        self.floor = self.room_no[0] if len(self.room_no) > 0 else 'None'
        index = 1
        start_index = self.name.rfind('_')
        
        if len(self.name) - start_index == 2:
            # This is to handle the S_S and L_L names
            start_index = self.name[ : start_index].rfind('_')

        while self.name[start_index + index] in string.digits:
            # This is to remove any numbers that occur before the sensor type
            index += 1
        self.type = self.name[start_index + index : ]
        self.prefix = self.name[ : self.name.find('R')]
        
    def __repr__(self):
        return 'Prefix: ' + self.prefix + ', Type: ' + self.type + ', Room No: ' + self.room_no + ', Floor: '+ self.floor + ', Full Name: ' + self.name

    def __str__(self):
        return repr(self)
