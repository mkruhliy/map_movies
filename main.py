"""
HTML Map
"""
# import time

import argparse
import pandas as pd
import folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from geopy.extra.rate_limiter import RateLimiter
from haversine import *


parser = argparse.ArgumentParser()
parser.add_argument("year", help='year')
parser.add_argument("lat", help='latitude')
parser.add_argument("lon", help='longtitude')
parser.add_argument("path_data", help='path to dataset')
args = parser.parse_args()


def FileRead(file):
    """
    Return the file content
    """
    content = []
    with open(file, 'r+', encoding='latin1') as file:
        for line in file.readlines():
            row = ''.join(line.split('\n'))
            row = row.split('\t')
            content.append(row)
    return content[15:-1]


def FormatingData(file):
    """
    Formating data from FileRead
    """
    content = FileRead(file)
    years = []
    names = []
    raw_location = []
    for i in content:
        splt = i[0].split('(')

        name = splt[0]
        names.append(name)

        year = splt[1].split(')')[0]
        years.append(year)

        place = ''.join(i[1:])
        raw_location.append(place)

    location = []
    for i in raw_location:
        part = i.split(',')[-1]
        part = part.split('(')[0]

        country = [j for j in part if j != ' ']
        first = i.split(',')[-3:-1]

        result = ''.join(first) + ' ' + ''.join(country)
        location.append(result)

    df = pd.DataFrame({'NAMES': names, 'YEARS': years, 'LOCATIONS': location})
    df = df[df['YEARS'] == args.year]
    return df


def LatitudeLongtitude(file):
    """
    Geo data
    """
    df = FormatingData(file)
    places = list(df['LOCATIONS'])
    lat = []
    lon = []

    geolocator = Nominatim(user_agent="UCU")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0.5)
    for i in places:
        try:
            lat_str = str(geolocator.geocode(i).latitude)
            lon_str = str(geolocator.geocode(i).longitude)
            lat.append(lat_str)
            lon.append(lon_str)
        except AttributeError:
            lat.append('NODATA')
            lon.append('NODATA')

    df['LAT'] = lat
    df['LON'] = lon
    df = df[df['LAT'] != 'NODATA']
    df = df[df['LON'] != 'NODATA']
    distance = []

    for i, j in zip(list(df['LAT']),list(df['LON'])):

        distance1 = haversine((float(args.lat), float(args.lon)), (float(i), float(j)))
        distance.append(round(distance1, 2))
    df['DISTANCE'] = distance

    return df


def Map(file):
    """
    Generating map
    """
    df = LatitudeLongtitude(file)
    df_close = df.sort_values(by=['DISTANCE'])
    df_close = df_close.drop_duplicates(subset=['DISTANCE'])
    df_close = df_close[:10]

    map = folium.Map(location=[args.lat, args.lon],
                     tiles="Stamen Terrain", zoom_start=8)
    map.add_child(folium.Marker([args.lat, args.lon],
                                popup="Your coordinates",
                                 icon=folium.Icon(color='blue')))
    fg_close = folium.FeatureGroup(name="10 closest")
    fg_by_year = folium.FeatureGroup(name="All moviies of {}".format(args.year))

    lat = df_close['LAT']
    lon = df_close['LON']
    nam = df_close['NAMES']

    for lt, ln, nm in zip(lat, lon, nam):
        fg_close.add_child(folium.Marker(location=[lt, ln],
                                         popup=nm, 
                                         icon=folium.Icon(color='red')))

    lat = df['LAT']
    lon = df['LON']
    nam = df['NAMES']

    for lt, ln, nm in zip(lat, lon, nam):
        fg_by_year.add_child(folium.Marker(location=[lt, ln],
                                                popup=nm,
                              icon=folium.Icon(color='red')))

    map.add_child(fg_by_year)
    map.add_child(fg_close)
    map.add_child(folium.LayerControl())
    map.save('Map.html')


def main():
    """
    Main function
    """
    print("Map is generating")
    Map(args.path_data)
    print("Done")

if __name__ == '__main__':
    main()


    # start = time.time()
    # main()
    # end = time.time()
    # print(end-start)
