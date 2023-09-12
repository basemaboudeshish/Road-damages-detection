from fpdf import FPDF
import datetime
import pytz
import os
from tabulate import tabulate
import pandas as pd
import dataframe_image as dfi
import os
from get_path_to_main_folder import get_RDD_Path
from natsort import natsorted
import sys
import re

#import foldername

def create_report(source_path):
    title = "Road Damage Detection Report"

    class PDF(FPDF):
        def header(self):
            #logo
            self.image(f'{dirname}\\THD-Logo-CSP-Software.jpg', 10, 8, 35)
            # (x_position, y_position, width, height)
            # if we just set the width, height will be set automatically
            # without changing the ratio

            # font
            self.set_font('helvetica', 'B', 20)
            # Calculating width of title and position
            title_w = self.get_string_width(title) + 6
            doc_w = self.w
            self.set_x((doc_w - title_w) / 2)
            # set colors of frame, background, and text
            self.set_draw_color(0, 80, 180) # RGB, border = Blue
            self.set_fill_color(230, 230, 0) # Background color = Yellow
            self.set_text_color(220, 50, 50) # Text Color = Red
            # Thickness of border (frame)
            self.set_line_width(1)
            # Title
            self.cell(title_w, 10, title, border=True, ln=True, align='C', fill=True)
            # align='C' meaning allign in the center

            #line break
            self.ln(10)
        


        def footer(self):
            # set position of footer
            self.set_y(-15) # 15mm from the bottom
            # set font
            self.set_font('helvetica', 'I', 8) #10 is font size
            # set font color
            self.set_text_color(169, 169, 169) # grey
            # page number
            self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align='C')
        

        # Chapter Title
        def chapter_title(self, ch_num, ch_title):
            # set font
            self.set_font('helvetica', '', 12)
            # set color
            self.set_fill_color(200, 220, 255)
            # chapter title
            chapter_title = f'Image frame {ch_num}'
            #chapter_title = f'Segment {ch_num}'
            self.cell(0, 5, chapter_title, ln=True, fill=True)
            #line break
            self.ln()

        
        # Cover page company name
        def company_name(self, name):
            with open(name, 'rb') as fh:
                company_name_txt = fh.read().decode('UTF-8')
                company_name_txt1 = "Company Name : " + company_name_txt 
            #set font
            self.set_font('times', '', 12)
            # insert text
            self.multi_cell(0, 5, company_name_txt1)
            # line break
            self.ln()
        
        
        def create_table(self, lst):
            df = pd.DataFrame(lst, index = ['Linear Crack', 'Alligator Crack', 'Pothole', 'White Line'], columns=['Count'])
            dfi.export(df, "my_table.png")

        def print_table(self, name):
            self.ln(5)
            self.cell(0, 5, "Total Count of Distresses : ")
            self.ln()
            self.image(name, w = 50)
            self.ln()

        def print_drivepicture(self, name):
            self.ln(5)
            self.cell(0, 5, "Route of this Drive : ")
            self.ln()
            self.image(name, w = 195)
            self.ln()

        def print_seg_count(self, count):
            self.ln(5)
            buffer = "Total Amount of Segments : " + str(count)
            self.cell(0, 5, buffer)
            self.ln()
            self.cell(0, 5, "(The segments without distress detection will not be shown below in the report)")
            self.ln()


        # Cover page date and time
        def date_time(self):
            tz_DE = pytz.timezone('Europe/Amsterdam')
            current_date_time = datetime.datetime.now(tz_DE).strftime("%d.%m.%Y, %H:%M:%S")
            current_date_time1 = "Recorded Date and Time : " + current_date_time
            # set font
            self.set_font('times', '', 12)
            # insert text
            self.multi_cell(0, 5, current_date_time1)
            # line break
            self.ln()

        # Chapter content
        def chapter_body(self, name1, name2, distress_img):
            self.image(distress_img, 20, 50, 0, 100)
            # read txt file
            with open(name1, 'r') as fh:
                txt1 = fh.read()
            with open(name2, 'r') as fh:
                txt2 = fh.read()
            # set font
            self.set_font('times', '', 12)
            # insert text
            self.ln(120)
            self.set_x(20)
            self.cell(60, 5, "Distress detected in this segment : ", border = True)
            self.ln(5)
            self.set_x(20)
            self.multi_cell(0, 5, txt1, ln = True, align = "L")
            self.ln(10)
            self.set_x(20)
            self.cell(47, 5, "Location of this segment : ", border = True)
            self.ln(5)
            self.set_x(20)
            self.multi_cell(0, 5, txt2, ln = True, align = "L")
            # line break
            self.ln()
            # end of chapter
            self.set_font('times', 'I', 12)
            #self.cell(0, 5, '--------------------------------------------------------------------------------', align = "")

        def print_chapter(self, ch_num, ch_title, name1, name2, distress_img):
            self.add_page()
            self.chapter_title(ch_num, ch_title)
            self.chapter_body(name1, name2, distress_img)


    # create FPDF object
    # Layout ('P','L')
    # Unit ('mm', 'cm', 'in')
    # Format ('A3', 'A4' (Default), 'A5', 'Letter', 'Legal', (100,50))
    pdf = PDF('P', 'mm', 'Letter')

    # get total page numbers
    pdf.alias_nb_pages()

    # Set Auto Page Break
    pdf.set_auto_page_break(auto=True, margin = 15)
    # margin is how far away from the bottom of the page

    dirname = f'{get_RDD_Path()}report'

    # Add a page
    pdf.add_page()

    # company name cover page
    pdf.company_name(dirname + '\\reportdata\\frontpage\\CompanyName.txt')


    seg_path = []
    for root, dirs, files in os.walk(dirname + "\\reportdata"):
        for i in dirs:
            if i.startswith("S"):
                seg_path.append(os.path.join(root, i))
    seg_path = natsorted(seg_path)
    ######print('seg_path', seg_path)##### 

    dis_img_path = []
    for j in seg_path:
        #os.walk(j)
        for root, dirs, files in os.walk(j):
            for file in files:
                if file.startswith("frame"):
                    bs = "\\"
                    dis_img_path.append(bs.join((root, file)))
    #####print('dis_img_path', dis_img_path)##### 

    dis_loc_path = []
    for j in seg_path:
        #os.walk(j)
        for root, dirs, files in os.walk(j):
            for file in files:
                if file.startswith("location"):
                    bs = "\\" 
                    dis_loc_path.append(bs.join((root, file)))
    #####print('dis_loc_path', dis_loc_path)##### 

    dis_count_path = []
    for loc_file in dis_loc_path:
        segment_path = "\\".join(loc_file.split("\\")[:-1])  # Extract the segment path from the location file
        for root, dirs, files in os.walk(segment_path):
            for file in files:
                if file.startswith("info"):
                    bs = "\\"
                    dis_count_path.append(bs.join((root, file)))
    ####print('dis_count_path', dis_count_path)##### #


    fp_table = [0,0,0,0]
    with open(dirname + '\\reportdata\\frontpage\\info.txt', 'rb') as fh:
        buffer = fh.read().decode('UTF-8')
        buffer1 = buffer.strip("[")
        buffer2 = buffer1.strip("]")
        fp_table = buffer2.split(",")


    distress_count_front_page = [fp_table[0], fp_table[1], fp_table[2], fp_table[3]]
    pdf.create_table(distress_count_front_page)
    pdf.print_table('my_table.png')


    seg_count = len(seg_path)
    pdf.print_seg_count(seg_count)

    pdf.print_drivepicture(dirname + '\\reportdata\\frontpage\\drivepicture.png')

    # date and time cover page
    pdf.date_time()



    segment_number = 1  # Default value if segment number is not found
    j = 0
    for i in dis_loc_path:
        if j < len(dis_loc_path):
            x = i[i.find('Segment')+7:] # finds the number of the segment which he is inside
            x = x[:x.rfind('.')]
            x = x[x.find('\\')+1:]  # removes the segment and slash part from location
            match = re.search(r'Segment(\d+)\\', i)
            if match:
                segment_number = int(match.group(1))
            y = []
            #####print('y', y)##### # 
            z = dis_img_path[j]
            ######print('z', z)####### # 
            v = dis_count_path[j]
            ######3print('v', v)###### #
            h = dis_loc_path[j]
            #####print('h', h)##### # 
            pdf.print_chapter(x, y, v, h, z)
            j += 1


    file_name = source_path.split('\\')[-1]
    file_name = file_name[:file_name.rfind('.')]

    #output
    pdf.output(f'{dirname}\\report_{file_name}.pdf')
    print('report is ready')
    sys.exit()
