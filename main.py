# this class contains all the functions that handle the sattlite data
import csv
import datetime
import time
import urllib.request

import ephem
from skyfield.api import load, utc
from calendar import timegm

#import ephem
import math

import numpy as np


import pickle

import ephem

#import distance_functions


def seconds_between(d1, d2):
    return abs((d2 - d1).seconds)

def datetime_from_time(tr):
    year, month, day, hour, minute, second = tr.tuple()
    dt = datetime.datetime(year, month, day, hour, minute, int(second))
    return dt

def dist(lat_1, lon_1 ,  lat_2, lon_2 ):
    r = 6376.5*1000
    r2=r+ 550*1000
    x_1 = r * math.sin(lon_1) * math.cos(lat_1)
    y_1 = r * math.sin(lon_1) * math.sin(lat_1)
    z_1 = r * math.cos(lon_1)

    x_2 = r2 * math.sin(lon_2) * math.cos(lat_2)
    y_2 = r2 * math.sin(lon_2) * math.sin(lat_2)
    z_2 = r2 * math.cos(lon_2)
    dist = math.sqrt((x_2 - x_1) * (x_2 - x_1) + (y_2 - y_1) *
                     (y_2 - y_1) + (z_2 - z_1) * (z_2 - z_1))
    return dist

#lat long in rads, alt in km
def distB(lat_1, lon_1 ,  lat_2, lon_2, alt ):
    r=6371+alt
    r2= 6371+550

    cosLat1=math.cos(lat_1)
    cosLat2=math.cos(lat_2)

    sinLat1=math.sin(lat_1)
    sinLat2 = math.sin(lat_2)

    cosr1=cosLat1*r
    cosr2=cosLat2*r2
    
    zz1=sinLat1*r
    zz2 = sinLat2 * r2
    xx1=math.cos(lon_1)*cosr1
    xx2=math.cos(lon_2)*cosr2

    yy1=math.sin(lon_1)*cosr1
    yy2=math.sin(lon_2)*cosr2

    dz=zz1-zz2
    dx=xx1-xx2
    dy=yy1-yy2

    dist=math.sqrt(dz*dz+dx*dx+dy*dy)

    return dist



def get_next_pass(lon, lat, alt,tle):

     #sat = ephem.readtle(str(tle[0]), str(tle[1]), str(tle[2]))
     sat = ephem.readtle(tle[0].decode("utf-8"), tle[1].decode("utf-8"), tle[2].decode("utf-8"))
     observer = ephem.Observer()
     observer.lat = str(lat)
     observer.long = str(lon)
     observer.elevation = alt
     observer.pressure = 0
     #observer.horizon = '-0:34'
     text = tle[0].decode("utf-8")
     now = datetime.datetime.utcnow()
     observer.date = now
     sat.compute(observer)
     from ephem import degree
     deg_lat=sat.sublat/degree
     deg_lon=sat.sublong/degree
     sat_lat= np.deg2rad(deg_lat)
     sat_lon= np.deg2rad(deg_lon)
     sat_alt=sat.alt
     #sat_lat=sat.sublat
     #sat_lon=sat.sublong
     #tr, azr, tt, altt, ts, azs = observer.next_pass(sat)

     #duration = int((ts - tr) *60*60*24)
     # rise_time = datetime_from_time(tr)
     # max_time = datetime_from_time(tt)
     # set_time = datetime_from_time(ts)

     #observer.date = max_time

     # sun = ephem.Sun()
     # sun.compute(observer)
     yh=sat.compute(observer)

     #sun_alt = np.degrees(sun.alt)

     visible = False
     #sep= ephem.separation((np.deg2rad(lon), np.deg2rad(lat)), (sat_lon, sat_lat))
     sep=distB(np.deg2rad(lat), np.deg2rad(lon), sat_lat, sat_lon, alt)
     alt=0
     distance=sep

     #if sat.eclipsed is False and -18 < sat_alt < -8 :
     if distance <1500:
        visible = True
        print(distance)
     return visible, {"sat": text, "lat": deg_lat, "lon": deg_lon, "inclenation": sat._inc, "dist": distance}


def main():
    lon=35.20944444
    lat=32.10472222
    alt=0.68
    StarLink_list = 'http://www.celestrak.com/NORAD/elements/starlink.txt'
    GPS_list = 'http://www.celestrak.com/NORAD/elements/gps-ops.txt'
    visibleSats = []
    satListInTime=[]
    for i in range(10): #loop in time
        sats=[]
        with urllib.request.urlopen(StarLink_list) as url:
            tles = url.readlines()
            # print(tles)
            tles = [item.strip() for item in tles]
            tles = [(tles[i], tles[i + 1], tles[i + 2]) for i in range(0, len(tles) - 2, 3)]

            s = ""
            c = 0
            for tle in tles:
                try:
                    visible, dic=get_next_pass(lon,lat,alt,tle)
                    if visible:
                        visibleSats.append(dic)
                        sats.append(dic["sat"])
                except ValueError as e:
                    print(e)
                    #if (sats)
                    #print(visibleSats)

            keys = visibleSats[0].keys()
            output_file = open("output_"+str(i)+"_.csv", "w")
                        # for s in keys:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(visibleSats)
            output_file.close()
            satListInTime.append(sats)

            time.sleep(1)
    with open("satsInTime.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(satListInTime)

    #createFilesFromTLe(5,0.5 ,lat_lon__csv_file=True,distance_csv_file=True,VG_files=True)

if __name__ == "__main__":

    print(distB(np.deg2rad(32.103),np.deg2rad( 35.208), np.deg2rad(37),np.deg2rad(30), 0.68))
    main()