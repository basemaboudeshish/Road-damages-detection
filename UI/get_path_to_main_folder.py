import os
import subprocess 
import runpy

def get_RDD_Path():
    buffer = os.path.dirname(__file__).split("\\")
    path = ""

    for element in buffer:
        path = rf'{path}{element}/'
        if element == "RoadDamageDetection":
            print(path)
            break

    return path