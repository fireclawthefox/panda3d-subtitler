import logging
from enum import Enum
from datetime import datetime

def helper_ConvertDoubleToSrtTimeString(double_t):
    # calculate the time parts
    t = double_t
    h = int(t // 3600)
    t %= 3600
    m = int(t // 60)
    t %= 60
    s = int(t)
    t %= 1
    ms = int(t * 1000)

    # build the string to convert
    return "{:01d}:{:02d}:{:02d},{:03d}".format(h,m,s,ms)

def helper_ConvertTimeDouble(double_t):
    # build the string to convert
    string_t = helper_ConvertDoubleToSrtTimeString(double_t)
    return helper_ConvertTime(string_t)

def helper_ConvertTime(string_t):
    """Convert a string of the usual SRT Time format to datetime"""
    return datetime.strptime(string_t, "%H:%M:%S,%f")

class SRTSubtitleElement:
    # The subtitle elements index in the SRT file
    index=0
    # Start time
    start_t=None
    # End time
    end_t=None
    # The actual subtitle text
    text=""

class SRTSubtitleReader:
    class SRTLineType(Enum):
        INDEX = 1
        TIME = 2
        TEXT = 3

    def __init__(self):
        self.subtitleElements = []

    def read(self, srtFilename):
        """Read the given SRT file into the memory"""
        lineType = self.SRTLineType.INDEX
        with open(srtFilename, "r") as srtFile:
            for line in srtFile:
                line = line.strip()
                if lineType is self.SRTLineType.INDEX:
                    # skip empty lines if we search for an index
                    if line == "": continue
                    subtitleElement = SRTSubtitleElement()
                    subtitleElement.index = int(line)
                    # Move to the next line type, which must be the time
                    lineType = self.SRTLineType.TIME

                elif lineType is self.SRTLineType.TIME:
                    # split up the line in its indivdual time parts
                    start,end = line.split(" --> ")

                    # convert start and end time
                    subtitleElement.start_t = helper_ConvertTime(start)
                    subtitleElement.end_t = helper_ConvertTime(end)

                    # Move to the next line type, which must be the text
                    lineType = self.SRTLineType.TEXT

                elif lineType is self.SRTLineType.TEXT:
                    if line:
                        if subtitleElement.text == "":
                            subtitleElement.text = line
                        else:
                            subtitleElement.text = "{}\n{}".format(subtitleElement.text, line)
                    else:
                        # empty line, store the element and move back to index
                        self.subtitleElements.append(subtitleElement)
                        lineType = self.SRTLineType.INDEX

class SRTSubtitle:
    def __init__(self):
        self.reader = SRTSubtitleReader()

    def open(self, srtFilename):
        self.reader.read(srtFilename)

    def findSubtitleElement(self, index=-1, start_t=None, cur_t=None):
        for element in self.reader.subtitleElements:
            if cur_t is not None:
                if cur_t >= element.start_t and cur_t <= element.end_t: return element
            if index > -1:
                if element.index == index: return element
            elif start_t is not None:
                if element.start_t == start_t: return element
        logging.debug("Couldn't find an element at index:{} or start time:{}".format(index, start_t))
        return None

    def getSubtitleText(self, index=-1, start_t=None, cur_t=None):
        """Returns the subtitles text at the given position"""
        element = self.findSubtitleElement(index, start_t, cur_t)
        if element != None:
            return element.text
        return None

    def getSubtitleIndex(self, start_t=None, cur_t=None):
        """If the element is available, return the index as integer
        of the subtitle at the given position, else returns -1"""
        element = self.findSubtitleElement(start_t=start_t, cur_t=cur_t)
        if element != None:
            return element.index
        return -1

    def getSubtitleDuration(self, index=-1, start_t=None, cur_t=None):
        """If the element is available, return a datetime.timedelta
        object containing the duration of the subtitle at the given
        position, else returns None"""
        element = self.findSubtitleElement(index, start_t, cur_t)
        if element != None:
            return element.end_t - element.start_t
        return None

    def getSubtitleStartT(self, index=-1, cur_t=None):
        """If the element is available, return a datetime.datetime
        object containing the start time of the subtitle at the given
        position, else returns None"""
        element = self.findSubtitleElement(index, cur_t=cur_t)
        if element != None:
            return element.start_t
        return None

    def getSubtitleEndT(self, index=-1, start_t=None, cur_t=None):
        """If the element is available, return a datetime.datetime
        object containing the end time of the subtitle at the given
        start position, else returns None"""
        element = self.findSubtitleElement(index, start_t, cur_t)
        if element != None:
            return element.start_t
        return None
