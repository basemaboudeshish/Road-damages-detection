import os
import subprocess
from get_path_to_main_folder import get_RDD_Path
import gpxpy
from gpxpy.gpx import GPX, GPXTrack, GPXTrackSegment, GPXTrackPoint
import datetime  
from math import floor 
import re 


def extract_gps_resolution():
    file_path = f'{get_RDD_Path()}report\\Camera_model.txt'
    number = 0.0  # Initialize the number variable
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if ':' in line:
                index = line.index(':') + 1
                num_str = line[index:].strip()
                try:
                    num = float(num_str)
                    number = num  # Update the number variable with the extracted integer
                    break  # Exit the loop after finding the first number
                except ValueError:
                    continue  # Skip lines that cannot be converted to integers
    return number

def convert_gps_coordinate(coordinate):
    # Remove the "deg" symbol from the coordinate
    coordinate = coordinate.replace("deg", "")
    # Split the coordinate into degrees, minutes, and seconds
    parts = coordinate.split(" ")
    print("parts", parts)

    # Extract the degrees, minutes, and seconds values
    degrees = float(parts[0])
    minutes_raw = (parts[2][:-1])
    minutes = float(minutes_raw.replace("'", ""))
    seconds_raw = (parts[3][:-1])
    seconds = float(seconds_raw.replace("'", "").replace('"', ""))

    # Calculate the decimal value
    decimal = round(degrees + (minutes / 60) + (seconds / 3600), 5)
    #decimal = round(degrees + (minutes / 60) + (seconds / 3600), 7)

    # Check if the coordinate is in the southern or western hemisphere and negate the decimal value accordingly
    if parts[4] == "S" or parts[3] == "W":
        decimal = -decimal

    return decimal

def calculate_time_difference(time1, time2, num_points):
    dt1 = datetime.datetime.strptime(time1, "%Y-%m-%dT%H:%M:%S.%fZ")
    dt2 = datetime.datetime.strptime(time2, "%Y-%m-%dT%H:%M:%S.%fZ")
    time_diff = (dt2 - dt1).total_seconds()
    time_increment = time_diff / num_points
    return time_increment

def extract_partitions(text):
    partitions = []
    start_index = 0
    while True:
        start_index = text.find("GPS Date Time", start_index)
        if start_index == -1:
            break  # No more occurrences of "GPS Date Time" exit the loop
        
        end_index = text.find("GPS Date Time", start_index + 1)
        if end_index == -1:
            break  # Closing "GPS Date Time" not found, exit the loop
        
        partition = text[start_index:end_index]  # Extract the partition between the start and end index
        partitions.append(partition)
        start_index = end_index - len("GPS Date Time")  # Move the start_index to the next position
        print(start_index)

    return partitions

def create_gpx(source_file):
    file_name = source_file.split('\\')[-1]
    file_name = file_name[:file_name.rfind('.')]
    path_to_rdd = get_RDD_Path()
    gpx_file_path = f'{path_to_rdd}report\\reportdata\\{file_name}.gpx'
    temp_gpx_file_path = f'{path_to_rdd}report\\reportdata\\{file_name}.txt'
    print (gpx_file_path)
    #exiftool_command = [f'{path_to_rdd}tools\\exiftool.exe' , f'{source_file}', '-ee', temp_text_file]
    #exiftool_command = [f'{path_to_rdd}tools/exiftool.exe', source_file, '-ee' , temp_gpx_file]
    with open(temp_gpx_file_path , 'w') as temp_gpx_file :
        exiftool_command = [f'{path_to_rdd}tools\\exiftool.exe' , f'{source_file}' , '-ee', f'{path_to_rdd}tools\\gpx.fmt']
        #Run the exiftool command to generate the XML output
        subprocess.run(exiftool_command,stdout = temp_gpx_file , check=True)
        #subprocess.run(exiftool_command, shell=True, check=True)

    # Write modified data to a new GPX file
    with open(gpx_file_path , 'w') as gpx_file:
        gpx_file.write('<?xml version="1.0" encoding="utf-8"?>\n')
        gpx_file.write('<gpx version="1.0"\n creator="ExifTool 12.06"\n xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n '
               'xmlns="http://www.topografix.com/GPX/1/0"\n xsi:schemaLocation="http://www.topografix.com/GPX/1/0 '
               'http://www.topografix.com/GPX/1/0/gpx.xsd">\n')
        gpx_file.write('<trk>\n<number>1</number>\n<trkseg>\n')

    # Read the XML output file
    with open(temp_gpx_file_path , 'r') as temp_gpx_file:
        #xml_data = temp_gpx_file.readlines()
        xml_data = str(temp_gpx_file.read())
        print("xml_data", xml_data)
    
    # Extract GPS Latitude, Longitude, and Time
    latitude = []
    transformed_latitude = []
    longitude = []
    transformed_longitude = []
    elevation = []
    time = []
    partition = []


    partitions = extract_partitions(xml_data)
    print("partitions", partitions)
    # Iterate over the lines in the file
    for partition in partitions:
        gps_date_time_start = partition.find("GPS Date Time")
        print("gps_date_time_start", gps_date_time_start)
        if gps_date_time_start != -1:
            line_end = partition.find("\n", gps_date_time_start)  # Find the end of the line
            print("line_end", line_end)
            if line_end != -1:
                time_start = gps_date_time_start + partition[gps_date_time_start:].index(':') + 2
                time = partition[time_start:line_end].strip()  # Extract the time value until the end of the line
                print(f"GPS Date Time: {time}")
                time_section = time  # Store the GPS Date Time for the section
                # Extract the time using regular expressions
                pattern = r"(\d{4}):(\d{2}):(\d{2}) (\d{2}):(\d{2}):(\d{2})\.(\d{3})"
                match = re.search(pattern, time_section)
                hours = match.group(4)
                print("match.group(4)", match.group(4))
                minutes = match.group(5)
                print("match.group(5)", match.group(5))
                seconds = match.group(6)
                print("match.group(6)", match.group(6))
                milliseconds = float(match.group(7))
                print("match.group(7)", match.group(7))
                # Extract the date using regular expressions
                year = match.group(1)
                print("date_match.group(1)", match.group(1))
                month = match.group(2)
                print("date_match.group(2)", match.group(2))
                day = match.group(3)
                print("date_match.group(3)", match.group(3))



        gps_latitude_starts = [idx for idx in range(len(partition)) if partition.startswith("GPS Latitude", idx)]
        print("gps_latitude_starts", gps_latitude_starts)
        gps_longitude_starts = [idx for idx in range(len(partition)) if partition.startswith("GPS Longitude", idx)]
        print("gps_longitude_starts", gps_longitude_starts) 
        gps_elevation_starts = [idx for idx in range(len(partition)) if partition.startswith("GPS Altitude", idx)]
        print("gps_elevation_starts", gps_elevation_starts)       

        for j, gps_latitude_start in enumerate(gps_latitude_starts):
            line_end = partition.find("\n", gps_latitude_start)  # Find the end of the line
            if line_end != -1:
                latitude_start = gps_latitude_start + partition[gps_latitude_start:].index(':') + 2
                latitude = partition[latitude_start:line_end].strip()  # Extract the latitude value until the end of the line
                transformed_latitude = convert_gps_coordinate(latitude)
                #print(f"GPS Latitude: {transformed_latitude[j]}")      

                gps_longitude_start = gps_longitude_starts[j]  # Get the corresponding longitude start index
                line_end = partition.find("\n", gps_longitude_start)  # Find the end of the line
                if line_end != -1:
                    longitude_start = gps_longitude_start + partition[gps_longitude_start:].index(':') + 2
                    longitude = partition[longitude_start:line_end].strip()  # Extract the longitude value until the end of the line
                    transformed_longitude = convert_gps_coordinate(longitude)
                    #print(f"GPS Longitude: {transformed_longitude[j]}")

                gps_elevation_start = gps_elevation_starts[j]  # Get the corresponding elevation start index
                line_end = partition.find("\n", gps_elevation_start)  # Find the end of the line
                if line_end != -1:
                    elevation_start = gps_elevation_start + partition[gps_elevation_start:].index(':') + 2
                    elevation = partition[elevation_start:line_end].strip()  # Extract the longitude value until the end of the line
                    #print(f"GPS altitude: {elevation}")
                    elevation = elevation.rstrip('m')  # Remove 'm' from the end of the string


                with open(gpx_file_path , 'a') as gpx_file:
                    gpx_file.write(f'<trkpt lat="{transformed_latitude}" lon="{transformed_longitude}">\n')
                    gpx_file.write(f'  <ele>{elevation}</ele>\n')
                    gpx_file.write('</trkpt>\n')  # Move the closing </trkpt> tag here

                    # Extract the gps resolution according to the camera model
                    gps_resolution = extract_gps_resolution()

                    # Calculate the updated milliseconds
                    milliseconds += gps_resolution * (j-1) / 1000  # Divide by 1000 to convert to seconds



                    # Adjust seconds if the total milliseconds exceed 999
                    if milliseconds >= 1:
                        additional_seconds = int(milliseconds)
                        milliseconds -= additional_seconds
                        seconds = str(int(seconds) + additional_seconds).zfill(2)

                    # Format the updated milliseconds with leading zeros
                    updated_milliseconds = str(int(milliseconds * 1000)).zfill(3)

                    # Construct the updated date-time string
                    updated_date_time = f"{year}-{month}-{day}T{hours}:{minutes}:{seconds}.{updated_milliseconds}Z"
                    with open(gpx_file_path , 'a') as gpx_file:
                        if j !=0:
                            gpx_file.write(f'  <time>{updated_date_time}</time>\n')

    

    # Write modified data to a new GPX file
    with open(gpx_file_path, 'a') as gpx_file:
        gpx_file.write('</trkseg>\n</trk>\n</gpx>')



def getMetadata(source_file): 
    path_to_rdd = get_RDD_Path()
    exiftool_path = f'{path_to_rdd}tools\\exiftool.exe'
    result = subprocess.check_output([exiftool_path, source_file, '-lat', '-lon', '-ee']) 
    result_str = result.decode('utf8') 
    result_by_line = result_str.split("\r\n") 
    file_properties = dict()
    print(result_by_line) # added by basem
 
    for one_line in result_by_line: 
        key_value = one_line.split(": ") 
        if len(key_value) == 2: 
            key_value[0] = key_value[0].rstrip() 
            file_properties[key_value[0]] = key_value[1] 
    print(file_properties)
    return file_properties 
