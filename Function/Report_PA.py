
################################################################
# This script is used to create reports
#
# - Input information
#    1. The folder in which to run
#    2. Information about the images covered by the report
#
# - Output information
#    1、Report pdf
#
# Author: Jerome. Date: 2023/10/11
################################################################


import os
import tkinter as tk
from tkinter import filedialog
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import re
import datetime
import pandas as pd



# 获取当前日期和时间
current_time = datetime.datetime.now()
# 格式化时间戳，去掉中间的符号，并保留到秒级别的时间精度
formatted_timestamp = current_time.strftime("%Y%m%d")
print('Time is ', formatted_timestamp)

# Creating a GUI window
root = tk.Tk()
root.withdraw()  # Hide main window

# Prompts the user to select the report save path
report_directory = filedialog.askdirectory()
if not report_directory:
    print("Save path not selected")
else:
    # Rename the File
    if 'Camera' in report_directory:
        pattern = r'Camera(\d+_\d+)'
        match = re.search(pattern, report_directory)
        result = 'Camera' + match.group(1)
        # Specify the report file name
        report_name = 'A01_' + result + "_report.pdf"
    else:
        report_name = 'A01_Concluding_report.pdf'

    # Build the full report file path
    report_path = os.path.join(report_directory, report_name)

    # Create a PDF file
    c = canvas.Canvas(report_path, pagesize=letter)

    N = 750
    delta = 30
    # Setting the font of TITLE
    ################################################################
    c.setFont("Helvetica-Bold", 18)

    c.drawString(50, N - 0 * delta, "Concluding Report")

    c.setFont("Helvetica", 14)
    c.drawString(50, N - 1 * delta, ("Date : " + formatted_timestamp))

    # Write in the body of the Second TITLE
    ################################################################
    c.setFont("Helvetica", 13)
    text = f'Conclusion report of the simulation of the omnidirectional lens.'
    c.drawString(50, N - 2 * delta, text)

    c.setFont("Helvetica-Bold", 15)
    text = 'Attention'
    c.drawString(50, N - 3 * delta, text)

    c.setFont("Helvetica", 13)
    text = '- The vertical direction corresponds to the horizontal scanning direction of the system.'
    c.drawString(50, N - 4 * delta, text)
    text = '- The horizontal direction corresponds to the vertical scanning direction of the system.'
    c.drawString(50, N - 5 * delta, text)

    ################################################################
    c.setFont("Helvetica-Bold", 15)
    text = 'System Overview'
    c.drawString(50, N - 6 * delta, text)

    c.setFont("Helvetica", 13)
    text = '- Summarize the characteristics of the system'
    c.drawString(50, N - 7 * delta, text)

    c.setFont("Helvetica", 13)
    text = '- Optical Path Volume of The System :  [ 84mm × 49mm × 98mm ]'
    c.drawString(50, N - 8 * delta, text)

    c.setFont("Helvetica", 13)
    text = '- Model of light source :  [   SPL S1L90H_3   ]'
    c.drawString(50, N - 9 * delta, text)

    c.setFont("Helvetica", 13)
    text = '- Transmit and receive using transceiver coaxial optical paths'
    c.drawString(50, N - 10 * delta, text)

    c.setFont("Helvetica-Bold", 15)
    text = 'System revision point : '
    c.drawString(50, N - 11 * delta, text)

    c.setFont("Helvetica", 13)
    text = '- Correcting the structural parameters of omnidirectional lenses '
    c.drawString(50, N - 12 * delta, text)

    text = '- Folding of the optical path of the emitting section using mirrors '
    c.drawString(50, N - 13 * delta, text)

    text = '- The TX light path is divided into two parts '
    c.drawString(50, N - 14 * delta, text)

    text = '- The optical path before the reflector is strictly collimated '
    c.drawString(50, N - 15 * delta, text)

    text = '- FAC-compensated lens and SAC-compensated lens after reflector '
    c.drawString(50, N - 16 * delta, text)

    text = '- Two sets of compensating lenses for aberration '
    c.drawString(50, N - 17 * delta, text)

    text = '- The source of the aberration is the omnidirectional lens '
    c.drawString(50, N - 18 * delta, text)

    # Create New page
    c.showPage()

    # Setting the font of 1st RESULTS
    ################################################################
    c.setFont("Helvetica-Bold", 15)

    c.drawString(50, N - 0.5 * delta, "System 3D Layout")
    # # Input Image
    image_path = (r"E:\02_Solutions\Someones\PA\Engineering Implementation Solutions"
                  r"\Cone_Variant_Solutions\ZMX_System\03_DataInfo\SetupData_up"
                  r"\AngleData_TX_Aper_5×2\InfoResponse\SystemOverview.jpg")  # 替换为你的图片文件路径
    image = ImageReader(image_path)
    c.drawImage(image, 100, 265, width=450, height=400)  # 调整位置和大小

    # Create New page
    c.showPage()

    # Setting the font of 2nd RESULTS
    ################################################################
    c.setFont("Helvetica-Bold", 15)

    c.drawString(50, N - 0.5 * delta, 'System Scan Angle')

    # Input Image
    image_path = (r"E:\02_Solutions\Someones\PA\Engineering Implementation Solutions\Cone_Variant_Solutions"
                  r"\ZMX_System\03_DataInfo\SetupData_up\AngleData_TX_Aper_5×2\InfoResponse\系统扫描角度.jpg")  # 替换为你的图片文件路径
    image = ImageReader(image_path)
    c.drawImage(image, 100, 415, width=400, height=300)  # 调整位置和大小

    # # Setting the font of 3th RESULTS
    # ################################################################

    c.drawString(50, 370, "Energy Efficiency of System Output")

    image_path = (r"E:\02_Solutions\Someones\PA\Engineering Implementation Solutions\Cone_Variant_Solutions\ZMX_System\03_DataInfo\SetupData_up\AngleData_TX_Aper_5×2\InfoResponse\系统出射能效.jpg")  # 替换为你的图片文件路径
    image = ImageReader(image_path)
    c.drawImage(image, 100, 50, width=400, height=300)  # 调整位置和大小


    # Create New page
    c.showPage()

    # Setting the font of 4th RESULTS
    ################################################################
    c.setFont("Helvetica-Bold", 15)

    c.drawString(50, N - 0.5 * delta, 'Horizontal divergence angle change')

    # Input Image
    image_path = (r"E:\02_Solutions\Someones\PA\Engineering Implementation Solutions\Cone_Variant_Solutions\ZMX_System\03_DataInfo\SetupData_up\AngleData_TX_Aper_5×2\InfoResponse\水平方向发散角变化.jpg")  # 替换为你的图片文件路径
    image = ImageReader(image_path)
    c.drawImage(image, 100, 415, width=400, height=300)  # 调整位置和大小

    # Setting the font of 5th RESULTS
    ################################################################

    c.drawString(50, 370, "Vertical divergence angle change")

    image_path = (r"E:\02_Solutions\Someones\PA\Engineering Implementation Solutions\Cone_Variant_Solutions\ZMX_System\03_DataInfo\SetupData_up\AngleData_TX_Aper_5×2\InfoResponse\垂直方向发散角变化.jpg")  # 替换为你的图片文件路径
    image = ImageReader(image_path)
    c.drawImage(image, 100, 50, width=400, height=300)  # 调整位置和大小

    # Create New page
    c.showPage()

    # Setting the font of 6th RESULTS
    ################################################################
    c.setFont("Helvetica-Bold", 15)

    c.drawString(50, N - 0.5 * delta, 'System Scanning Spot')

    # Input Image
    image_path = (r"E:\02_Solutions\Someones\PA\Engineering Implementation Solutions\Cone_Variant_Solutions\ZMX_System\03_DataInfo\SetupData_up\AngleData_TX_Aper_5×2\InfoResponse\系统扫描光斑.jpg")  # 替换为你的图片文件路径
    image = ImageReader(image_path)
    c.drawImage(image, 250, 225, width=100, height=500)  # 调整位置和大小

    # Create New page
    c.showPage()

    c.setFont("Helvetica-Bold", 15)

    c.drawString(50, N - 0.5 * delta, 'System Dispersion Angle Information')

    c.setFont("Helvetica", 10)
    xls_path = (r'E:\02_Solutions\Someones\PA\Engineering Implementation Solutions\Cone_Variant_Solutions\ZMX_System\03_DataInfo\SetupData_up\AngleData_TX_Aper_5×2\InfoResponse\SystemData.xlsx')

    excel_data = pd.read_excel(xls_path)  # Excel file path
    data_as_np_array = excel_data.values
    data_as_np_array = data_as_np_array.tolist()
    dataHead = ['OPA Angle/°', 'System Angle/°', 'System Vertical Angle/°', 'System horizontal Angle/°']
    data_as_np_array.insert(0, dataHead)
    # print(data_as_np_array)
    num_rows = len(data_as_np_array)
    num_cols = len(data_as_np_array[0])
    # print(data_as_np_array[0][0])
    x_position = 50
    y_position = 670

    # 设置矩形框的大小
    box_width = 125
    box_height = 30

    for row in range(num_rows):
        for col in range(num_cols):
            cell_data = str(data_as_np_array[row][col])
            # 绘制矩形框
            c.rect(x_position, y_position, box_width, box_height)
            # 将数据放入矩形框中
            c.drawString(x_position + 5, y_position + 5, cell_data)
            x_position += 125  # 调整列之间的距离
        y_position -= 30  # 调整行之间的距离
        x_position = 50  # 重置列位置



    # 保存PDF文件
    c.save()

    print(f"报告已生成并保存到 {report_path}")

# # 运行GUI主循环
# root.mainloop()
