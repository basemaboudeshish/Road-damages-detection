import os
import subprocess 
import runpy
import configuration.config as config
from get_path_to_main_folder import get_RDD_Path

def run_rdd(source_file_path, detection_mode = None):

    path_to_Yolo_folder = f'{get_RDD_Path()}yolov5'

    weights = config.weights
    imgagesize = config.imgagesize
    confidence = config.confidence

    detect_file_path = f'{path_to_Yolo_folder}\detect2.py'
    weights_file_path = f'{path_to_Yolo_folder}\weights\\{weights}'

    if detection_mode == 'Live mode':
        source_file_path = 0
    os.chdir(path_to_Yolo_folder)
    command = f'python "{detect_file_path}" --weights "{weights_file_path}" --img {imgagesize} --conf {confidence} --source "{source_file_path}" --save-txt --save-crop --project RDD --view-img'
    print(f'python "{detect_file_path}" --weights "{weights_file_path}" --img {imgagesize} --conf {confidence} --source "{source_file_path}" --save-txt --save-crop')
    os.system(command)
