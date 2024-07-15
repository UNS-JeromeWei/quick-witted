import spectral
import matplotlib.pyplot as plt
import os
import numpy as np
from scipy import ndimage
import cv2
import math
import re
from scipy.signal import medfilt, savgol_filter
from lxml import etree
from scipy.interpolate import interp1d
from datetime import datetime
import time
from Function.envi import *
import json
import csv
import pandas as pd


def count_files_in_directory(directory_path):
    # Used to find available documents in a directory
    #
    # Input parameters:
    #   - directory_path: Folder to be analyzed
    #
    # Output parameters:
    #   - file_list : The list of files in the analysis directory which is available
    #   - wavelength_list : The list of wavelength which used to get the state cube
    #
    try:
        # Get a list of all files in a directory
        file_list_O = os.listdir(directory_path)
        T_file = []
        wavelength_list = []
        # Find a logical list of documents
        count = 0
        for i in range(0, len(file_list_O)):
            f_file_name = file_list_O[i]
            if f_file_name[:5] == 'state':
                T_file.append(i)
                wavelength_list.append(int(f_file_name[5:9])/10)
                count = count + 1
            elif f_file_name[:4] == 'cube':
                T_file.append(i)
                wavelength_list.append(int(f_file_name[5:9]) / 10)
                count = count + 1
        file_list = file_list_O[T_file[0] : T_file[-1]+1]
        return file_list, wavelength_list
    except OSError as e:
        print(f"Error accessing directory: {e}")
        return -1


def file_rawdata_element(foldername):
    # Find the raw data filename list
    file_list = os.listdir(foldername)
    return file_list

def centerpower(img, center_x, center_y):
    size = 100
    maxValue = 1023
    exposure_time = 250
    gain = 1
    sigma = 2
    K = 1
    filtersize = 2 * math.ceil(2 * K * sigma) + 1
    imginfo = cv2.GaussianBlur(img, (filtersize, filtersize), K * sigma,
                                           borderType=cv2.BORDER_REPLICATE)
    center_region = imginfo[center_x - size // 2: center_x + size // 2, center_y - size // 2: center_y + size // 2]
    total_sum = np.sum(center_region)/maxValue/exposure_time/gain/(100*100)
    return total_sum

def CollectAllBand(file_list, img, directory_path_n):
    AllBandPower = np.zeros((len(file_list), 10))

    for i in range(len(file_list)):
        file_name = (directory_path_n + "\\" + file_list[i])  # Double '\' Synthesis Path
        raw_file_name = file_rawdata_element(file_name)  # Determine the data of the document
        hdr_path = file_name + "\\" + raw_file_name[0]
        raw_path = file_name + "\\" + raw_file_name[1]

        img_Box = []
        A = np.zeros((10, 1))  # Build buffer for centerpower
        data = spectral.envi.open(hdr_path)
        sigma = 2
        K = 1
        for index, band in enumerate(data.bands.centers):
            imginfo = data.read_band(index)
            # img[:, :, index, i] = np.float32(imginfo)
            imginfo = np.float32(imginfo)
            filtersize = 2 * math.ceil(2 * K * sigma) + 1
            # img[:, :, index, i] = ndimage.gaussian_filter(imginfo, sigma)
            img[:, :, index, i] = cv2.GaussianBlur(imginfo, (filtersize, filtersize), K * sigma, borderType=cv2.BORDER_REPLICATE)

            center_x = imginfo.shape[0] // 2
            center_y = imginfo.shape[1] // 2
            power = centerpower(imginfo, center_x, center_y)  # Calculate center power
            A[index] = power

        ExposureTime = data.metadata["exposure time"][0]
        Gain = data.metadata["gain"][0]
        AllBandPower[i, :] = np.transpose(A)

    return img, AllBandPower, ExposureTime, Gain


def DealWithSpectrum(img, output_folder, wavelength_list, file_list):
    img_Cube = np.zeros((1024, 1280, 10)).astype(np.uint16)
    driftdata_Array = np.zeros((10, 5))
    # data_dtype = img_Cube.dtype
    # print("数据类型：", data_dtype)
    for j in range(10):
        img1 = img[:, :, j, :]
        img_single_rebuild = img1.reshape((1024 * 1280, len(file_list)))
        # Find the max value of each row
        max_values_Index_per_row = np.argmax(img_single_rebuild, axis=1)
        for i in range(len(max_values_Index_per_row)):
            max_values_Index_per_row[i] = wavelength_list[max_values_Index_per_row[i]]

        CWL_drift_dis = max_values_Index_per_row.reshape([1024, 1280])
        img_Cube[:, :, j] = CWL_drift_dis

        # 中心波长漂移的数据的核心位置
        column = 1024
        row = 1280
        step = 50

        # print(int(column/2-step), int(column/2+step), int(row/2-step) , int(row/2+step))

        driftdata_Array[j, 0] = np.mean(CWL_drift_dis[462 : 562, 590 : 690])
        driftdata_Array[j, 3] = np.mean(CWL_drift_dis[1024 - 100: -1, 0: 100])
        driftdata_Array[j, 2] = np.mean(CWL_drift_dis[1024 - 100: -1, 1280-100:-1])
        driftdata_Array[j, 1] = np.mean(CWL_drift_dis[0: 100, 1280-100: -1])
        driftdata_Array[j, 4] = np.mean(CWL_drift_dis[0: 100, 0: 100])

        CWL_drift_dis[462 : 562, 590 : 690] = 1000
        CWL_drift_dis[1024 - 100: -1, 0: 100] = 1000
        CWL_drift_dis[1024 - 100: -1, 1280-100:-1] = 1000
        CWL_drift_dis[0: 100, 1280-100: -1] = 1000
        CWL_drift_dis[0: 100, 0: 100] = 1000

        output_path = output_folder + "//" + f"image_{j}.png"
        plt.imshow(img_Cube[:,:,j])
        plt.axis('off')
        plt.colorbar()
        plt.savefig(output_path, bbox_inches='tight', pad_inches=0, dpi=300)
        plt.close()

    return img_Cube, driftdata_Array


def DealWithSpectrum_50pixel(img, output_folder, wavelength_list, file_list):
    img_Cube = np.zeros((1024, 1280, 10)).astype(np.uint16)
    driftdata_Array = np.zeros((10, 5))
    # data_dtype = img_Cube.dtype
    # print("数据类型：", data_dtype)
    for j in range(10):
        img1 = img[:, :, j, :]
        img_single_rebuild = img1.reshape((1024 * 1280, len(file_list)))
        # Find the max value of each row
        max_values_Index_per_row = np.argmax(img_single_rebuild, axis=1)
        for i in range(len(max_values_Index_per_row)):
            max_values_Index_per_row[i] = wavelength_list[max_values_Index_per_row[i]]

        CWL_drift_dis = max_values_Index_per_row.reshape([1024, 1280])
        img_Cube[:, :, j] = CWL_drift_dis

        # 中心波长漂移的数据的核心位置
        column = 1024
        row = 1280
        step = 50

        # print(int(column/2-step), int(column/2+step), int(row/2-step) , int(row/2+step))

        driftdata_Array[j, 0] = np.mean(CWL_drift_dis[462 : 562, 590 : 690])
        driftdata_Array[j, 3] = np.mean(CWL_drift_dis[1024 - 50: -1, 0: 50])
        driftdata_Array[j, 2] = np.mean(CWL_drift_dis[1024 - 50: -1, 1280-50:-1])
        driftdata_Array[j, 1] = np.mean(CWL_drift_dis[0: 50, 1280-50: -1])
        driftdata_Array[j, 4] = np.mean(CWL_drift_dis[0: 50, 0: 50])

        CWL_drift_dis[462 : 562, 590 : 690] = 1000
        CWL_drift_dis[1024 - 100: -1, 0: 100] = 1000
        CWL_drift_dis[1024 - 100: -1, 1280-100:-1] = 1000
        CWL_drift_dis[0: 100, 1280-100: -1] = 1000
        CWL_drift_dis[0: 100, 0: 100] = 1000

        output_path = output_folder + "//" + f"image_{j}.png"
        plt.imshow(CWL_drift_dis)
        plt.axis('off')
        plt.colorbar()
        plt.savefig(output_path, bbox_inches='tight', pad_inches=0, dpi=300)
        plt.close()

    return img_Cube, driftdata_Array



def find_max_value(matrix):
    max_value = None

    for row in matrix:
        for value in row:
            if max_value is None or value > max_value:
                max_value = value

    return max_value

def CreatDecSourceFolderpath(directory_path_n, SecondFoldername, formatted_timestamp):
    # 获取当前运行目录
    current_directory = os.getcwd()

    # 创建下级目录
    current_Second_directory = os.path.join(current_directory, SecondFoldername)
    # 检查文件夹是否已存在
    if not os.path.exists(current_Second_directory):
        # 创建文件夹
        os.makedirs(current_Second_directory)
        print(f"-> Folder '{SecondFoldername}' created at '{current_directory}'")
    else:
        print(f"-> Folder '{SecondFoldername}' already exists at '{current_directory}'")

    # 找到待分析目录的字符串
    pattern = r'Camera(\d+_\d+)'
    match = re.search(pattern, directory_path_n)
    result = 'Camera' + match.group(1)

    # 创建文件夹路径
    folder_path = os.path.join(current_Second_directory, result, formatted_timestamp)
    # 检查文件夹是否已存在
    if not os.path.exists(folder_path):
        # 创建文件夹
        os.makedirs(folder_path)
        print(f"-> Folder '{result}' created at '{folder_path}'")
    else:
        print(f"-> Folder '{result}' already exists at '{folder_path}'")

    return folder_path

def get_txt_files_in_directory(directory):
    txt_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".txt"):
                txt_files.append(os.path.join(root, file))
    return txt_files

def read_txt_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    lines_stripped = [line.strip() for line in lines]

    return lines_stripped


def find_txt_files(directory):
    txt_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".txt"):
                txt_files.append(os.path.join(root, file))
    return txt_files

def DenoiseSignal(signal):
    # 假设 signal 是一个 NumPy 数组
    signalOut = signal

    # 移除异常值
    median_filtered = medfilt(signal, kernel_size=11)
    TF = np.abs(signal - median_filtered) > 5
    signalOut[TF] = median_filtered[TF]

    # 去噪信号
    signalOut = savgol_filter(signalOut, window_length=19, polyorder=3)


    return signalOut


def curveTendency(directory_path_n):
    # Used to get the intermediate parameter from monochromator
    #
    # Input parameters:
    #   - directory_path_n : Folder to be analyzed which from monochromator
    #
    # Output parameters:
    #   - wavelength_List : 660~980 gap=5 array, form system calibration
    #   - max_intensity_List : Max value from each wavelength
    #   - indes_matrix : Index array mapping the available data in each file
    #   - wave_matrix : Wave array mapping the available data in each file
    #   - indices : Index mapping the available wavelength which is the same array of each file
    #

    if 'LabSphere' in directory_path_n:
        # 使用正则表达式提取LabSphere后面的所有字符串
        pattern = r'LabSphere_(.+)'  # (.+) 匹配一个或多个字符
        match = re.search(pattern, directory_path_n)
    else:
        pattern = r'Camera(\d+_\d+)'
        match = re.search(pattern, directory_path_n)

    txt_files = find_txt_files(directory_path_n)
    wavelength_List = []

    for i in range(len(txt_files)):
        file_name = directory_path_n  # Double '\' Synthesis Path
        txt_files = get_txt_files_in_directory(file_name)
        txt_file_lines = read_txt_file(txt_files[i])

        strmonodata = txt_file_lines[0]
        monomatch = re.search(r'Spectrum_(\d+)', strmonodata)
        number = monomatch.group(1)
        wavelength_List.append(int(number)/1)


        target_strings = [r'Number of Pixels in Spectrum:3648', r'Number of Pixels in Spectrum: 3648', r'Number of Pixels in Spectrum: 2048']
        matching_indices = np.isin(txt_file_lines, target_strings)
        matching_rows = np.where(matching_indices)[0]  # 行数是从1开始计数
        file_pixel_info = txt_file_lines[int(matching_rows)]
        pattern_info = r'Spectrum:\s*(\d+)'  # (.+) 匹配一个或多个字符
        match_data = re.search(pattern_info, file_pixel_info)
        spectrum_pixels = match_data.group(1)


    # AllBandPower = np.zeros((len(txt_files),10))
    wave_matrix = np.zeros((len(txt_files), int(spectrum_pixels)))
    indes_matrix = np.zeros((len(txt_files), int(spectrum_pixels)))
    smoothed_matrix_ = np.zeros((len(txt_files), int(spectrum_pixels)))

    max_intensity_List = []

    # 获取 SetUpCalibration 信息
    for i in range(len(txt_files)):
        file_name = directory_path_n  # Double '\' Synthesis Path
        txt_files = get_txt_files_in_directory(file_name)

        txt_file_lines = read_txt_file(txt_files[i])
        data_strings = txt_file_lines[14: -1]

        numeric_matrix = []
        for data_string in data_strings:
            parts = data_string.strip().split('\t')  # 分割字符串，去除多余的空白字符
            numeric_row = [float(part) for part in parts]  # 将字符串部分转换为浮点数
            numeric_matrix.append(numeric_row)  # 添加该行到矩阵

        for j in range(len(numeric_matrix)):
            wave_matrix[i, j] = numeric_matrix[j][0]
            indes_matrix[i, j] = numeric_matrix[j][1]

        # 对数据进行去噪处理
        # 降噪处理有好几部分
        # 1、Range 为 550nm ~ 1000 nm
        # 2、Value 为负数的直接赋 0
        # 3、不进行 Smooth 直接找 Peak 值，尽可能的保真
        # 4、能量包络 Threshold 按照 3% 衡量
        # 5、能量包络的 xarray 外展 1.5
        # 6、波长与保留下来的能量包络进行积分

        smoothed_matrix = DenoiseSignal(indes_matrix[i, :])
        smoothed_matrix_[i, :] = smoothed_matrix
        # 指定阈值，找到大于阈值的元素的索引
        threshold = [550, np.max(wave_matrix[i, :])]
        indices = np.where((wave_matrix[i,:] > threshold[0]) & (wave_matrix[i,:] < threshold[1]))[0]
        wavelength_ = wave_matrix[i, min(indices):-1]
        indensity_ = smoothed_matrix_[i, min(indices):-1]

        indx_indensity = np.argmax(indensity_)  # 找到最大值对应得索引

        max_intensity_List.append(np.max(indensity_))
        # wavelength_List.append(wavelength_[indx_indensity])

    figurename = 'Camera'+match.group(1)

    # wavelength_List 是Monochromator标定使用的 gap=5 的数组
    # max_intensity_List 是每个数组对应的最大值
    # indes_matrix 是强度对应的数组
    # wave_matrix 是波长对应的数组
    # indices 是有效波长对应的索引
    wavelength_List = np.array(sorted(wavelength_List))
    # filtered_wavelength_List = wavelength_List[wavelength_List <= 9800]

    return wavelength_List, max_intensity_List, indes_matrix, wave_matrix, indices

def output_originalSpectrum_tendencies(wavelength_List_R, wave_matrix, indes_matrix, indices, ansys_FolderPath, formatted_timestamp):
    # Used to get the original spectrum tendency
    #
    # Input parameters:
    #   - wavelength_List_R : 660~980 gap=5 array, form system calibration
    #   - wave_matrix: Wave array mapping the available data in each file
    #   - indes_matrix : Index array mapping the available data in each file
    #   - indices: Index mapping the available wavelength which is the same array of each file
    #   - ansys_FolderPath: Used to save detail information which was analyzed
    #
    # Output parameters:
    #   - wave_matrix_valiable : 660~980 gap=5 array, form system calibration
    #   - mainEnergyPack : Main energy blob of each file
    #

    mainEnergyPack = np.zeros([len(wavelength_List_R), len(indices)])
    energyThreshold = 3/100
    indes_matrix_valiable = indes_matrix[:, indices[:]]
    wave_matrix_valiable = wave_matrix[:, indices[:]]

    # plt.figure(figsize=(18, 12))
    # plt.plot(wave_matrix_valiable[76, :], indes_matrix_valiable[76, :])
    # plt.show()

    for i in range(len(wavelength_List_R)):
        # Find main energy range
        EnergyPeakValue = np.max(indes_matrix_valiable[i, :])
        threshold = energyThreshold * EnergyPeakValue
        EnergyPeak_index = np.argmax(indes_matrix_valiable[i, :])
        EnergyRange_index_left = np.max(np.where(indes_matrix_valiable[i, : EnergyPeak_index + 1] < threshold)[0])
        EnergyRange_index_right_num = np.where(indes_matrix_valiable[i, EnergyPeak_index: -1] < threshold)[0]
        plt.figure(1, figsize=(18, 12))
        plt.plot(wave_matrix[i, : -10], indes_matrix[i, : -10], linestyle='--', color='black')

        if EnergyRange_index_right_num.size > 0:
            EnergyRange_index_right = np.min(EnergyRange_index_right_num)
            mainEnergyPack[i, EnergyRange_index_left : EnergyPeak_index+EnergyRange_index_right+1] = \
                (indes_matrix_valiable[i, EnergyRange_index_left : EnergyPeak_index+EnergyRange_index_right+1])
            plt.figure(1, figsize=(18, 12))
            plt.plot(wave_matrix_valiable[i, :],mainEnergyPack[i, :])
            plt.grid(True)
            plt.title('Spectrum Tendencies of Monochromatic')
            plt.savefig(ansys_FolderPath + r'\01_Original_Spectrum_Tendencies.png')

    plt.close(1)
    print('-> output original spectrum ')
    return wave_matrix_valiable, mainEnergyPack

def curveTendencyVIS(directory_path_n):
    # Used to get the intermediate parameter from monochromator
    #
    # Input parameters:
    #   - directory_path_n : Folder to be analyzed which from monochromator
    #
    # Output parameters:
    #   - wavelength_List : 660~980 gap=5 array, form system calibration
    #   - max_intensity_List : Max value from each wavelength
    #   - indes_matrix : Index array mapping the available data in each file
    #   - wave_matrix : Wave array mapping the available data in each file
    #   - indices : Index mapping the available wavelength which is the same array of each file
    #
    if 'LabSphere' in directory_path_n:
        # 使用正则表达式提取LabSphere后面的所有字符串
        pattern = r'LabSphere_(.+)'  # (.+) 匹配一个或多个字符
        match = re.search(pattern, directory_path_n)
    else:
        pattern = r'Camera(\d+_\d+)'
        match = re.search(pattern, directory_path_n)

    txt_files = find_txt_files(directory_path_n)
    wavelength_List = []

    for i in range(len(txt_files)):
        file_name = directory_path_n  # Double '\' Synthesis Path
        txt_files = get_txt_files_in_directory(file_name)
        txt_file_lines = read_txt_file(txt_files[i])

        strmonodata = txt_file_lines[0]
        monomatch = re.search(r'Spectrum_(\d+)', strmonodata)
        number = monomatch.group(1)
        wavelength_List.append(int(number)/1)

        target_strings = [r'Number of Pixels in Spectrum:3648', r'Number of Pixels in Spectrum: 3648', r'Number of Pixels in Spectrum: 2048']
        matching_indices = np.isin(txt_file_lines, target_strings)
        matching_rows = np.where(matching_indices)[0]  # 行数是从1开始计数
        file_pixel_info = txt_file_lines[int(matching_rows)]
        pattern_info = r'Spectrum:\s*(\d+)'  # (.+) 匹配一个或多个字符
        match_data = re.search(pattern_info, file_pixel_info)
        spectrum_pixels = match_data.group(1)

    wave_matrix = np.zeros((len(txt_files), int(spectrum_pixels)))
    indes_matrix = np.zeros((len(txt_files), int(spectrum_pixels)))
    smoothed_matrix_ = np.zeros((len(txt_files), int(spectrum_pixels)))

    max_intensity_List = []

    # 获取 SetUpCalibration 信息
    for i in range(len(txt_files)):
        file_name = directory_path_n  # Double '\' Synthesis Path
        txt_files = get_txt_files_in_directory(file_name)

        txt_file_lines = read_txt_file(txt_files[i])
        data_strings = txt_file_lines[14: -1]

        numeric_matrix = []
        for data_string in data_strings:
            parts = data_string.strip().split('\t')  # 分割字符串，去除多余的空白字符
            numeric_row = [float(part) for part in parts]  # 将字符串部分转换为浮点数
            numeric_matrix.append(numeric_row)  # 添加该行到矩阵

        for j in range(len(numeric_matrix)):
            wave_matrix[i, j] = numeric_matrix[j][0]
            indes_matrix[i, j] = numeric_matrix[j][1]

        # 对数据进行去噪处理
        # 降噪处理有好几部分
        # 1、Range 为 550nm ~ 1000 nm
        # 2、Value 为负数的直接赋 0
        # 3、不进行 Smooth 直接找 Peak 值，尽可能的保真
        # 4、能量包络 Threshold 按照 3% 衡量
        # 5、能量包络的 xarray 外展 1.5
        # 6、波长与保留下来的能量包络进行积分

        smoothed_matrix = DenoiseSignal(indes_matrix[i, :])
        smoothed_matrix_[i, :] = smoothed_matrix
        # 指定阈值，找到大于阈值的元素的索引
        threshold = [400, 800]
        indices = np.where((wave_matrix[i,:] > threshold[0]) & (wave_matrix[i,:] < threshold[1]))[0]
        wavelength_ = wave_matrix[i, min(indices):-1]
        indensity_ = smoothed_matrix_[i, min(indices):-1]

        indx_indensity = np.argmax(indensity_)  # 找到最大值对应得索引

        max_intensity_List.append(np.max(indensity_))

    figurename = 'Camera'+match.group(1)

    # wavelength_List 是标定使用的 660~980 gap=5 的数组
    # max_intensity_List 是每个数组对应的最大值
    # indes_matrix 是强度对应的数组
    # wave_matrix 是波长对应的数组
    # indices 是有效波长对应的索引

    return wavelength_List, max_intensity_List, indes_matrix, wave_matrix, indices


def curveTendencyVISZolix(directory_path_n):
    if 'LabSphere' in directory_path_n:
        # 使用正则表达式提取LabSphere后面的所有字符串
        pattern = r'LabSphere_(.+)'  # (.+) 匹配一个或多个字符
        match = re.search(pattern, directory_path_n)
    else:
        pattern = r'Camera(\d+_\d+)'
        match = re.search(pattern, directory_path_n)

    txt_files = find_txt_files(directory_path_n)
    wavelength_List = []

    for i in range(len(txt_files)):
        file_name = directory_path_n  # Double '\' Synthesis Path
        txt_files = get_txt_files_in_directory(file_name)
        txt_file_lines = read_txt_file(txt_files[i])

        strmonodata = txt_file_lines[0]
        # monomatch = re.search(r'Spectrum_(\d+)', strmonodata)


        print(strmonodata)
        number = strmonodata.split('_')[0][2:5]
        # print(number)
        # print(strmonodata)
        # print(txt_file_lines)
        # number = monomatch.group(1)

        wavelength_List.append(int(number))


        target_strings = [r'Number of Pixels in Spectrum:3648', r'Number of Pixels in Spectrum: 3648', r'Number of Pixels in Spectrum: 2048']
        matching_indices = np.isin(txt_file_lines, target_strings)
        matching_rows = np.where(matching_indices)[0]  # 行数是从1开始计数
        file_pixel_info = txt_file_lines[int(matching_rows)]
        pattern_info = r'Spectrum:\s*(\d+)'  # (.+) 匹配一个或多个字符
        match_data = re.search(pattern_info, file_pixel_info)
        spectrum_pixels = match_data.group(1)


    # AllBandPower = np.zeros((len(txt_files),10))
    wave_matrix = np.zeros((len(txt_files), int(spectrum_pixels)))
    indes_matrix = np.zeros((len(txt_files), int(spectrum_pixels)))
    smoothed_matrix_ = np.zeros((len(txt_files), int(spectrum_pixels)))

    max_intensity_List = []

    # 获取 SetUpCalibration 信息
    for i in range(len(txt_files)):
        file_name = directory_path_n  # Double '\' Synthesis Path
        txt_files = get_txt_files_in_directory(file_name)

        txt_file_lines = read_txt_file(txt_files[i])
        data_strings = txt_file_lines[14: -1]

        numeric_matrix = []
        for data_string in data_strings:
            parts = data_string.strip().split('\t')  # 分割字符串，去除多余的空白字符
            numeric_row = [float(part) for part in parts]  # 将字符串部分转换为浮点数
            numeric_matrix.append(numeric_row)  # 添加该行到矩阵

        for j in range(len(numeric_matrix)):
            wave_matrix[i, j] = numeric_matrix[j][0]
            indes_matrix[i, j] = numeric_matrix[j][1]

        # 对数据进行去噪处理
        # 降噪处理有好几部分
        # 1、Range 为 550nm ~ 1000 nm
        # 2、Value 为负数的直接赋 0
        # 3、不进行 Smooth 直接找 Peak 值，尽可能的保真
        # 4、能量包络 Threshold 按照 3% 衡量
        # 5、能量包络的 xarray 外展 1.5
        # 6、波长与保留下来的能量包络进行积分

        smoothed_matrix = DenoiseSignal(indes_matrix[i, :])
        smoothed_matrix_[i, :] = smoothed_matrix
        # 指定阈值，找到大于阈值的元素的索引
        threshold = [400, 800]
        indices = np.where((wave_matrix[i,:] > threshold[0]) & (wave_matrix[i,:] < threshold[1]))[0]
        wavelength_ = wave_matrix[i, min(indices):-1]
        indensity_ = smoothed_matrix_[i, min(indices):-1]

        indx_indensity = np.argmax(indensity_)  # 找到最大值对应得索引

        max_intensity_List.append(np.max(indensity_))
        # wavelength_List.append(wavelength_[indx_indensity])

    figurename = 'Camera'+match.group(1)

    # wavelength_List 是标定使用的 660~980 gap=5 的数组
    # max_intensity_List 是每个数组对应的最大值
    # indes_matrix 是强度对应的数组
    # wave_matrix 是波长对应的数组
    # indices 是有效波长对应的索引

    return wavelength_List, max_intensity_List, indes_matrix, wave_matrix, indices, figurename, spectrum_pixels



def ReadXml(FilePath):
    # 指定 XML 文件路径
    xml_file_path = FilePath + '\Experiment log.xml'

    # 解析 XML 文件
    tree = etree.parse(xml_file_path)

    # 获取根元素
    root = tree.getroot()
    count = 0

    # 遍历 XML 结构
    for element in root.iter():
        count = count + 1
        # print(f"{element.tag}: {element.text}")
        if count == 6:
            SRCalibPath = element.text

    print('-> Find the SRSetup Calibration Data Path at: \n', SRCalibPath)
    return SRCalibPath


def GetSystemResponse(SetupPath, ansys_FolderPath, FilePath, formatted_timestamp):
    # Find the folder which is available
    # Initialize element settings
    [indx, file_list, wavelength_list, count] = count_files_in_directory(FilePath)
    norsize = count
    AllBandPower = np.zeros((norsize,10))

    [wavelength_List_R, max_intensity_List, indes_matrix, wave_matrix, indices, figurename, spectrum_pixels] = curveTendency(SetupPath)
    [wave_matrix_valiable, mainEnergyPack] = output_originalSpectrum_tendencies(wavelength_List_R, wave_matrix, indes_matrix, indices, ansys_FolderPath, formatted_timestamp)

    # Search for maximal of each spectrum and plot the curves
    Peak_Intensity_matrix = []
    Peak_wave_matrix = []
    [ST_row, ST_Column] = np.shape(mainEnergyPack[:, :])

    for i in range(ST_row):
        Peak_Intensity_matrix.append(np.trapz(mainEnergyPack[i, :], wave_matrix_valiable[i, :]))
        Peak_indx_matrix = np.argmax(wave_matrix_valiable[i, :])
        Peak_wave_matrix.append(wave_matrix[i, Peak_indx_matrix])

    window_size = 5  # 窗口大小
    poly_order = 2  # 多项式拟合的阶数
    k = 1 # 校正系数
    Peak_Intensity_matrix_smoothed = k * savgol_filter(Peak_Intensity_matrix, window_size, poly_order)

    # Rebuild matrix for wave array
    # Find min wave data and index
    wavelength_List_R = np.array(wavelength_List_R)/10
    wavelength_List_R = list(wavelength_List_R)
    if wavelength_List_R[0] <= wavelength_list[0]:
        minwavedata_indx = wavelength_List_R.index(wavelength_list[0])
        minwavedata = wavelength_list[0]
    else:
        minwavedata_indx = wavelength_list.index(wavelength_List_R[0])
        minwavedata = wavelength_List_R[0]
    # Find max wave data and index
    if wavelength_List_R[-1] <= wavelength_list[-1]:
        maxwavedata_indx = wavelength_list.index(wavelength_List_R[-1])
        maxwavedata = wavelength_List_R[-1]
    else:
        maxwavedata_indx = wavelength_List_R.index(wavelength_list[-1])
        maxwavedata = wavelength_List_R[-1]

    wavedata = np.arange(minwavedata, maxwavedata+1, 5)

    bandwaverange = wavelength_list[0 : maxwavedata_indx+1]

    Radiance_data = np.zeros([len(bandwaverange), 2])
    Radiance_data[:, 0] = bandwaverange[:]
    Radiance_data[:, 1] = Peak_Intensity_matrix_smoothed[minwavedata_indx:]

    # Collector Intensity Distribution
    for i in range(len(indx)):
        file_name = (FilePath + "\\" + file_list[indx[i]])  # Double '\' Synthesis Path
        raw_file_name = file_rawdata_element(file_name) # Determine the data of the document
        hdr_path = file_name + "\\" + raw_file_name[0]
        raw_path = file_name + "\\" + raw_file_name[1]

        data = spectral.envi.open(hdr_path)
        img = []
        A = np.zeros((10, 1)) # Build buffer for centerpower
        for index, band in enumerate(data.bands.centers):
            img = data.read_band(index)
            center_x = img.shape[0] // 2
            center_y = img.shape[1] // 2
            power = centerpower(img, center_x, center_y) # Calculate center power
            A[index] = power

        AllBandPower[i, :] = np.transpose(A)

    # Normalize the data
    AllBandPower_ = AllBandPower[0:maxwavedata_indx+1, 0:]

    BandPowerData = np.zeros([len(AllBandPower_), 10])
    BandPowerData[:, :] = AllBandPower_[:, :]
    # file_path = ansys_FolderPath + r"\07_BandPowerData.txt"
    # np.savetxt(file_path, BandPowerData, fmt='%.6f', delimiter='\t')

    PowerNormal_dist = np.zeros([len(wavedata), 10])
    x_array = np.arange(minwavedata, maxwavedata, 1)
    PowerNormal_Fitting_dist = np.zeros([len(x_array), 10])
    Data_CWL = np.zeros(10)
    CWL = [713, 736, 759, 782, 805, 828, 851, 874, 897, 920]

    for j in range(10):
        # 定义移动平均窗口大小
        window_size = 1
        # 计算移动平均
        smoothed_data = np.convolve(AllBandPower_[:, j], np.ones(window_size) / window_size, mode='same')

        PowerNormal_dist[:, j] = smoothed_data / Peak_Intensity_matrix_smoothed[minwavedata_indx:]
        PowerNormal_fitting = interp1d(wavedata, PowerNormal_dist[:, j], kind='cubic')
        PowerNormal_Fitting_dist[:, j] = PowerNormal_fitting(x_array)
        # use argmax find the index of the maximum element
        max_index = np.argmax(PowerNormal_Fitting_dist[:, j])
        Data_CWL[j] = x_array[max_index]

        plt.figure(2, figsize=(14, 8)),
        plt.plot(wavedata, PowerNormal_dist[:, j], 'r-', linewidth=2)
        plt.plot(x_array, PowerNormal_Fitting_dist[:, j], 'g--', label='post-fit curve')
        plt.legend(['Original Data', 'Post-processing Data'], loc='upper right')
        plt.grid(True)
        plt.title('Monarch Power Distribution After Normalization')
        plt.savefig(
            ansys_FolderPath + r'\02_Monarch_Power_Distribution_After_Normalization.png')
    return x_array, PowerNormal_Fitting_dist

def AnalyzeSystemResponse(x_array, SystemResponse):
    J_count = 0
    for i in range(10):
        dx = np.diff(x_array)
        dy = np.diff(SystemResponse[:, i])
        dy_dx = dy / dx

        # Smooth the Diff data
        # Define the smooth window
        window_size = 5
        smoothed_y = np.convolve(dy_dx, np.ones(window_size) / window_size, mode='valid')

        # Disposal of noise
        threshold = np.max(smoothed_y) * 1 / np.exp(2)
        smoothed_y[abs(smoothed_y) < threshold] = 0

        # Judgement
        # Find all index which value > 0
        positive_indices = np.where(smoothed_y > 0)[0]
        # Find all index which value < 0
        negative_indices = np.where(smoothed_y < 0)[0]

        if max(positive_indices) > min(negative_indices):
            J_count += 1
            print('-> Error ： Band ', i+1, 'have more than 1 Peak or more than 1 Troughs.')


        plt.figure(3, figsize=(14, 8))
        plt.plot(x_array[:len(smoothed_y)], smoothed_y, label='dy/dx')
        plt.title('Derivative'), plt.grid(True)
        plt.legend()

    if J_count > 0:
        result = 'NG'
    else:
        result = 'PASS'

    return result

def print_csv_files(directory):
    try:
        # 获取目录下所有文件
        files = os.listdir(directory)

        # 筛选出以.csv结尾的文件
        csv_files = [file for file in files if file.endswith(".csv")]
        count = 0
        csv_file_name = [None] * len(csv_files)
        # 打印.csv文件名
        print(f"获取在目录 {directory} 下的.csv文件 ")
        for csv_file in csv_files:
            csv_file_name[count] = csv_file
            count = count + 1
    except Exception as e:
        print(f"发生错误: {e}")

    return csv_file_name


def find_duplicates_with_index(nums):
    num_index_dict = {}  # 用字典存储数字和它们的索引

    for i, num in enumerate(nums):
        if num in num_index_dict:
            # 如果数字已经在字典中，则是重复的
            print(f"重复的数值 {num} 在索引 {num_index_dict[num]} 和 {i}")
        else:
            # 否则将数字和索引存入字典
            num_index_dict[num] = i



def CreateFolder(path, Foldername):
    folder_save_Path = path + Foldername

    # 检查文件夹是否已存在
    if not os.path.exists(folder_save_Path):
        # 创建文件夹
        os.makedirs(folder_save_Path)
        print(f"-> Info: Folder '{folder_save_Path}' created! ")
    else:
        print(f"-> Info: Folder '{folder_save_Path}' already exists! ")

    return folder_save_Path


def GetStateCubeData(Path):
    raw_file_name = file_rawdata_element(Path)  # Determine the data of the document

    hdr_path = Path + "\\" + raw_file_name[0]
    raw_path = Path + "\\" + raw_file_name[1]

    data = spectral.envi.open(hdr_path)
    bandnum = data.nbands
    img = np.zeros([1024, 1280, bandnum])
    for index, band in enumerate(data.bands.centers):
        imginfo = data.read_band(index)
        img[:, :, index] = np.float32(imginfo)
    return img, bandnum

def CWLDriftDataSaving(directory_path, current_Second_directory):
    # Start time
    start_time = time.process_time()
    # Get the current time
    current_date = datetime.datetime.now().strftime("%Y%m%d%H%M")
    directory_path_n = directory_path

    # Finding Available Files
    [file_list, wavelength_list] = count_files_in_directory(directory_path_n)

    img = np.zeros((1024, 1280, 10, len(file_list)))

    # Collecting All Cube Information
    [img, AllBandPower, exposureTime, Gain] = CollectAllBand(file_list, img, directory_path_n, wavelength_list)

    CWL = []
    for i in range(10):
        valy = AllBandPower[:, i]
        valy_list = valy.tolist()
        # Initialize the maximum value and its corresponding index
        max_value = max(valy)
        max_index = valy_list.index(max_value)
        CWL.append(wavelength_list[max_index])
        # print('第',i,'组曲线的中心波长是',CWL[i])


    # New Folder to saved Image
    Wafer_level = findWaferIndx(directory_path)
    camera_layer = findcamera_layer(directory_path)


    output_folder = f"{current_Second_directory}\\{Wafer_level}_{camera_layer}_output_Info_{current_date}"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Save Spectrum Cube to folder which names currently time
    img_Cube, driftdata_Array = DealWithSpectrum_50pixel(img, output_folder, wavelength_list, file_list)
    # print(img_Cube.shape)

    # folder = output_folder+"/raw/cube_{}".\
    #     format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    # os.makedirs(folder, exist_ok=True)
    # img_frame = []
    # envi = ENVI(sensor_type="MONARCH")
    # for i in range(10):
    #     envi.append_data(
    #         img=img_Cube[:, :, i],
    #         data={
    #             ENVI.WAVELENGTH: CWL[i],
    #             ENVI.GAIN: Gain,
    #             ENVI.EXPOSURE_TIME: exposureTime,
    #             ENVI.EXPOSURE_TYPE: "radiometric-calibration",
    #             ENVI.DEFAULT_BANDS: CWL[0]
    #         }
    #     )
    #
    # envi.save(folder)

    # Recording Ending time
    end_time = time.process_time()
    # Calculate execution time
    execution_time = end_time - start_time

    print("CWL Drift 代码块执行时间：", execution_time, "秒")

    # pyimageinfo = img[:, :, 0, 10]
    # img_Cube_simgle = img_Cube[:, :, 1]
    return img_Cube, driftdata_Array, output_folder
    # plt.show()

def findcamera_layer(path):
    # 使用正则表达式匹配路径中的 Camera 层
    match = re.search(r'Camera\d+', path)

    if match:
        camera_layer = match.group()
        print("Camera 层的路径名称为:", camera_layer)
        return camera_layer
    else:
        print("未找到 Camera 层的路径名称")


def findWaferIndx(path):
    # 使用正则表达式匹配路径中的第四级目录层
    match = re.search(r'\\[^\\]+\\([^\\]+)\\[^\\]+\\[^\\]+\\', path)

    if match:
        Wafer_level = match.group(1)
        print("芯片目录层的名称为:", Wafer_level)
        return Wafer_level
    else:
        print("未找到芯片目录层")


def CreatSavingFolderpath(Layer_name):
    # Create the folder path used to saving output files.
    #
    # Input parameters:
    #   - Layer_name
    #
    # Output parameters:
    #   - Create saving folder
    #

    # Get the current directory path
    current_directory = os.getcwd()
    # Creaste the layer path
    current_Second_directory = os.path.join(current_directory, Layer_name)

    # Check if a folder already exists
    if not os.path.exists(current_Second_directory):
        os.makedirs(current_Second_directory)
        print(f'-> Folder created successfully!\n')
    else:
        print(f"-> Folder '{Layer_name}' already exists! ")

    return current_Second_directory


def AccuracySanityCheck(Data_directory_path, ansys_FolderPath, formatted_timestamp):
    # Check the accuracy of raw data.
    #
    # Input parameters:
    #   - Data_directory_path
    #   - ansys_FolderPath
    #   - Formatted_timestamp
    #
    # Output parameters:
    #   - Diagram about the accuracy sanity test
    #

    # Find the underlying catalog name
    last_dir = os.path.basename(Data_directory_path)
    last_dir = formatted_timestamp + '_' + last_dir
    ansys_FolderPath = CreateFolder(ansys_FolderPath, last_dir)

    ansys_FolderPath_original = ansys_FolderPath
    Data_directory_path_original = Data_directory_path

    file_list_1st = os.listdir(Data_directory_path)
    print(f'-> Info: This directory has {len(file_list_1st)} files.')

    CWL = np.array([510, 530, 550, 570, 590, 610, 630, 650, 670, 690, 713, 736, 759, 782, 805, 828, 851, 874, 897, 920])
    ROI_info = np.zeros((len(CWL), len(CWL), len(file_list_1st))) - 1

    for num in range(len(file_list_1st)):
        print(f'-> Info: Now analyze data is FPS = {file_list_1st[num]}.')
        foldername = f'FPS={file_list_1st[num]}'
        ROI = np.zeros((len(CWL), len(CWL))) - 1
        # Get data detail directory
        Data_directory_path = os.path.join(Data_directory_path_original, file_list_1st[num])
        [file_list, wavelength_list] = count_files_in_directory(
            Data_directory_path)  # Find the folder valiable

        plt.figure(num + 1, figsize=(10, 16))
        databox = np.zeros(len(CWL)) - 1
        for j in range(len(file_list)):
            indx = np.where(CWL == wavelength_list[j])[0]
            img_path = os.path.join(Data_directory_path, file_list[j])
            img_data_info = GetStateCubeData(img_path)
            img_data = img_data_info[0]
            for i_image in range(len(CWL)):
                data = img_data[:, :, i_image]
                img_info = data[int(462): int(562), int(590): int(690)]
                databox[i_image] = np.mean(img_info)
            ROI[indx, :] = databox[:] / max(databox[:])

        ROI_info[:, :, num] = ROI[:, :]
        for j in range(len(CWL)):
            if j < 10:
                plt.subplot(10, 2, 2 * (j + 1) - 1), plt.plot(CWL, ROI[j, :])
                plt.grid(True), plt.ylim(0, 1.2)
            else:
                plt.subplot(10, 2, 2 * (j + 1 - 10)), plt.plot(CWL, ROI[j, :])
                plt.grid(True), plt.ylim(0, 1.2)

        filename = foldername
        filepath = os.path.join(ansys_FolderPath_original, filename)
        plt.savefig(filepath)

    print('=============== Cal CWL =================')
    plt.figure(figsize=(10, 16))
    for j in range(len(file_list_1st)):
        for num in range(len(CWL)):
            # Find each the max value of available matrix
            ROIdata = ROI_info[num, :, j]
            array = find_max_and_index(ROIdata)
            if array[0] == -1:
                # print(f'-> Info : FPS = {file_list_1st[j]}, Band {num+1} CWL is None')
                continue
            else:
                if len(array[1]) == 1:
                    if CWL[array[1]] == CWL[num]:
                        print(f'-> Info : FPS = {file_list_1st[j]}, Band {num + 1} CWL is True')
                    else:
                        print(f'-> Info : FPS = {file_list_1st[j]}, Band {num + 1} CWL is {CWL[array[1]]}, wanted CWL is {CWL[num]}')
                else:
                    print(f'\n=============== Warning =================')
                    print('-> Info: There are more than one maximum element !')
                    for count in range(len(array[1])):
                        A = array[1][count]
                        print(f'--> Error : FPS = {file_list_1st[j]}, Band {num + 1} CWL is {CWL[A]}, wanted CWL is {CWL[num]}')
                    print(f'=========================================\n')

            if num < 10:
                plt.subplot(10, 2, 2 * (num + 1) - 1), plt.plot(CWL, ROI_info[num, :, j])
                plt.grid(True), plt.ylim(0, 1.2)
            else:
                plt.subplot(10, 2, 2 * (num + 1 - 10)), plt.plot(CWL, ROI_info[num, :, j])
                plt.grid(True), plt.ylim(0, 1.2)

    filename = 'AllFPSDis'
    filepath = os.path.join(ansys_FolderPath_original, filename)
    plt.savefig(filepath)
    print('-> Info: Finished!')


def find_max_and_index(arr):

    max_val = np.max(arr)  # find the maximum
    max_index = np.where(arr == max_val)[0]  # find the index of maximum value

    return max_val, max_index

def get_json_data(json_path):
    # 读取 json 文件内容
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def get_csv_data(csv_path):
    # 打开并读取 CSV 文件
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        # 将内容保存为矩阵
        matrix = [row for row in reader]
        # 打印矩阵内容
        # for row in matrix:
        #     print(row)

    return matrix

def get_excel_data(file_path):
    # 读取Excel文件
    df = pd.read_excel(file_path)
    return df