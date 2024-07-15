#! /usr/bin/env python3
"""
Sample of using pyautogui (pip install pyautogui)
"""

### Globals ##################################################################
import asyncio
import datetime
import msvcrt
import os
import time
import pyautogui as ag
# import pygame

### GUI Sequences ############################################################

def gui_stray_light(args):
    """
    Automate stray light task.
    Capture images at varying exposure durations.
    """
    
    # Auto GUI
    COORDS = {
        "Context"   : (250, 10),
        "View"      : (65,30),
        "RegRW"     : (116,150),
        "RegAddress": (292, 145),
        "RegValue"  : (90, 216),
        "RegGet"    : (523, 119),
        "RegSet"    : (521, 154),
        "File"      : (32, 35),
        "RAW10"     : (67, 80),
        "Filename"  : (800, 824),
        "Save"      : (1417, 736),
        "SaveYes"   : (1020, 596)
    }
    DELAY = 0.5/2
    TYPE_DELAY = 0.05/4

    # Bring the window to context
    ag.moveTo(*COORDS["Context"], DELAY)
    ag.click()

    # Sequence
    fileprefix = os.path.spl
    
    exposure_vals = (
    0x000001,  
    0x00000a,
    0x000064,
    0x0003e8,
    0x002710,
    0x0186a0,
    0x0f4240
    )
    
    for exp, exposure_val in enumerate(exposure_vals):
        exposure_exp = 10**exp
        reg_low = hex(exposure_val & 0x0000ff)
        reg_mid = hex((exposure_val & 0x00ff00)>>8)
        reg_hi  = hex((exposure_val & 0xff0000)>>16)
    
        ag.moveTo(*COORDS["View"], DELAY)
        ag.click()
        ag.moveTo(*COORDS["RegRW"], DELAY)
        ag.click()
        
        ag.moveTo(*COORDS["RegAddress"], DELAY)     ; ag.doubleClick()
        ag.typewrite("0x3502", interval=TYPE_DELAY)
        ag.moveTo(*COORDS["RegGet"], DELAY)         ; ag.click()
        ag.moveTo(*COORDS["RegValue"], DELAY)       ; ag.doubleClick()
        ag.typewrite(reg_low, interval=TYPE_DELAY)
        ag.moveTo(*COORDS["RegSet"], DELAY)         ; ag.click()
        
        ag.moveTo(*COORDS["RegAddress"], DELAY)     ; ag.doubleClick()
        ag.typewrite("0x3501", interval=TYPE_DELAY)
        ag.moveTo(*COORDS["RegGet"], DELAY)         ; ag.click()
        ag.moveTo(*COORDS["RegValue"], DELAY)       ; ag.doubleClick()
        ag.typewrite(reg_mid, interval=TYPE_DELAY)
        ag.moveTo(*COORDS["RegSet"], DELAY)         ; ag.click()
        
        ag.moveTo(*COORDS["RegAddress"], DELAY)     ; ag.doubleClick()
        ag.typewrite("0x3500", interval=TYPE_DELAY)
        ag.moveTo(*COORDS["RegGet"], DELAY)         ; ag.click()
        ag.moveTo(*COORDS["RegValue"], DELAY)       ; ag.doubleClick()
        ag.typewrite(reg_hi, interval=TYPE_DELAY)
        ag.moveTo(*COORDS["RegSet"], DELAY)         ; ag.click()
        
        # Wait for change to update grabbing pipe
        ag.press("esc")
        time.sleep(1)
        # Save image
        ag.moveTo(*COORDS["File"], DELAY)           ; ag.click()
        ag.moveTo(*COORDS["RAW10"], DELAY)          ; ag.click()
        ag.moveTo(*COORDS["Filename"], DELAY)       ; ag.doubleClick()
        filename = os.path.join(args.dir, "{}_exp_{}.raw".format(fileprefix, exposure_exp))
        ag.typewrite(filename, interval=TYPE_DELAY)
        ag.moveTo(*COORDS["Save"], DELAY)           ; ag.click()
        ag.moveTo(*COORDS["SaveYes"], DELAY)        ; ag.click()
        
def sunny_auto_Save(filenameinput):
    """
    Automate sunny save
    Capture images at varying exposure durations.
    """
    DELAY = 0.5/4
    TYPE_DELAY = 0.05/4
    COORDS = {
        "Context"   : (250, 10),
        "View"      : (65,30),
        "RegRW"     : (116,150),
        "RegAddress": (292, 145),
        "RegValue"  : (90, 216),
        "RegGet"    : (523, 119),
        "RegSet"    : (521, 154),
        "File"      : (32, 35),
        "RAW10"     : (67, 80),
        "Filename"  : (787  , 738),
        "Save"      : (1344, 811),
        "SaveYes"   : (1020, 596)
    }
    ag.moveTo(*COORDS["File"], DELAY)           ; ag.click()
    ag.moveTo(*COORDS["RAW10"], DELAY)          ; ag.click()
    ag.moveTo(*COORDS["Filename"], DELAY*3)       ; ag.doubleClick()
    
    ag.typewrite(filenameinput, interval=TYPE_DELAY)
    ag.moveTo(*COORDS["Save"], DELAY)           ; ag.click()
    # Auto GUI
    
def spectrometer_auto_save(filenameinput):
    """
    Automate Thorlabs save
    Saving Spectrometer results from thorlabs
    """
    DELAY = 0.2
    TYPE_DELAY = 0.05/8
    COORDS = {
        "Asignal"   : (40, 153),
        "Asave"     : (109,533),
        "savetype"  : (156,549),
        "saveasCsv": (170, 580),
        "Filename"  : (154 , 514),
        "save_1"    : (756, 586),
        "save_ok"    : (969, 645)
    }
    ag.moveTo(*COORDS["Asignal"], DELAY)            ; ag.click()
    ag.moveTo(*COORDS["Asave"], DELAY)              ; ag.click()
    ag.moveTo(*COORDS["savetype"], DELAY)           ; ag.click()
    ag.moveTo(*COORDS["saveasCsv"], DELAY)          ; ag.click()
    ag.moveTo(*COORDS["Filename"], DELAY)           ; ag.click()
    ag.typewrite(filenameinput, interval=TYPE_DELAY)
    ag.moveTo(*COORDS["save_1"], DELAY)          ; ag.click()
    
    
    ag.moveTo(*COORDS["save_ok"], DELAY)           ; ag.click()
    # Auto GUI

def ocean_spectrometer_auto_save_old(filenameinput):
    """
    Automate Thorlabs save
    Saving Spectrometer results from thorlabs
    """

    drive, path = os.path.splitdrive(filenameinput)
    path, filename = os.path.split(path)
    DELAY = 0.2
    TYPE_DELAY = 0.05/8
    COORDS = {
        "Configוure_graph_saving"   : (645, 121),
        "Targt_Directory"     : (774,513),
        "Folder_Naming"  : (872,743),
        "Open": (1203, 743),
        "BaseName"  : (918 , 579),
        "Apply"    : (958, 766),
        "exit"    : (1288, 806),
        "Save_File"    : (599, 126)
    }
    ag.moveTo(*COORDS["Configוure_graph_saving"], DELAY)            ; ag.click()
    ag.moveTo(*COORDS["Targt_Directory"], DELAY)              ; ag.click()
    ag.moveTo(*COORDS["Folder_Naming"], DELAY)           ; ag.click()
    ag.typewrite(drive  +path, interval=TYPE_DELAY)
    ag.moveTo(*COORDS["Open"], DELAY)          ; ag.click()
    ag.moveTo(*COORDS["BaseName"], DELAY)           ; ag.click()
    for deletealot in range(25):
        ag.typewrite('\b\b', interval=TYPE_DELAY)
    ag.typewrite(filename, interval=TYPE_DELAY)
    ag.moveTo(*COORDS["Apply"], DELAY)           ; ag.click()
    ag.moveTo(*COORDS["exit"], DELAY)           ; ag.click()
    ag.moveTo(*COORDS["Save_File"], DELAY)          ; ag.click()
    
    
    # Auto GUI

def ocean_spectrometer_auto_save(filenameinput):
    """
    Oceanview version 2.0.14
    Automate oceanview save
    Saving Spectrometer results from oceanview
    """

    drive, path = os.path.splitdrive(filenameinput)
    path, filename = os.path.split(path)
    DELAY = 0.2
    TYPE_DELAY = 0.05/8
    COORDS = {
        "Configוure_graph_saving"   : (458, 155),
        "Targt_Directory"     : (741,423),
        "Folder_Naming"  : (827,579),
        "Open": (1141, 665),
        "BaseName"  : (958 , 536),
        "Apply"    : (958, 772),
        "exit"    : (1321, 810),
        "Save_File"    : (417, 154)
    }
    ag.moveTo(*COORDS["Configוure_graph_saving"], DELAY)            ; ag.click()
    ag.moveTo(*COORDS["Targt_Directory"], DELAY)              ; ag.click()
    ag.moveTo(*COORDS["Folder_Naming"], DELAY)           ; ag.click()
    ag.typewrite(drive  +path, interval=TYPE_DELAY)
    ag.moveTo(*COORDS["Open"], DELAY)          ; ag.click()
    ag.moveTo(*COORDS["BaseName"], DELAY)           ; ag.click()
    for deletealot in range(25):
        ag.typewrite('\b\b', interval=TYPE_DELAY)
    ag.typewrite(filename, interval=TYPE_DELAY)
    ag.moveTo(*COORDS["Apply"], DELAY)           ; ag.click()
    ag.moveTo(*COORDS["exit"], DELAY)           ; ag.click()
    ag.moveTo(*COORDS["Save_File"], DELAY)          ; ag.click()
    
def Ov5640_auto_save(filenameinput):
    """
    Automate sunny save
    Capture images at varying exposure durations.
    """
    DELAY = 0.2
    TYPE_DELAY = 0.05/8
    COORDS = {
        "Asignal"   : (948, 657),
        "Filename"     : (934,1006),
        "save_1"    : (1554, 1071),
    }
    ag.moveTo(*COORDS["Asignal"], DELAY)            ; ag.click()
    ag.moveTo(*COORDS["Filename"], DELAY)           ; ag.click()
    ag.typewrite(filenameinput, interval=TYPE_DELAY)
    ag.moveTo(*COORDS["save_1"], DELAY)          ; ag.click()
        # Auto GUI
       
def gui_notepad(args):
    """
    Example sequence.
    Before executing, open Notepad and maximize.
    """
    print("Moving mouse to tab, and clicking")
    ag.moveTo(270, 140, 1)
    ag.click()
    ag.hotkey("ctrl", "end")
    ag.press("enter")
    ag.typewrite("Hello everyone!")
    ag.press("enter")
    ag.typewrite("I am sentient")
    ag.hotkey("alt", "F")
    ag.hotkey("S")
    filename = os.path.join(args.dir, args.filename.format(make_timestamp()))
    ag.typewrite(filename)


# Register the sequences for CLI selection
SEQUENCES = {
        "gui_notepad": gui_notepad,
        "gui_stray_light" : gui_stray_light,
        }


### Classes and Core functions ###############################################

def display_mouse_location():
    """
    Show mouse coordinates.
    Useful for preparing sequences.
    """
    async def mouse_at():
        while True:
            print("Mouse at", ag.position(), "[ESC to stop]")
            if msvcrt.kbhit():
                ch = ord(msvcrt.getch())
                if ch == 27: break
            await asyncio.sleep(0.1)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(mouse_at())
    loop.close()

def make_timestamp():
    """
    Helper routing for generating unique identifiers.
    """
    return "{0:%y}-{0:%m}-{0:%d}T{0:%H}-{0:%M}-{0:%S}".format(datetime.datetime.now())


### Command Line Interface ###################################################
if __name__ == "__main__":

    ### CLI Option Parser ####################################################
    import argparse
    import sys

    desc = __doc__ + """\n
    """
    epi = """
    """

    # merge several help formatters
    class MyFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
        pass

    parser = argparse.ArgumentParser(description=desc, epilog=epi,
                                     formatter_class=MyFormatter)

    # options
    parser.add_argument("--sequence",
                        default=None,
                        type=str,
                        choices=SEQUENCES.keys(),
                        help="sequence to execute"
    )
    parser.add_argument("--filename",
                        default="test-{}.txt",
                        type=str,
                        help="filename format string for placing the timestamp"
    )
    parser.add_argument("--dir",
                        default=os.getcwd(),
                        type=str,
                        help="output directory"
    )
    parser.add_argument("--mouse",
                        default=False,
                        action="store_true",
                        help="display mouse coordinates"
    )
    # positional arguments

    ### argument validation ##################################################
    args = parser.parse_args()

    ### process ##############################################################
    if args.mouse:
        display_mouse_location()
        sys.exit(0)

    if args.sequence is not None:
        SEQUENCES[args.sequence](args)
    else:
        print("Select --sequence in: {}".format([k for k in SEQUENCES.keys()]))
