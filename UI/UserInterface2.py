from cProfile import label
from inspect import ArgSpec
from pickle import TRUE
from tkinter import W, Button, Variable
from ast import Pass, arg
from cgitb import text
from ctypes.wintypes import SIZE
from msilib.schema import File
from re import MULTILINE
from smtplib import SMTPAuthenticationError
from tkinter import Widget
from tkinter.font import ITALIC
from turtle import onkeypress, onscreenclick
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.base import runTouchApp
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.lang import Builder
from PyQt5 import QtCore
from kivy.factory import Factory
from kivy.properties import ObjectProperty,NumericProperty,StringProperty
from kivy.uix.popup import Popup
from functools import partial
from kivy.factory import Factory
import sys
from run_yolo import run_rdd
import time
import cv2
import os
from move_report_data import run_yolo_and_generate_report
from get_path_to_main_folder import get_RDD_Path



Builder.load_string('''
#:kivy 1.10.0


<SaveFile>

    title: 'Save File'
    auto_dismiss: False

    # FileChooserLayout
    GridLayout:
        cols:1   
        # ButtonArea
        GridLayout:
            cols:1
            spacing: 50
            size_hint: (.5,.5)
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}

            TextInput:
                id: file_path
                size_hint: (.09,.09)
            
            FileChooserIconView:
                id:filechooser
                on_selection: 
                    file_path.text = self.selection and self.selection[0]
                dirselect: True
 
        Button:
            text: "Save and continue"
            size_hint: (.09,.09)
            on_press:
                root.Getthepath(file_path.text)
                root.dismiss()

<RootWidget>:


''')

class SaveFile(Popup):
    def Getthepath(self,filepath):
        global Latestpath
        Latestpath=str(filepath)
        print("path",Latestpath)
        
    
class RootWidget(GridLayout):
    
    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        filepop = SaveFile()
        filepop.open()

#Saving path for the generated Infor

save_path = f'{get_RDD_Path()}report'
      
class UserInterface (App):
    empty2 = Label()  # Add the empty2 attribute
        
    def build(self):
        self.window = GridLayout()
        self.window.cols = 1
        self.window.size_hint = (0.8, 0.8)
        self.window.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        # Add widgets to window
        
        # Welcome
        self.greeting = Label(text="Welcome to Road Detection Project",
                              font_size=40, color='#25a9e8', bold=True, italic=True)
        self.window.add_widget(self.greeting)

        # Company Info
        self.Info = Label(text="Enter your company name", font_size=18,
                          color='#25a9e8', size_hint=(1, 0.4), halign='left', valign='top')
        self.window.add_widget(self.Info)

        self.user = TextInput(
            hint_text='Company', multiline=False, size_hint=(1, 0.3), padding_y=(5, 5))
        self.window.add_widget(self.user)


        # Select the camera model
        self.Info2 = Label(text="Select the camera model",
                           font_size=18, color='#25a9e8', size_hint=(1, 0.4))
        self.window.add_widget(self.Info2)

        # Select the Camera model
        self.spinner2 = Spinner(
            # default value shown
            text='Camera model',
            #available values
            values=("GoPro HERO9", "GoPro HERO10"),
            # just for positioning in our example
            size_hint=(0.1, None),
            size=(100, 40),
            pos_hint={'center_x': 0.5, 'center_y': 0.5})
        
        self.window.add_widget(self.spinner2)

        
        Cond1=False

        # Select the video file
        self.Info3 = Label(text="Select the video file",
                           font_size=18, color='#25a9e8', size_hint=(1, 0.4))
        self.window.add_widget(self.Info3)
        
        #Select folder button
        self.button3=Button(text='Load',size_hint=(1, 0.4),disabled =Cond1)
        self.button3.bind(on_press=self.callback2)
        self.window.add_widget(self.button3)


        # Sign In
        self.button = Button(text="Save and Start the detection", size_hint=(
            1, 0.4), bold=True, font_size=16, background_color='#25a9e8')
        self.button.bind(on_press=self.callback)
        self.button.bind(on_release=self.callback3)
        self.window.add_widget(self.button)

        return self.window
     
         
    def callback(self, instance):
        self.text = "Thanks "+self.user.text + \
                " for choosing our model,the prediction will start soon"
        completeName = os.path.join(save_path, 'Company.txt')
        file1 = open(completeName, "w")
        file1.write(self.user.text)

        if self.spinner2.text == "GoPro HERO9":
            self.empty2.text = self.spinner2.text + ":55.56"
        else:
            self.empty2.text = self.spinner2.text + ":100.0"
        completeName2 = os.path.join(save_path, 'Camera_model.txt')
        file2 = open(completeName2, "w")
        file2.write(self.empty2.text)

        

 
    def callback2(self,instance):
        return RootWidget()                                 
        
    def callback3(self, instance):
        run_yolo_and_generate_report(Latestpath) 
   
if __name__ == "__main__":
    UserInterface().run()