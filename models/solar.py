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
import numpy as np
import pdb

def radiation(day=False):
    """
    Return average amount of solar radiation falling on atmosphere
    normal to the rays of the sun in W/m^2 on specified dnay of year If
    no argument is provided, return the average 1367 W/m^2,
    """
    I0 = 1367
    if np.any(day):
        return I0*(1 + 0.034*np.cos(np.radians(360*day/365.25)))
    else:
        return 1367

def declination(day):
    """
    Return the solar declination in degrees on day n with January 1
    being n=1. The solar declination is the angle between the
    earth-sun line and the plane through the equator. It varies
    between -23.45 degrees on Dec 21 and 23.45 degrees on June 21. It
    has the same numerical value as the latitude at which the sun is
    directly overhead at noon on a given day.
    """
    return 23.45*np.sin(2*np.pi*(284 + day)/365)
#    return np.degrees(np.sin(np.radians(23.45)) * np.sin(np.radians(360*(284 + day)/365)))

def declination2(day):
    """
    A somewhat more precise calculation of the declination.  See
    declination.
    """
    x = 2*np.pi*day/365
    d = 0.302 - 22.93*np.cos(x) - 0.229*np.cos(2*x) - 0.243*np.cos(3*x) + 3.851*np.sin(x) + 0.002*np.sin(2*x) - 0.055*np.sin(3*x)
    return d

# 30 days hath September, April, June and November, All the rest have 31, Excepting February alone
months    = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
monthDays = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def rsum(a):
    s = 0
    rs = []
    for x in a:
        rs.append(s)
        s = s+x
    return rs

sumDays = rsum(monthDays)

def findDay(day):
    """
    Return (mon, day) for the spacified year day.
    """
    for month in range(0,12):
        if day <= monthDays[month]:
            return (months[month], day)
        day = day - monthDays[month]
    return ('err', -1)

def mapDay(month,day):
    """
    Map a month and day of month to year day.
    """
    yday = 0
    for mon in range(0,12):
        if month == months[mon] :
            if day > monthDays[mon] : return -1
            return yday+day
        yday = yday + monthDays[mon]
    return -1

def hourAngle(h):
    """
    Return the hour angle in degrees, which is the rotation relative
    to local solar noon.  noon=>0
    """
    return (h-12)*15

def angleHour(a):
    """
    Return local solar time from hour angle.
    """
    return (a+180)/15

def hourAngleWest(lat, day):
    l = np.radians(lat)
    d = np.radians(declination(day))
    if (lat == 0): return 90
    tw = np.arccos(np.tan(d)/np.tan(l))
    return np.degrees(tw)

def altitudeOld(lat, day, hour):
    """
    Return the solar altitude angle at specified latitude on day of
    year and time This is the angle of the sun relative to a
    horizontal plans.
    """
    l = np.radians(lat)
    d = np.radians(declination(day))
    h = np.radians(hourAngle(hour))
    sin_aa = np.sin(l)*np.sin(d) + np.cos(l)*np.cos(d)*np.cos(h)
    alpha = np.arcsin(sin_aa)
    return np.degrees(alpha)

def zenith(lat, day, hour):
    """
    Return the solar Zenith angle at specified latitude on day of year
    and time This is the angle of the sun relative to the zenith
    """
    l = np.radians(lat)
    d = np.radians(declination(day))
    h = np.radians(hourAngle(hour))
    cos_sz = np.sin(l)*np.sin(d) + np.cos(l)*np.cos(d)*np.cos(h)
    sz = np.arccos(cos_sz)
    return np.degrees(sz)

def altitude(lat, day, hour):
    return 90 - zenith(lat, day, hour)

def sunrise(lat, day):
    d = np.radians(declination(day))
    l = np.radians(lat)
    sr = np.arccos(-np.tan(l)*np.tan(d))
    return -np.degrees(sr)

def sunset(lat, day):
    d = np.radians(declination(day))
    l = np.radians(lat)
    sr = np.arccos(-np.tan(l)*np.tan(d))
    return np.degrees(sr)

def azimuthRaw(lat, day, hour):
    """
    Return the Solar Alzimuth angle, which is the angle measured from
    due south of the earth-sun line projected onto the horizontal
    plane
    """
    d = np.radians(declination(day))
    h = np.radians(hourAngle(hour))
    l = np.radians(lat)
    cos_sz = np.sin(d)*np.sin(l) + np.cos(d)*np.cos(l)*np.cos(h)
    sz = np.arccos(cos_sz)
    sin_sz = np.sin(sz)
    sin_sa = -np.cos(d)*np.sin(h)/sin_sz
    sa = np.arcsin(sin_sa)
    return sa

def azimuth(lat, day, hour):
    """
    Return the Solar Alzimuth angle, which is the angle measured from
    due north increasing toward east (90) of the earth-sun line
    projected onto the horizontal plane
    """
    d = np.radians(declination(day))
    h = np.radians(hourAngle(hour))
    l = np.radians(lat)
    z = np.radians(zenith(lat,day,hour))
    sin_sa = -np.cos(d)*np.sin(h)/np.sin(z)
# fix up the angle ambiguity arisine from sin(a) = sin(180-a) = sin(360+a)
    csa = np.arcsin(sin_sa)
    sa1 = np.degrees(csa)
    sa2 = 180 - sa1
    ewtest = np.cos(h) < (np.tan(d)/np.tan(l))
    ew    = np.where(sa1>=0, sa1, 360+sa1)
    north = np.where(ewtest, ew, sa2)
    n2    = np.where(l <= d, ew, north)
    sew   = np.where(sa1>=0,sa2,-180-sa1)
    south = np.where(ewtest, sew, sa1)
    s2    = np.where(l >= d, sew, south)
    sa    = np.where(l >= 0, n2, s2)
    return sa

def incident(lat, day, hour, tilt, direction, attenuate=False):
    """
    incident(lat, day, hour, tilt, direction) computes the normalized
    incident solar radiation of the beam on a panel with normal tilt
    relative to verticle and oriented at angle direction relative to
    true north.

    incident ~ cos X = cos(tilt)*cos(alt) + sin(tilt)*sin(alt)*cos(dir-az)

    The optional attenuate factor accounts for attenuation through the
    atmosphere, typically used in conjunction with computing radiation
    onto an object
    """
    zen  = zenith(lat, day, hour)
    az   = azimuth(lat, day, hour)
    zrad = np.radians(zen)
    trad   = np.radians(tilt)
    drad   = np.radians(direction - az)
    vert   = np.where(np.less(zen,90), np.cos(trad)*np.cos(zrad),0)
    hor    = np.where(np.less(zen,90), np.sin(trad)*np.sin(zrad)*np.cos(drad), 0)
    cosX = np.maximum(0,hor+vert)
    if (attenuate):
        if (attenuate == True): tau = 0.1
        else: tau = attenuate
        return cosX*np.exp(-tau/np.cos(zrad))
    else: 
        return cosX
