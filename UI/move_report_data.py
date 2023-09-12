from msilib.schema import Directory
import os
from statistics import mean
from cv2 import pointPolygonTest
from get_path_to_main_folder import get_RDD_Path
import shutil
from create_gpx_file import create_gpx
from create_gpx_file import getMetadata
import gpxpy 
from geopy.geocoders import Nominatim
import gpxpy.gpx 
from gpxplotter import read_gpx_file, create_folium_map, add_segment_to_map
import folium
from selenium import webdriver
from generate_report import create_report
from selenium.webdriver.firefox.options import Options
import cv2
import subprocess
from run_yolo import run_rdd
import time
from yolov5.utils.get_path_to_exp_folder import get_path_to_exp_folder # pass the experiment path


RDD_Path = get_RDD_Path()
exp_name = f'{get_path_to_exp_folder()}'
RDDpath = f'{RDD_Path}yolov5\\RDD/'
exp_path = RDDpath + exp_name 
print(exp_path)


def create_metadata_file():
    file_path = f'{RDD_Path}report\\Company.txt'
    try:
        with open(file_path, "r") as file:
            contents = file.read()
            print(contents)
    except FileNotFoundError:
        print("File not found.")
    with open(f'{RDD_Path}report\\reportdata\\frontpage\\CompanyName.txt', 'w+') as f:
        f.write(contents) # make it take the value stored in the variable

def get_adress(Latitude,Longitude):# input Latitude and Longitude and return the acording adress, if no internet or invalid inpuit return errorr message
    geolocator = Nominatim(user_agent="geoapiExercises")
    try: 
        location = geolocator.reverse(Latitude+","+Longitude)
    except:
        location = "address could not be resolved"
        
    return location

def clean_report_data_folder(dir_path = None):# clear Folder structure (by default report data folder)
    
############################################ define path variables for recreation ############################## 
    if dir_path is None:
        dir_path = f'{RDD_Path}report\\reportdata'
    frame_path = f'{RDD_Path}report\\reportdata\\frontpage'
    mode = 0o666

########################################### deletes all Folders in reportdata #################################

    if os.path.exists(dir_path): # check if the path exists
        shutil.rmtree(dir_path, ignore_errors=True) 

############################################ recreation of basic folder structure ############################# 

    os.makedirs(dir_path, mode, exist_ok=True)
    os.makedirs(frame_path, mode, exist_ok=True)

def create_segment_Folders(NrofFrames,SegmentSize,parent_dir = None):

    mode = 0o666
    if parent_dir is None:
        parent_dir = f'{RDD_Path}report\\reportdata'

    if NrofFrames%SegmentSize == 0:
        SizeOfSegments = int(NrofFrames/SegmentSize)
    else:
        SizeOfSegments = int(NrofFrames/SegmentSize) + 1

    for i in range(SizeOfSegments):
        directory = f'Segment{i+1}'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path, mode)


def count_labels(path): 
    files = [f for f in os.listdir(path) if f.endswith('.txt')] # list all .txt files
    print(files)
    print(len(files))
    labels_list = [] # saves all labels (eg. 0,1,2,3...)
    counted_labels = {} # dictionary with class as key and the number of occurrences as value eg. Key: class0 value: 507; Key: class1 value: 304

    # loop through the files in the directory and save the labels (first letter of each line in a file)
    for file in files:
        file_path = os.path.join(path, file)
        with open(file_path, "r") as txtfile:
            # read the first character of each line and append to labels_list
            labels_list += [line[0] for line in txtfile]
    print('labels_list', labels_list)

    # create a set of all unique labels
    labels = set(labels_list)
    print('labels' ,labels)
    
    # create dictionary with class as key and number of occurrences as value
    # Loop through each label and count the number of occurrences in the labels_list
    for label in labels:
        class_name = f"Class{label}"
        counted_labels[class_name] = labels_list.count(label)
    print('counted_labels', counted_labels)

    # Get the count of each label and return as a list
    count_list = [str(counted_labels.get(f"Class{i}", 0)) for i in range(4)]  # Assuming there are 4 possible labels
    print('count_list',count_list)
    return count_list

def labels_classification(path,BeginOfSegment,EndOfSegment):  # part of count_labels_of_Segment function in order to return the classification of the damage only   
    allFiles = [] # Saves names of all Files in directory that are txt Files
    labels = [] #saves all Lables (eg. 0,1,2,3...)
    lables_List = []# saves all ocations of all Lables eg 0,0,1,0,2,4,3
    files = []# Saves names of all Files in the Segment 
    SegmentedLableList = []# saves all ocations of all Lables in Segment eg 0,0,1,0,2,4,3,



    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            if file.endswith('.txt') and file.find('_'):
                allFiles.append(file)
                q = file.rfind('_')
                Nr = file[q+1:].rstrip('.txt')
                if int(Nr) < EndOfSegment and int(Nr) > BeginOfSegment:
                    files.append(file)
                #print(r,d)

    # loop through the files in the directory and save the Lables (first letter of each line in a File)
    for f in allFiles:
        act_file = path + "\\"  + f
        try:
            txt = open(act_file, "rt")
        except:
            continue
        for line in txt:  
            lables_List.append(line [0])
    print('lables_List',lables_List)

    # create a List of all Lables (each element just once) 
    for objekt in lables_List:
        if objekt in labels:
            continue
        else:
            labels.append(objekt)
    print('label',labels)      

    # loop through the files in the directory and save the Lables of segment (first letter of each line in a File)
    for f in files:
        act_file = path + "\\"  + f
        try:
            txt = open(act_file, "rt")
        except:
            continue
        for line in txt:  
            SegmentedLableList.append(line [0])

    labels.sort()
    labels = list(labels) # transform the set into a list
    print('label',labels)
    return labels

def count_labels_of_Segment(path,BeginOfSegment,EndOfSegment):
    allFiles = [] # Saves names of all Files in directory that are txt Files
    labels = [] #saves all Lables (eg. 0,1,2,3...)
    lables_List = []# saves all ocations of all Lables eg 0,0,1,0,2,4,3
    couted_labels = {}# creates dictionary with class as key and the number of ocations as value eg. Key: class0 value: 507; Key: class1 value: 304
    count_list = []# Saves values of couted_labels as List eg [507,304,...]
    files = []# Saves names of all Files in the Segment 
    SegmentedLableList = []# saves all ocations of all Lables in Segment eg 0,0,1,0,2,4,3,

    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            if file.endswith('.txt') and file.find('_'):
                allFiles.append(file)
                q = file.rfind('_')
                Nr = file[q+1:].rstrip('.txt')
                if int(Nr) < EndOfSegment and int(Nr) > BeginOfSegment:
                    files.append(file)
                #print(r,d)

    # loop through the files in the directory and save the Lables (first letter of each line in a File)
    for f in allFiles:
        act_file = path + "\\"  + f
        try:
            txt = open(act_file, "rt")
        except:
            continue
        for line in txt:  
            lables_List.append(line [0])
    print('lables_List',lables_List) 

    # create a List of all Lables (each element just once) 
    for objekt in lables_List:
        if objekt in labels:
            continue
        else:
            labels.append(objekt)
    print('label',labels)     

    # loop through the files in the directory and save the Lables of segment (first letter of each line in a File)
    for f in files:
        act_file = path + "\\"  + f
        try:
            txt = open(act_file, "rt")
        except:
            continue
        for line in txt:  
            SegmentedLableList.append(line [0])

    labels.sort()
    print('label',labels) 

    # create dictionary with Class as Key and Nr of locations as value
    for objekt in labels:
      #print( 'Class ', objekt, ' = ' , lables_List.count(objekt))
      Key = 'Class'+ str(objekt)
      couted_labels.update({Key : SegmentedLableList.count(objekt)})
    print('couted_labels',couted_labels) 

    
    #convert dictionary to list to have both options 
    for i in range(4):  #Modify the range according to the number of classes you want to consider
        Key = f'Class{i}'
        count_list.append(couted_labels.get(Key, '0'))


    print('count_list', count_list)
    return count_list #couted_labels if you want to return a dictionary

def count_Damages(path):  # it returns a list of the frames with damages, name of fuction need to changed to reflect its function
    damages = [] # saves frame numbers in which damages were found
    files = [] # saves names of all files in directory that are txt files

    # loop through all files in the directory and append the names of the labels to the 'files' list if they are txt files
    for file in os.listdir(path):
        if file.endswith('.txt'):
            files.append(file)
    print('files',files)

    # loop through all files in the directory and append the label numbers in which damages were found to the 'damages' list
    for file in files:
        label_num = file[file.find('_')+1:].rstrip('.txt')
        damages.append(int(label_num))
    print('damages',damages)

    return damages


def gps_points_extraction(source_path):   # function to use gps data flexibly through the code
    points = []
    file_name = source_path.split('\\')[-1]
    file_name = file_name[:file_name.rfind('.')]
    gpx_path = f'{RDD_Path}report\\reportdata\\{file_name}.gpx'
    print(gpx_path)
    gpx_file = open(gpx_path, 'r')
    print(gpx_file)
    gpx = gpxpy.parse(gpx_file) 
    for track in gpx.tracks: 
        for segment in track.segments: 
            for point in segment.points: 
                points.append([point.latitude, point.longitude])
    print('points', points)
    print('Length of points', len(points))
    return points

def create_frontpage_and_segmet_data(source_path,NrofFrames,SegmentSize,RDD_Path,exp_path):
    
    ####################################### define / calculate importatnt variables ########################################

    points=[]
    DamegesOfSegment = [0, 0, 0, 0]
    file_name = source_path.split('\\')[-1]
    file_name = file_name[:file_name.rfind('.')]
    points = gps_points_extraction(source_path) # separating the gps points in a single function

    print(NrofFrames)
    NrOfSegments = int(NrofFrames/SegmentSize)
    point_per_segment = int(NrofFrames/NrOfSegments)
    FramesPerGPSPoint = NrofFrames/len(points)
    print("FramesPerGPSPoint", FramesPerGPSPoint)
    print(exp_path)
    labels_path = f'{exp_path}\\labels' 
    AllDamages = count_labels(labels_path)

    ########################################## Write text Files for Frontpage ##################################################################

    DamageFrameList = count_Damages(labels_path)
    print('DamageFrameList', DamageFrameList)
    with open(f'{RDD_Path}report\\reportdata\\frontpage\\info.txt', 'w+') as f:
        f.write(f'{AllDamages}') 
        print('AllDamages', AllDamages)

    ########################################### Write text Files and move pictures for Segments ################################################

    PriviousNrOfDamage = 0
    DamageLocations = []
    i = 1
    q = 0  # initialization of q for the number of frames
    NewGPSpoint = [0,0]# gps points
    PreviousGPSpoint = [0,0] # previous gps points

    while q <= NrofFrames:
        print('q', q)

        if q in DamageFrameList:
            print('2')
            NewGPSpoint = points[int(q / FramesPerGPSPoint)]
            print("NewGPSpoint",NewGPSpoint)
            DamageLocations.append(points[int(q / FramesPerGPSPoint)])
            print('DamageLocations', DamageLocations)
            with open(f'{exp_path}\\labels\\{file_name}_{q}.txt', 'r') as f:
                labels = f.read()
                NrOfDamage = labels.count('\n')
                print("NrOfDamage", NrOfDamage)

            if NrOfDamage >= PriviousNrOfDamage and (abs(NewGPSpoint[0] - PreviousGPSpoint[0]) > 0.00005 or abs(NewGPSpoint[1] - PreviousGPSpoint[1]) > 0.00004):
                        file_path = f'{exp_path}\\frames\\frame_{q}.jpg'
                        destination_path = f'{RDD_Path}report\\reportdata\\Segment{i}\\frame{q}.jpg'
                        shutil.copy2(file_path, destination_path)
                        with open(f'{RDD_Path}report\\reportdata\\Segment{i}\\info.txt', 'w+') as f:
                            DamegesOfSegment = count_labels_of_Segment(f'{exp_path}\\labels', (SegmentSize * (i - 1)), ((SegmentSize * (i - 1)) + SegmentSize))
                            print('SegmentSize * (i - 1)', SegmentSize * (i - 1))
                            print('((SegmentSize * (i - 1)) + SegmentSize)', ((SegmentSize * (i - 1)) + SegmentSize))
                            print('DamegesOfSegment', DamegesOfSegment)
                            f.write(f'Alligator Crack: {DamegesOfSegment[0]}\nLinear Crack: {DamegesOfSegment[1]}\nPothole: {DamegesOfSegment[2]}\nWhite Line: {DamegesOfSegment[3]}')
                        with open(f'{RDD_Path}report\\reportdata\\Segment{i}\\location{q}.txt', 'w+') as f: # write the location of the damage for every frame
                            f.write(f'gps: {points[int(q / FramesPerGPSPoint)]}\nAdress: {get_adress(str(points[int(q / FramesPerGPSPoint)][0]), str(points[int(q / FramesPerGPSPoint)][1]))}')
                            print('int(q/FramesPerGPSPoint)',int(q/FramesPerGPSPoint))

                        PriviousNrOfDamage = NrOfDamage
                        PreviousGPSpoint = points[int(q / FramesPerGPSPoint)] # make sure that the gps location is different


        q += 1

        if q > (SegmentSize* i):
            i += 1
            print ('i+1',i)
            PriviousNrOfDamage = 0
            continue

    ############################################# Create picture with road and damages for frontpage ###################################
    
    middlePoint = [0,0]
    for i in points:
        middlePoint[0] = middlePoint[0]+i[0]
        middlePoint[1] = middlePoint[1]+i[1]
    middlePoint[0] = middlePoint[0] / len(points)
    middlePoint[1] = middlePoint[1] / len(points)
        
    m = folium.Map(location=middlePoint, zoom_start=14)
    f1=folium.FeatureGroup("Vehicle 1")
    line_1=folium.vector_layers.PolyLine(points,popup='<b>Path of Vehicle_1</b>',tooltip='Vehicle_1',color='blue',weight=10).add_to(f1)
    f1.add_to(m)
    
    for i in range(len(DamageLocations)):
        folium.Marker(DamageLocations[i]).add_to(m)

    # save the map as html
    mapFname = 'output.html'
    m.save(mapFname)



    mapUrl = 'file://{0}/{1}'.format(os.getcwd(), mapFname)

    # use selenium to save the html as png image
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(executable_path = f'{RDD_Path}tools\\geckodriver.exe',options=options)
    driver.get(mapUrl)
    # wait for 5 seconds for the maps and other assets to be loaded in the browser
    time.sleep(5)
    driver.save_screenshot(f'{RDD_Path}report\\reportdata\\frontpage\\drivepicture.png')
    driver.quit()
    os.remove('output.html')
    os.remove('geckodriver.log')

def frames_number(source_path): # count number of frame in video files
    cap = cv2.VideoCapture(source_path) 
    NrofFrames =  int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    print(NrofFrames)

    return(NrofFrames)

def run_yolo_and_generate_report(source_path,SegmentSize=None):
    run_rdd(source_path)
    SegmentSize = 500
    NrofFrames = frames_number(source_path)

    clean_report_data_folder()
    create_metadata_file()
    create_gpx(source_path)
    create_segment_Folders(NrofFrames,SegmentSize)
    create_frontpage_and_segmet_data(source_path,NrofFrames,SegmentSize,RDD_Path,exp_path)
    create_report(source_path)