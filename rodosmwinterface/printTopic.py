#!/bin/python3
# rodos-middleware: This file is a part of the Master Thesis of Sebastian Kind 2023

import struct

import os
import atexit
import subprocess
import sys
import signal
import traceback

from .topic import *

g_mw_print_enabled = True
g_single_terminal_logging = False
g_logging_enabled = False
g_logfile_name = "./RODOS_LogFile.txt"



_single_terminal_opened = False
fileList = []
subProcessThreadIdList = []
plist = []



def closeFiles():
    for k in thread2fifoDict:
        try:
            os.remove(thread2fifoDict[k]) # remove FIFOs/named pipes
        except FileNotFoundError:
            pass
    for p in plist: #terminate monitors e.g. xterm
        p.terminate()
        p.kill()

atexit.register(closeFiles)

def sigHandler(signo, frame):
    closeFiles()
    sys.exit(0)

signal.signal(signal.SIGTERM, sigHandler)


thread2fifoDict = {}
def getOrCreateFIFO(threadID: int) -> str:
    """

    :param threadID: unique ID of a C++RODOS-Thread that is printing something. This is ID is used to create a unique
    FIFO(named pipe) that collects the thread's debug output
    :return: return the filename of the FIFO, relative path for now
    """
    if threadID not in thread2fifoDict:
        #thread not known, add it to the dict
        FIFOName = "./RodosThread"+str(threadID)
        try:
            os.remove(FIFOName)
        except FileNotFoundError:
            pass
        os.mkfifo(FIFOName, 0o666)
        thread2fifoDict[threadID] = FIFOName
        #thread known or added
    return thread2fifoDict[threadID]


def openMonitor(threadID: int, fifoName: str):
    """
    Open a new monitor window using xterm to display the content of a specified FIFO (Named Pipe).

    Parameters:
    - threadID (int): Unique identifier for the thread associated with the monitor, usually memory address of thread
                      in rodos (c++) memory space
    - fifoName (str): The name of the FIFO (Named Pipe) whose content will be displayed in the monitor.

    If the monitor for the specified threadID already exists (checked against `subProcessThreadIdList`),
    the function returns without creating a new monitor. Otherwise, it appends the threadID to the list,
    constructs the command to run (using 'tail -f' to continuously display new content in the monitor),
    and spawns a subprocess to open an xterm window running the specified command.

    The subprocess object is added to the global `plist` list to ensure it can be closed on program exit.

    Note:
    - This function relies on the global variables `subProcessThreadIdList` and `plist`.
    - Ensure that the FIFO specified by `fifoName` exists before calling this function.

    """
    if _single_terminal_opened: #side effect of another function
        return
    if threadID in subProcessThreadIdList:
        return

    subProcessThreadIdList.append(threadID)
    command_to_run = "xterm -e 'tail -f {}' &".format(fifoName)
    proc = subprocess.Popen(command_to_run, shell=True)

    plist.append(proc) # close it on exit



def _print_topic_handler(data):
    """
    :param data: called by caller of callback
    :return: nothing

    print_topic_handler get a variable length structure with leading 8 bytes of metadata, first uint32 denoting the
    sending thread, second uint32 containing the length of the whole print-message including the metadata. The actual
    print message starts at the 9th byte (index 8)

    each thread should get its own named pipe/serial monitor/whatever to list show the output in a terminal
    """

    try:
        unpacked = struct.unpack("ii", bytes(data[:8]))

       # print("id =", unpacked[0], "length = ", unpacked[1])
        threadID = unpacked[0]
        length = unpacked[1]


        fifoName = getOrCreateFIFO(threadID)
        #print("printtopic data:", data[8:length+8])

        openMonitor(threadID, fifoName)

        try:
            with open(fifoName, "wb") as fifo:
                fifo.write(data[8:length + 8])
        except Exception as e:
            print(f"Error writing to FIFO: {e}")
    except Exception as error:
        print("printtopic exception", type(error).__name__)

        traceback.print_exc()
    pass

def _print_topic_handler_single_terminal(data):
    """
    :param data: called by caller of callback
    :return: nothing

    print_topic_handler get a variable length structure with leading 8 bytes of metadata, first uint32 denoting the
    sending thread, second uint32 containing the length of the whole print-message including the metadata. The actual
    print message starts at the 9th byte (index 8)

    each thread should get its own named pipe/serial monitor/whatever to list show the output in a terminal
    """
    global _single_terminal_opened
    nameString = "RODOS_OUTPUT"
    fifoName = getOrCreateFIFO(nameString)

    try:
        unpacked = struct.unpack("ii", bytes(data[:8]))
        threadID = unpacked[0]
        length = unpacked[1]
        openMonitor(threadID, fifoName)
        _single_terminal_opened = True
        try:
            with open(fifoName, "wb") as fifo:
                fifo.write(data[8:length + 8])
        except Exception as e:
            print(f"Error writing to FIFO: {e}")
    except Exception as error:
        print("printtopic exception:", type(error).__name__)

        traceback.print_exc()
    pass


def _print_topic_handler_logfile_only(data):
    """
    :param data: called by caller of callback
    :return: nothing

    print_topic_handler get a variable length structure with leading 8 bytes of metadata, first uint32 denoting the
    sending thread, second uint32 containing the length of the whole print-message including the metadata. The actual
    print message starts at the 9th byte (index 8)
    """

    try:
        unpacked = struct.unpack("ii", bytes(data[:8]))
        threadID = unpacked[0]
        length = unpacked[1]

        try:
            #open logfile
            with open(g_logfile_name, "ab") as logfile:
                logfile.write(data[8:length + 8])
        except Exception as e:
            print(f"Error writing to logfile({g_logfile_name}): {e} ")
    except Exception as error:
        print("printtopic exception:", type(error).__name__)

        traceback.print_exc()
    pass


__g_print_topic = Topic(11)

def printTopicInit(single_terminal=False, enable=True, enable_log_file=False, log_file_path=""):
    """
    enabled: is set True by default
    """
    global g_single_terminal_logging
    global g_mw_print_enabled
    global __g_print_topic
    g_single_terminal_logging = single_terminal
    g_mw_print_enabled = enable
    if enable_log_file:
        global g_logging_enabled
        g_logging_enabled = enable_log_file
        __g_print_topic.addSubscriber(_print_topic_handler_logfile_only)
    if g_single_terminal_logging:
        __g_print_topic.addSubscriber(_print_topic_handler_single_terminal)
    elif g_mw_print_enabled:
        __g_print_topic.addSubscriber(_print_topic_handler)

    else:
        #No logging
        pass

