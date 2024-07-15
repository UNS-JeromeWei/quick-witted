# -*- coding: utf-8 -*-
import time, sys, os
import traceback
import numpy as np
import cv2
import datetime
import threading

from UNSCamera.camera_card_controller import CameraCardController
from envi import ENVI
myCamera = CameraCardController()
videostream_state = True
lowpower_state = False
global EnablePreview
EnablePreview = False

def DisplaySerialNumber():
    print("SerialNumber = {}".format(myCamera.GetSerialNumber()))


def DisplayGainRatio():
    print("GainRatio = {}".format(myCamera.GetGain()))


def DisplayExposureTime():
    print("ExposureTime = {}".format(myCamera.GetExposureTime()))


def DisplayTemperture():
    print("Tempreture = {}".format(myCamera.GetTemperature()))


def DisplayACTD():
    print("ACTD = {}".format(myCamera.GetACTD()))


def DisplayLutLine():
    print("L - Display LUT Table ")
    for i in range(10):
        ret = myCamera.GetLUTLine(i)
        try:
            print('''LutLine("{}") = ("{}", "{}", "{}", "{}") , "{}", "{}", "{}"'''.format(i, ret[0][0], ret[0][1],
                                                                                           ret[0][2], ret[0][3], ret[1],
                                                                                           ret[2], ret[3]))
        except:
            pass


def DisplayFWVersion():
    print("FWVersion = {}".format(myCamera.GetFwVersion()))


def DisplayAPIVersion():
    print("APIVersion = {}".format(myCamera.GetApiVersion()))


def ChangeACTD():
    try:
        newVal = input("Enter new ACTD:")
        myCamera.SetACTD(int(newVal))
    except:
        print("{}".format(traceback.format_exc()))


def ChangeGainRatio():
    try:
        newVal = input("Enter new GainRatio:")
        myCamera.SetGain(float(newVal))
    except:
        print("{}".format(traceback.format_exc()))


def ChangeExposureTime():
    try:
        newVal = input("Enter new ExposureTime (fps):")
        myCamera.SetExposureFps(int(newVal))
    except:
        print("{}".format(traceback.format_exc()))


def ChangeCurrentLineIndex():
    try:
        newVal = input("Enter new Current LUT Index:")
        myCamera.SetLUTIndex(int(newVal))
    except:
        print("{}".format(traceback.format_exc()))


def RestoreLUT():
    print("Restore LUT Table")
    myCamera.RestoreLUT()


def ChangeSerialNumber():
    try:
        newVal = input("Enter new  SerialNuber:")
        myCamera.SetSerialNumber(int(newVal))
    except:
        print("{}".format(traceback.format_exc()))


def BuildCustomLUT():
    try:
        indexes = input("Enter relevant indexes:")
        array = indexes.split(",")
        array = [int(i) for i in array]
        myCamera.BuildCustomLUT(array)
    except:
        print("{}".format(traceback.format_exc()))


def SetBandVoltages():
    try:
        newVal = input("Enter line index : ")
        myCamera.SetLineVoltages(int(newVal))
    except:
        print("{}".format(traceback.format_exc()))


def AutoExposuer():
    try:
        newExposuer, maxBrightBand = myCamera.AutoExposure()
        print("new exposuer:{}, brightest band:{}".format(newExposuer, maxBrightBand))
    except:
        print("{}".format(traceback.format_exc()))


def TurnONLed():
    myCamera.PowerLed(1)


def TurnOFFLed():
    myCamera.PowerLed(0)


def ToggleVideoStream():
    if videostream_state:
        videostream_state = False
        myCamera.EnableVideoStream(0)
    else:
        videostream_state = True
        myCamera.EnableVideoStream(1)


def ToggleLowPower():
    if lowpower_state:
        lowpower_state = False
        myCamera.EnableLowPower(0)
    else:
        lowpower_state = True
        myCamera.EnableLowPower(1)

def EnableThermalShiftCorrection():
    myCamera.EnableThermalShiftCorrection()
    print("enabled thermal shift correction algorithm")

def DisableThermalShiftCorrection():
    myCamera.DisableThermalShiftCorrection()
    print("disabled thermal shift correction algorithm")

def GetThermalShiftCorrectionCoefs():
    coefs = myCamera.GetThermalShiftCorrectionCoefs()
    print(f"the coefs is:{coefs}")

def SetThermalShiftCorrectionCoefs():
    input_str = input("Enter the Coefs (dict type):")
    try:
        coefs = eval(input_str)
        if not isinstance(coefs, dict):
            print("the input is not dict instance")
            return
    except SyntaxError:
        print("the input is not valid")
        return

    myCamera.SetThermalShiftCorrectionCoefs(coefs)

def GetAvailableBands():
    bands=myCamera.GetAvailableBands()
    print("available bands list:\n")
    for index,band in enumerate(bands):
        print(f"#{index}         {band} nm")

def ValidateWantedBands():
    input_str = input("Enter the bands to be validated (list type):")
    try:
        bands = eval(input_str)
        if not isinstance(bands, list):
            print("the input is not list instance")
            return
    except SyntaxError:
        print("the input is not valid")
        return
    valid_bands,invalid_bands=myCamera.ValidateWantedBands(bands)

    print("valid bands:\n")
    print(valid_bands)
    print("=========================================")


    print("invalid bands:\n")
    print(invalid_bands)
    print("=========================================")



def GetWantedLut():
    input_str = input("Enter your wanted bands (list type), use default 10 bands, press enter directly:")
    if input_str=="":
        bands=[713,736,759,782,805,828,851,874,897,920]
    else:
        try:
            bands = eval(input_str)
            if not isinstance(bands, list):
                print("the input is not list instance")
                return
        except SyntaxError:
            print("the input is not valid")
            return

    lut=myCamera.GetWantedLut(bands)
    print("lut for wanted bands:\n")
    print(lut)
    return lut

def GetWantedLutAndUpdateLut():
    lut=GetWantedLut()
    if not isinstance(lut,list):
        return 
    myCamera.UpdateLut(lut)

    



def SavePng(folder, img, cwl, gain, exposure):
    folder = folder + "/png/"
    os.makedirs(folder, exist_ok=True)
    fileName = "CWL_{}_Gain_{}_Exposure_{}.png".format(cwl, gain, exposure)
    file_path = folder + fileName
    img = cv2.subtract(img, 64)
    png_img = (img >> 2).astype(np.uint8)
    file_path.encode(encoding='utf-8').decode('ascii')
    cv2.imwrite(file_path, png_img, [cv2.IMWRITE_PNG_COMPRESSION, 0])


def SaveCaptureedLUT(hs_cube):
    # create folder to save png/raw/hdr
    temperature = myCamera.GetTemperature()
    folder = "../../raw/cube_{}".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    os.makedirs(folder, exist_ok=True)
    envi = ENVI(sensor_type="MONARCH")
    DEFAULT_BANDS = None
    for i in range(10):
        ret = myCamera.GetLUTLine(i)
        try:
            print('''LutLine("{}") = ("{}", "{}", "{}", "{}") , "{}", "{}", "{}"'''.format(i, ret[0][0], ret[0][1],
                                                                                           ret[0][2], ret[0][3], ret[1],
                                                                                           ret[2], ret[3]))
            if not DEFAULT_BANDS:
                DEFAULT_BANDS = ret[3]
            envi.append_data(
                img=hs_cube[i],
                data={
                    ENVI.WAVELENGTH: ret[3],
                    ENVI.GAIN: ret[2],
                    ENVI.EXPOSURE_TIME: ret[1],
                    ENVI.EXPOSURE_TYPE: "radiometric-calibration",
                    ENVI.DEFAULT_BANDS: DEFAULT_BANDS
                }

            )
            envi.update_temperature(temperature)
            SavePng(folder, hs_cube[i], ret[3], ret[2], ret[1])
        except:
            pass

    envi.save(folder)


def CaptureLUTFrames():
    hs_cube = np.array(myCamera.CaptureLUT())
    hs_cube = hs_cube.reshape(-1, 1024, 1280)
    SaveCaptureedLUT(hs_cube)

def CaptureLUTFramesWithThermalShiftCorrection():
    bands=[713,736,759,782,805,828,851,874,897,920]
    myCamera.EnableThermalShiftCorrection()
    lut=myCamera.GetWantedLut(bands)
    myCamera.UpdateLut(lut)

    CaptureLUTFrames()



def ListCommands():
    print("h - Display Help")
    print("1 - Display data")
    print("F - Display FW version")
    print("V - Display API version")
    # print("a - Change ACDT Time" )
    print("A - Display ACDT Time")
    print("e - Change Exposure Time")
    print("E - Display Exposure Time")
    print("g - Change Gain Ratio")
    print("G - Display Gain Ratio")
    print("T - Display Temperture")
    # print("n - Change Serial Number" )
    print("N - Display Serial Number")
    # print("c - Change Coords" )
    # print("C - Display Coords" )
    # print("l - Change LUT Line" )
    print("L - Display LUT Line")
    print("v - Set LUT Line Voltages")
    print("x - Auto Exposure")
    print("y - Capture Cube")
    # print("s - SaveLUT" )
    print("r - RestoreLUT")
    print("b - BuilsCustomLUT")
    # print("w - Dac write" )
    print("u - Dac update")
    print("m - Turn on OpenCV camera")
    print("M - Turn off OpenCV camera")
    print("d - Turn on LED")
    print("D - Turn off LED")
    print("2 - Enable thermal shift correction algorithm")
    print("3 - Disable thermal shift correction algorithm")
    print("4 - Get thermal shift correction coefs")
    print("5 - Set thermal shift correction coefs")
    print("6 - Get available bands")
    print("7 - validate the wanted bands")
    print("8 - Get the LUT for wanted bands")
    print("9 - Get the LUT for wanted bands and update the LUT to camera")
    print("10 - Capture Cube for default 10 bands with thermal shift correction")
    print("q - Exit Application")

def DisplayAllData():
    print("------ Display All Data ------")
    DisplaySerialNumber()
    DisplayGainRatio()
    DisplayExposureTime()
    DisplayTemperture()
    DisplayACTD()
    DisplayLutLine()
    # DisplayOpenCVCameraStatus()


def preview():
    global EnablePreview
    while True:
        if EnablePreview:
            img = myCamera.GetPreview()
            img = np.array(img)
            img = np.fromstring(img, np.uint8)
            img = img.reshape([1024, 1280])
            img = img.astype(np.uint8)
            cv2.imshow("preview", img)
            cv2.waitKey(1)
        # else:
        #     cv2.destroyAllWindows()


def loop():
    global EnablePreview
    time.sleep(1)
    myCamera.SetExposureFps(10)
    while True:
        cmd = input("\nEnter request:>")
        # print(cmd)
        if cmd == "F":
            DisplayFWVersion()
        elif cmd == "A":
            DisplayACTD()
        elif cmd == "a":
            ChangeACTD()
        elif cmd == "V":
            DisplayAPIVersion()
        elif cmd == "G":
            DisplayGainRatio()
        elif cmd == "g":
            ChangeGainRatio()
        elif cmd == "E":
            DisplayExposureTime()
        elif cmd == "e":
            ChangeExposureTime()
        elif cmd == "I":
            ChangeCurrentLineIndex()
        elif cmd == "T":
            DisplayTemperture()
        elif cmd == "r":
            RestoreLUT()
        elif cmd == "n":
            ChangeSerialNumber()
        elif cmd == "N":
            DisplaySerialNumber()
        elif cmd == "H" or cmd == "h":
            ListCommands()
        elif cmd == "1":
            DisplayAllData()
        elif cmd == "L":
            DisplayLutLine()
        elif cmd == "y":
            oldPreviewMode = EnablePreview
            EnablePreview = False
            print("***** CaptureLUTFrames Start *****")
            CaptureLUTFrames()
            print("***** CaptureLUTFrames end *****")
            EnablePreview = oldPreviewMode

        elif cmd == "b":
            BuildCustomLUT()
        elif cmd == "v":
            SetBandVoltages()
        elif cmd == "x":
            print("***** Auto exposure start *****")
            oldPreviewMode = EnablePreview
            EnablePreview = False
            AutoExposuer()
            EnablePreview = oldPreviewMode
            print("***** Auto exposure start *****")
        elif cmd == "m":
            EnablePreview = True
        elif cmd == "M":
            EnablePreview = False
        elif cmd == "d":
            TurnONLed()
        elif cmd == "D":
            TurnOFFLed()
        elif cmd == "S":
            ToggleVideoStream()
        elif cmd == "P":
            ToggleLowPower()
        elif cmd == "2":
            EnableThermalShiftCorrection()
        elif cmd == "3":
            DisableThermalShiftCorrection()
        elif cmd == "4":
            GetThermalShiftCorrectionCoefs()
        elif cmd == "5":
            SetThermalShiftCorrectionCoefs()
        elif cmd == "6":
            GetAvailableBands()
        elif cmd == "7":
            ValidateWantedBands()
        elif cmd == "8":
            GetWantedLut()
        elif cmd == "9":
            GetWantedLutAndUpdateLut()
        elif cmd == "10":
            oldPreviewMode = EnablePreview
            EnablePreview = False
            print("***** CaptureLUTFrames with thermal shift correction Start *****")
            CaptureLUTFramesWithThermalShiftCorrection()
            print("***** CaptureLUTFrames with thermal shift correction end *****")
            EnablePreview = oldPreviewMode



        elif cmd == "q" or cmd == "Q":
            myCamera.Release()
            break


if __name__ == '__main__':
    DisplayAllData()
    t = threading.Thread(target=preview, args=())
    t.setDaemon(True)
    t.start()
    loop()

