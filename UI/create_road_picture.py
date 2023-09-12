import gpxpy 
import gpxpy.gpx 
from gpxplotter import read_gpx_file, create_folium_map, add_segment_to_map
import folium
import io
from PIL import Image
from selenium import webdriver
import os
import time
from get_path_to_main_folder import get_RDD_Path
from geopy.geocoders import Nominatim

def create_frontpicture(gpx_path):
    points=[]
    gpx_file = open(gpx_path, 'r') 
    gpx = gpxpy.parse(gpx_file) 
    for track in gpx.tracks: 
        for segment in track.segments: 
            for point in segment.points: 
                points.append([point.latitude, point.longitude])

    m = folium.Map(location=points[0], zoom_start=13)
    f1=folium.FeatureGroup("Vehicle 1")
    line_1=folium.vector_layers.PolyLine(points,popup='<b>Path of Vehicle_1</b>',tooltip='Vehicle_1',color='blue',weight=10).add_to(f1)
    f1.add_to(m)
    try:
        with open(f'{get_RDD_Path()}report\\reportdata\\damage_list.txt', "r") as f:
            q = f.read()    
        DamageFrameList = [ int(x) for x in q.split(',') if x.isdigit() ]
    except:
        DamageFrameList = []
    for i in DamageFrameList:
        test = points[i]
        folium.Marker(points[i]).add_to(m)

    # save the map as html
    mapFname = 'output.html'
    m.save(mapFname)

    mapUrl = 'file://{0}/{1}'.format(os.getcwd(), mapFname)

    # use selenium to save the html as png image
    driver = webdriver.Firefox(executable_path = f'{get_RDD_Path()}tools\geckodriver.exe')
    driver.get(mapUrl)
    # wait for 5 seconds for the maps and other assets to be loaded in the browser
    time.sleep(5)
    driver.save_screenshot(f'{get_RDD_Path()}report\\reportdata\\frontpage\\drivepicture.png')
    driver.quit()
    os.remove('output.html')
    os.remove('geckodriver.log')



def get_adress(Latitude,Longitude):
    geolocator = Nominatim(user_agent="geoapiExercises") 
    location = geolocator.reverse(Latitude+","+Longitude)

    return location








