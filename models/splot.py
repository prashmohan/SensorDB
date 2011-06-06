#!/usr/bin/env python
"""
Author:  culler@cs.berkeley.edu
         http://www.cs.berkeley.edu/~culler
        
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

import solar
import energy
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

def plotZenithDays(lats,days):
    ts = np.arange(0,24,0.25)
    for lat in lats:
        for day in days:
            (mon,md) = solar.findDay(day)
            plt.plot(ts,solar.zenith(lat,day,ts),label= mon + " " + str(md) + " " + str(lat) + "deg")
    plt.plot(ts,90*np.ones(len(ts)),label="horizon")
    plt.axis([0,24,0,180])
    plt.xlabel('Hour')
    plt.ylabel('deg')
    plt.title('Solar Zenith Angle over Day at '+str(lat)+' degs lat')
    axes = plt.axes()
    handles, labels = axes.get_legend_handles_labels()
    axes.legend(handles, labels, loc=3)
    return axes

def plotAltitudeDays(lats,days):
    ts = np.arange(0,24,0.25)
    for lat in lats:
        for day in days:
            (mon,md) = solar.findDay(day)
            plt.plot(ts,solar.altitude(lat,day,ts),label= mon + " " + str(md) + " " + str(lat) + "deg")
    plt.plot(ts,0*np.ones(len(ts)),label="horizon")
    plt.axis([0,24,-90,90])
    plt.xlabel('Hour')
    plt.ylabel('deg')
    plt.title('Solar Altitude Angle over Day at '+str(lat) + ' degs lat')
    axes = plt.axes()
    handles, labels = axes.get_legend_handles_labels()
    axes.legend(handles, labels, loc=3)
    return axes

def plotAzimuthDays(lat,days):
    ts = np.arange(0,24,0.25)
    for day in days:
        (mon,md) = solar.findDay(day)
        plt.plot(ts,solar.azimuth(lat,day,ts),label= mon + " " + str(md) + " " + str(lat) + "deg")
    plt.xlabel('Hour')
    plt.ylabel('deg')
    plt.title('Solar Azimuth Angle over Day at '+str(lat)+' degs lat')
    axes = plt.axes()
    handles, labels = axes.get_legend_handles_labels()
    axes.legend(handles, labels, loc=2)
    return axes

def plotAzimuthDaysFix(lats,days):
    ts = np.arange(0,24,0.25)
    h = np.radians(solar.hourAngle(ts))
    for lat in lats:
        for day in days:
            d = np.radians(solar.declination(day))
            l = np.radians(lat)
            print 'day: ' + str(day) + " lat: " + str(lat), np.tan(d), np.tan(l), np.tan(d)/np.tan(l)
    
            (mon,md) = solar.findDay(day)
            plt.plot(ts,solar.azimuthRaw(lat,day,ts),label= mon + " " + str(md) + " " + str(lat) + " deg")
    plt.plot(ts, np.cos(h))
    plt.plot(ts, (np.tan(d)/np.tan(l)) * np.ones(len(ts)))
    plt.title('Solar Azimuth Angle Day')
    plt.xlabel('Hour')
    plt.ylabel('rad')
    axes = plt.axes()
    handles, labels = axes.get_legend_handles_labels()
    axes.legend(handles, labels, loc=3)
    return axes

def plotPath(lat,days):
    ts = np.arange(0,24,0.25)
    for day in days:
        (mon,md) = solar.findDay(day)
        az= solar.azimuth(lat,day,ts)
        alt = solar.altitude(lat,day,ts)
        plt.plot(az,alt,label= mon + " " + str(md) + " " + str(lat) + "deg")
    plt.xlabel('azimuth')
    plt.ylabel('altitude')
    plt.title('Solar Path over Day at '+str(lat)+' degs lat')
    axes = plt.axes()
    handles, labels = axes.get_legend_handles_labels()
    axes.legend(handles, labels, loc=2)
    return axes

def plotIncident(lats, days, tilts, dirs, attenuate=False):
    if np.isscalar(lats):  lats  = [lats]
    if np.isscalar(days):  days  = [days]
    if np.isscalar(tilts): tilts = [tilts]
    if np.isscalar(dirs):  dirs  = [dirs]
    ts = np.arange(0,24,0.25)
    h = np.radians(solar.hourAngle(ts))
    for lat in lats:
        for day in days:
            for tilt in tilts:
                for dir in dirs:
                    (mon,md) = solar.findDay(day)
                    plt.plot(ts,solar.incident(lat,day,ts,tilt,dir,attenuate),label= mon + " " + str(md) + " " + str(lat) + " deg @" +str(tilt)+"["+str(dir)+"]" )
    plt.title('Effective Incident Solar')
    plt.xlabel('Hour')
    axes = plt.axes()
    handles, labels = axes.get_legend_handles_labels()
    axes.legend(handles, labels, loc=2)
    return axes                         

def plotHoursEff(lats, tilts, dirs):
    if np.isscalar(lats):  lats  = [lats]
    if np.isscalar(tilts): tilts = [tilts]
    if np.isscalar(dirs):  dirs  = [dirs]
    days = np.arange(1,365)
    for lat in lats:
        for tilt in tilts:
            for dir in dirs:
                vals = [energy.solarHours(lat,day,tilt,dir) for day in days]
                plt.plot(vals,label= str(lat) + " deg @" +str(tilt)+"["+str(dir)+"]" )
    plt.title('Effective Solar Hours per Day')
    plt.xlabel('Day')
    axes = plt.axes()
    handles, labels = axes.get_legend_handles_labels()
    axes.legend(handles, labels, loc=2)
    return axes                         
