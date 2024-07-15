
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
formatted_timestamp = current_time.strftime("%Y%m%d%H%M%S")
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
        report_name = "A01_Concluding_report.pdf"

    # Build the full report file path
    report_path = os.path.join(report_directory, report_name)

    # Create a PDF file
    c = canvas.Canvas(report_path, pagesize=letter)

    # Setting the font of TITLE
    ################################################################
    c.setFont("Helvetica", 16)

    c.drawString(50, 750, "CONCLUSION")

    # Write in the body of the Second TITLE
    ################################################################
    c.setFont("Helvetica", 13)

    text = f'This is used to summarize the conclusions of this calculation.'
    c.drawString(50, 715, text)
    text = 'The conclusion represents the results of this calculation.'
    c.drawString(50, 675, text)

    # Setting the font of 1st RESULTS
    ################################################################
    c.setFont("Helvetica", 16)

    c.drawString(50, 625, "Spectrum Tendencies")
    # Input Image
    image_path = (r"D:\PythonFunctionLab\DetectionSourceCalibration"
                  r"\DecSourceDataAnalysis\Camera1140_20231010\20231010172517"
                  r"\01_Original_Spectrum_Tendencies_20231010172517.png")  # 替换为你的图片文件路径
    image = ImageReader(image_path)
    c.drawImage(image, 100, 350, width=450, height=270)  # 调整位置和大小

    # Setting the font of 2nd RESULTS
    ################################################################
    c.setFont("Helvetica", 16)

    c.drawString(50, 330, "Interp Spectrum Tendencies")

    # Input Image
    image_path = (r"D:\PythonFunctionLab\DetectionSourceCalibration"
                  r"\DecSourceDataAnalysis\Camera1140_20231010\20231010172517"
                  r"\03_Interp_Spectrum_Tendencies_20231010172517.png")  # 替换为你的图片文件路径
    image = ImageReader(image_path)
    c.drawImage(image, 125, 50, width=400, height=270)  # 调整位置和大小


    # Create New page
    c.showPage()

    # Setting the font of 3th RESULTS
    ################################################################
    c.setFont("Helvetica", 16)

    c.drawString(50, 740, "Monarch Power Distribution After Normalization")

    image_path = (r"D:\PythonFunctionLab\DetectionSourceCalibration"
                  r"\DecSourceDataAnalysis\Camera1140_20231010\20231010172517"
                  r"\04_Monarch_Power_Distribution_After_Normalization_20231010172517.png")  # 替换为你的图片文件路径
    image = ImageReader(image_path)
    c.drawImage(image, 100, 420, width=450, height=300)  # 调整位置和大小

    # Setting the font of 4th RESULTS
    ################################################################
    c.setFont("Helvetica", 16)

    c.drawString(50, 390, "Data Information")

    c.setFont("Helvetica", 12)
    xls_path = (r'D:\PythonFunctionLab\DetectionSourceCalibration'
                r'\DecSourceDataAnalysis\Camera1140_20231010\20231010172517'
                r'\05_DataInfo_20231010170046.xlsx')

    excel_data = pd.read_excel(xls_path)  # Excel file path
    data_as_np_array = excel_data.values
    data_as_np_array = data_as_np_array.tolist()
    dataHead = ['CWL_mean', 'CWL_Wanted', 'CWL_Peakwave', 'FWHM', 'Data_DiffCWL']
    data_as_np_array.insert(0, dataHead)
    # print(data_as_np_array)
    num_rows = len(data_as_np_array)
    num_cols = len(data_as_np_array[0])
    # print(data_as_np_array[0][0])
    x_position = 50
    y_position = 340

    # 设置矩形框的大小
    box_width = 100
    box_height = 20

    for row in range(num_rows):
        for col in range(num_cols):
            cell_data = str(data_as_np_array[row][col])
            # 绘制矩形框
            c.rect(x_position, y_position, box_width, box_height)
            # 将数据放入矩形框中
            c.drawString(x_position + 5, y_position + 5, cell_data)
            x_position += 100  # 调整列之间的距离
        y_position -= 20  # 调整行之间的距离
        x_position = 50  # 重置列位置

    # 保存PDF文件
    c.save()

    print(f"报告已生成并保存到 {report_path}")

# # 运行GUI主循环
# root.mainloop()
