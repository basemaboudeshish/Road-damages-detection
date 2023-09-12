from geopy.geocoders import Nominatim
from run_yolo import run_rdd

def get_adress(Latitude,Longitude):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.reverse(Latitude+","+Longitude)

    return location
 
