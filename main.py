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

def distance(lat_1, lon_1, alt_1 , lat_2, lon_2, alt_2):

    r = 6376.5 * 1000
    x_1 = r * math.Sin(lon_1) * math.Cos(lat_1)
    y_1 = r * math.Sin(lon_1) * math.Sin(lat_1)
    z_1 = r * math.Cos(lon_1)

    x_2 = r * math.Sin(lon_2) * math.Cos(lat_2)
    y_2 = r * math.Sin(lon_2) * math.Sin(lat_2)
    z_2 = r * math.Cos(lon_2)
    dist = math.Sqrt((x_2 - x_1) * (x_2 - x_1) + (y_2 - y_1) *
                     (y_2 - y_1) + (z_2 - z_1) * (z_2 - z_1))

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
     sat_lat= np.rad2deg(sat.sublat)
     sat_lon= np.rad2deg(sat.sublong)

     tr, azr, tt, altt, ts, azs = observer.next_pass(sat)

     duration = int((ts - tr) *60*60*24)
     rise_time = datetime_from_time(tr)
     max_time = datetime_from_time(tt)
     set_time = datetime_from_time(ts)

     observer.date = max_time

     sun = ephem.Sun()
     sun.compute(observer)
     sat.compute(observer)

     sun_alt = np.degrees(sun.alt)

     visible = False
     sep= ephem.separation((lon, lat), (sat_lon, sat_lat))
     alt=0
     distance=sep

     #if sat.eclipsed is False: #and -18 < np.degrees(sun_alt) < -6 :
     if distance <0.1:
        visible = True
        print(distance)
     return visible, {"sat": text, "lat": sat_lat, "lon": sat_lon, "inclenation": sat._inc, "duration": duration}


def main():
    lon=35.207718
    lat=32.103188
    alt=660
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
    main()