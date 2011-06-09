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
import time
import re
import datetime
import collections
from common import DataRecord, DataCollection, Name
import httplib
import logging
import logging.handlers
import numpy as np

# Log verbosely
root_logger = logging.getLogger('')
root_logger.setLevel(logging.DEBUG)

# Logger console output
# console = logging.StreamHandler(sys.stderr)
# console_format = '%(message)s'
# console.setFormatter(logging.Formatter(console_format))
# console.setLevel(logging.INFO)
# root_logger.addHandler(console)

# Traceback handlers
traceback_log = logging.getLogger('traceback')
traceback_log.propogate = False
traceback_log.setLevel(logging.ERROR)

if __name__ == '__main__':
    # Logger file output
    file_handler = logging.handlers.RotatingFileHandler(sys.argv[0] + '.log', )
    file_format = '%(asctime)s %(levelname)6s %(name)s %(message)s'
    file_handler.setFormatter(logging.Formatter(file_format))
    file_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    traceback_log.addHandler(file_handler)


def handle_errors(exc_type, exc_value, traceback):
    logging.getLogger(__name__).error(exc_value)
    logging.getLogger('traceback').error(
        exc_value,
        exc_info=(exc_type, exc_value, traceback),
        )
sys.excepthook = handle_errors

log = logging.getLogger(__name__)


class SCADAException(Exception):
    pass


class TSDBException(SCADAException):
    pass


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
            data.append(DataRecord(parts[4], parts[1], parts[2]))
        return data

    def __repr__(self):
        return 'Trace type: ' + os.path.dirname(self.loc) + \
            '\tTrace Date: ' + str(self.date)

    def __str__(self):
        return repr(self)    


class SensorTrace(object):
    def __init__(self, sensor_name, start_limit=None, stop_limit=None):
        self.name = sensor_name
        self.trace_data = DataCollection(start_limit, stop_limit)
        self.start_limit = start_limit
        self.stop_limit = stop_limit
        self.initialize()

    def initialize(self):
        pass

    def __repr__(self):
        return repr(Name(self.name))

    def get_name(self):
        return Name(self.name)

    def get_type(self):
        return self.get_name().type

    def __str__(self):
        return repr(self)

    def get_length(self):
        """Returns the length of the trace as a timedelta object"""
        return self.trace_data.get_length()

    def get_data_tuples(self, start_limit=None, stop_limit=None):
        """Retrieve data and timestamps from the data collection.

        start_limit and stop_limit are optional arguments that
        describe the subsection of the trace to operate on. If these
        options are not provided, then any arguments provided on
        object intialization will be used."""
        start_limit, stop_limit = self.get_limits(start_limit, stop_limit)
        data = self.load_data(start_limit, stop_limit)
        self.trace_data = DataCollection(start_limit, stop_limit)
        self.trace_data.append(data)
        return self.trace_data.get_data_tuples(start_limit, stop_limit)

    def get_data_collection(self):
        return self.trace_data

    def load_data(self, start_limit=None, stop_limit=None):
        log.warn('Empty load data is called. This should typically not happen')
        pass

    def is_room(self) :
        return re.match('^SODA\dR.*_+(ASO|ART|ARS|AGN|VAV|RVAV)$', self.get_name().name)

    def is_in_room(self, room) :
        target = '^SODA\dR' + room + '_+(ASO|ART|ARS|AGN|VAV|RVAV)$'
        return re.match(target, self.get_name().name)

    def get_summary(self):
        self.get_data_tuples()
        vals = [data for data in self.trace_data.get_data() if data > 0]
        if vals:
            return {'min': np.amin(vals), 'ave': np.mean(vals), 'max': np.amax(vals)}
        else:
            return {'min': np.nan, 'ave': np.nan, 'max': np.nan}

    def get_limits(self, start_limit, stop_limit):
        if not start_limit:
            start_limit = self.start_limit
        if not start_limit:
            start_limit = datetime.datetime(2008, 11, 01)
        if not stop_limit:
            stop_limit = self.stop_limit
        return start_limit, stop_limit


class TSDBTrace(SensorTrace):
    TIME_FORMAT = '%Y/%m/%d-%H:%M:%S'
    
    def __init__(self, loc, sensor_name, start_limit=None, stop_limit=None):
        self.loc = loc
        super(TSDBTrace, self).__init__(sensor_name,
                                        start_limit,
                                        stop_limit)

    
    def load_data(self, start_limit=None, stop_limit=None):
        start_limit, stop_limit = self.get_limits(start_limit, stop_limit)
        if not start_limit:
            raise TSDBException("Starting time should be given")

        request_string = '/q?start=' + start_limit.strftime(self.TIME_FORMAT)
        if stop_limit:
            request_string += '&end=' + stop_limit.strftime(self.TIME_FORMAT)
        request_string += '&m=avg:SCADA.SODA.' + self.name
        request_string += '&ascii'

        conn = httplib.HTTPConnection(self.loc)
        conn.request("GET", request_string)
        response = conn.getresponse()
        if response.status != 200:
            raise TSDBException("Could not load Sensor Data: " + self.name + "\nError: " + response.reason)
        
        return self.__parse_data(response.read())
        

    def __parse_data(self, data):
        return [DataRecord(line.split()[2], int(line.split()[1])) \
                    for line in data.splitlines()]

                                
class FileTrace(SensorTrace):
    def __init__(self, loc, start_limit=None, stop_limit=None):
        self.loc = loc
        self.trace_files = []
        super(FileTrace, self).__init__(os.path.basename(loc),
                                        start_limit,
                                        stop_limit)
        
    def initialize(self):
        self.trace_files = [TraceFile(os.path.join(self.loc, file_name)) \
                                for file_name in os.listdir(self.loc) \
                                if file_name.endswith('H.DAT.csv')]
        # Ignore the Monthly aggregates
            
    def get_length(self):
        """Returns the trace length in months"""
        dates = [trace.get_date() for trace in self.trace_files]
        return ((max(dates) - min(dates)) / 30).days

    def load_data(self, start_limit=None, stop_limit=None):
        return_records = DataCollection()
        for trace in self.trace_files:
            log.info("Loading file: " + trace.loc)
            if start_limit and trace.get_date() < start_limit:
                continue
            if stop_limit and trace.get_date() > stop_limit:
                continue
            return_records.append(trace.get_data())
        return return_records


class SCADATrace(object):
    """Access SCADA Sensor data from various sources"""
    def __init__(self, location='prmohan-ec2.dyndns.org:4242', start_limit=None, stop_limit=None):
        self.traces = []
        self.start_limit = start_limit
        self.stop_limit = stop_limit
        
        if location.find('4242') != -1:
            self.__tsdb_trace_initialize(location)
        else:
            self.__file_trace_initialize(location)        

    def __tsdb_trace_initialize(self, location):
        self.traces = [TSDBTrace(location, sensor_name, self.start_limit, \
                                 self.stop_limit) \
                       for sensor_name in self.__get_tsdb_metrics(location)]
        
    def __file_trace_initialize(self, directory):
        self.traces = [FileTrace(os.path.join(directory, sensor_name),
                                   self.start_limit, self.stop_limit) \
                           for sensor_name in os.listdir(directory)]

    def __get_tsdb_metrics(self, location):
        request_string = '/suggest?type=metrics&q=SCADA.SODA'
        conn = httplib.HTTPConnection(location)
        conn.request("GET", request_string)
        response = conn.getresponse()
        if response.status != 200:
            raise TSDBException("Could not load Sensor Names.\nError: " + response.reason)
        data = response.read()
        return [sensor[sensor.rfind('.') + 1 : ] for sensor in eval(data)]

    def get_sensor_types(self):
        """Returns the different types of sensors in the Trace"""
        return set([trace.get_type() for trace in self.traces])

    def get_traces(self, type):
        """Returns all Sensors of a given `type'"""
        return [trace for trace in self.traces \
                    if trace.get_type() == type]

    def get_trace(self, sensor_name):
        """Given the name of the sensor retrieve the SensorTrace
        object"""
        for trace in self.traces:
            if trace.get_name().name == sensor_name:
                return trace

    def get_sensor_names(self):
        """Returns the names of all the sensors in the trace"""
        return [trace.get_name() for trace in self.traces]

    def get_rooms(self, floor_no=None):
        """Get the room map of the building"""
        room_map = {}
        for sensor in self.traces:
            if not sensor.is_room():
                continue
            room_no = sensor.get_name().room_no
            if floor_no and sensor.get_name().floor != floor_no:
                continue
            sensor_type = sensor.get_name().type
            if not room_map.has_key(room_no):
                room_map[room_no] = Room(room_no)

            if sensor_type == 'ARS':
                room_map[room_no].ARS = sensor
            elif sensor_type == 'ART':
                room_map[room_no].ART = sensor
            elif sensor_type == 'VAV':
                room_map[room_no].VAV = sensor
                room_map[room_no].reheat = False
            elif sensor_type == 'RVAV':
                room_map[room_no].VAV = sensor
                room_map[room_no].reheat = True
        return room_map

    def get_floors(self):
        """Retrieve the floor map of the building"""
        floor_map = collections.defaultdict(dict)
        room_map = self.get_rooms()

        for room in room_map:
            floor = room_map[room].get_name().floor
            floor_map[floor][room] = room_map[room]
            
        return floor_map


class Room(object):
    def __init__(self, room_no):
        self.room_no = room_no
        self.name = Name('R' + room_no + '_ROOM')
        self.reheat = False
        self.ART  = None                  # air temp
        self.ARS  = None                  # set point
        self.VAV  = None                  # variable air vol

    def get_summary(self):
        return self.ART.get_summary()

    def get_name(self):
        return self.name


def get_datetime(year, month):
    return datetime(year, month, 1)

def clean_name(name):
    return name.replace('_', '')

def get_clean(data):
    return [x for x in data if not isnan(x)]
