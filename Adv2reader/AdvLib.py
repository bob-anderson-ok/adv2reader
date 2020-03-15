# The naming conventions follow those used in github.com/AstroDigitalVideo/ADVlib
# While not exactly 'Pythonic' (i.e., not snake case), it was my judgement (Bob Anderson) that
# fewer errors would be introduced and would reduce the intellectual 'load' of comparing
# the Python code against the equivalent code in github.com/AstroDigitalVideo/ADVlib

# We use type hinting so that it is easy to see the intent as matching the C++/C# code

# This module holds the relevant static methods (i.e., involved in reading a file as opposed
# to writing a file) that are defined in the C# file PInvoke.cs via
# 'public static class Adv2DLLlibs' (the pythonic equivalent is
# a module with the methods defined at the top level, such as this)

import os
import pathlib
import platform
from ctypes import CDLL, byref, c_char_p, c_int, c_uint
from struct import pack, unpack
from typing import Tuple

from Adv import AdvFileInfo, AdvFrameInfo, StreamId, TagPairType

print(os.getcwd())


# The following code/tests will run at import time (startup) and raise/throw an exception if we can cannot
# distinguish Windows 64bit/32bit from Mac 64bit/32bit from Linux 64bit/32bit or find libraries.  We
# allow such an event to be a fatal error.

if platform.system().lower().startswith('windows'):
    # We're running on a on a Windows system
    if platform.architecture()[0] == '64bit':
        # The following line generates a platform agnostic filepath (deals with / \ issues)
        file_path = str(pathlib.Path('../Adv2DLLlibs/AdvLib.Core64.dll'))
        advDLL = CDLL(file_path)
    elif platform.architecture()[0] == '32bit':
        file_path = str(pathlib.Path('../Adv2DLLlibs/AdvLib.Core32.dll'))
        advDLL = CDLL(file_path)
    else:
        raise ImportError("System is neither 64 bit nor 32 bit.")
elif platform.system().lower().startswith('darwin'):
    # We're running on MacOS
    if platform.architecture()[0] == '64bit':
        # The following line generates a platform agnostic filepath (deals with / \ issues)
        file_path = str(pathlib.Path('../Adv2DLLlibs/libAdvCore.dylib'))
        advDLL = CDLL(file_path)
    elif platform.architecture()[0] == '32bit':
        raise ImportError("No 32 bit library available for MacOS")
    else:
        raise ImportError("System is neither 64 bit nor 32 bit.")
elif platform.system().lower().startswith('linux'):
    # We're running on a linux system
    if platform.architecture()[0] == '64bit':
        # The following line generates a platform agnostic filepath (deals with / \ issues)
        file_path = str(pathlib.Path('../Adv2DLLlibs/libAdvCore64.so'))
        advDLL = CDLL(file_path)
    elif platform.architecture()[0] == '32bit':
        # The following line generates a platform agnostic filepath (deals with / \ issues)
        file_path = str(pathlib.Path('../Adv2DLLlibs/libAdvCore32.so'))
        advDLL = CDLL(file_path)
    else:
        raise ImportError("System is neither 64 bit nor 32 bit.")


def AdvOpenFile(filepath: str, fileinfo: AdvFileInfo) -> int:
    advFileInfoFormat = '6iQiQi4BQ?4i'  # format of AdvFileInfo structure needed by pack() and unpack()
    # The above format specifies 6*int32 int64 int32 int64 4*uint8 int64 bool 4*uint32

    # Create a C style structure per the supplied format string
    file_info = pack(advFileInfoFormat,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

    # Convert the Python string to an array of bytes (with null terminator)
    file_path_as_bytes = bytes(filepath + '\0', 'utf-8')
    fname_ptr = c_char_p(file_path_as_bytes)  # fname_ptr equivalent to: const char* fileName

    # Call into the library with C-compatible arguments
    ret_val = advDLL.AdvOpenFile(fname_ptr, c_char_p(file_info))

    # Extract the entries from the the C struct file_info into the Python structure fileInfo
    fileinfo.Width = unpack(advFileInfoFormat, file_info)[0]
    fileinfo.Height = unpack(advFileInfoFormat, file_info)[1]
    fileinfo.CountMainFrames = unpack(advFileInfoFormat, file_info)[2]
    fileinfo.CountCalibrationFrames = unpack(advFileInfoFormat, file_info)[3]
    fileinfo.DataBpp = unpack(advFileInfoFormat, file_info)[4]
    fileinfo.MaxPixelValue = unpack(advFileInfoFormat, file_info)[5]
    fileinfo.MainClockFrequency = unpack(advFileInfoFormat, file_info)[6]
    fileinfo.MainStreamAccuracy = unpack(advFileInfoFormat, file_info)[7]
    fileinfo.CalibrationClockFrequency = unpack(advFileInfoFormat, file_info)[8]
    fileinfo.CalibrationStreamAccuracy = unpack(advFileInfoFormat, file_info)[9]
    fileinfo.MainStreamTagsCount = unpack(advFileInfoFormat, file_info)[10]
    fileinfo.CalibrationStreamTagsCount = unpack(advFileInfoFormat, file_info)[11]
    fileinfo.SystemMetadataTagsCount = unpack(advFileInfoFormat, file_info)[12]
    fileinfo.UserMetadataTagsCount = unpack(advFileInfoFormat, file_info)[13]
    fileinfo.UtcTimestampAccuracyInNanoseconds = unpack(advFileInfoFormat, file_info)[14]
    fileinfo.IsColourImage = unpack(advFileInfoFormat, file_info)[15]
    fileinfo.ImageLayoutsCount = unpack(advFileInfoFormat, file_info)[16]
    fileinfo.StatusTagsCount = unpack(advFileInfoFormat, file_info)[17]
    fileinfo.ImageSectionTagsCount = unpack(advFileInfoFormat, file_info)[18]
    fileinfo.ErrorStatusTagId = unpack(advFileInfoFormat, file_info)[19]

    # ret_val is an int32.  We need to remove the sign-extension that happens during the int64 conversion
    return ret_val & 0xffffffff


def AdvCloseFile() -> int:
    ret_val = advDLL.AdvCloseFile()

    # ret_val is an int32.  We need to remove the sign-extension that happens during the int64 conversion
    return ret_val & 0xffffffff


def AdvGetFileVersion(filepath: str) -> Tuple[str, int]:
    if not pathlib.Path(filepath).is_file():
        return f'Error - cannot find file: {filepath}', 0
    else:
        # Convert the Python string to an array of bytes (with null terminator)
        file_path_as_bytes = bytes(filepath + '\0', 'utf-8')
        fname_ptr = c_char_p(file_path_as_bytes)  # fname_ptr: const char* fileName

        version_num = advDLL.AdvGetFileVersion(fname_ptr)

        if version_num == 0:
            return f'Error - not an FSTF file: {filepath}', 0
        else:
            return '', version_num


def AdvVer2_GetFramePixels(streamId: StreamId, frameNo: int,
                           pixels: c_uint, frameInfo: AdvFrameInfo, systemErrorLen: int) -> int:

    advFrameInfoFormat = '7I4f3Bb8I'  # format of AdvFrameInfo needed by pack() and unpack()
    # The above format specifies 7 * uint32 4 * float32 3 * uchar char 8 * uint32
    # Create a C style structure per the supplied format string
    frame_info = pack(advFrameInfoFormat, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

    # Call into the library will C-compatible arguments
    ret_val = advDLL.AdvVer2_GetFramePixels(c_int(streamId.value), c_int(frameNo), pixels,
                                            c_char_p(frame_info), byref(c_int(systemErrorLen)))

    # Unpack the C struct frame_info into the Python struct frameInfo
    frameInfo.StartTicksLo = unpack(advFrameInfoFormat, frame_info)[0]
    frameInfo.StartTicksHi = unpack(advFrameInfoFormat, frame_info)[1]
    frameInfo.EndTicksLo = unpack(advFrameInfoFormat, frame_info)[2]
    frameInfo.EndTicksHi = unpack(advFrameInfoFormat, frame_info)[3]

    frameInfo.UtcMidExposureTimestampLo = unpack(advFrameInfoFormat, frame_info)[4]
    frameInfo.UtcMidExposureTimestampHi = unpack(advFrameInfoFormat, frame_info)[5]
    frameInfo.Exposure = unpack(advFrameInfoFormat, frame_info)[6]

    frameInfo.Gamma = unpack(advFrameInfoFormat, frame_info)[7]
    frameInfo.Gain = unpack(advFrameInfoFormat, frame_info)[8]
    frameInfo.Shutter = unpack(advFrameInfoFormat, frame_info)[9]
    frameInfo.Offset = unpack(advFrameInfoFormat, frame_info)[10]

    frameInfo.GPSTrackedSatellites = unpack(advFrameInfoFormat, frame_info)[11]
    frameInfo.GPSAlmanacStatus = unpack(advFrameInfoFormat, frame_info)[12]
    frameInfo.GPSFixStatus = unpack(advFrameInfoFormat, frame_info)[13]
    frameInfo.GPSAlmanacOffset = unpack(advFrameInfoFormat, frame_info)[14]

    frameInfo.VideoCameraFrameIdLo = unpack(advFrameInfoFormat, frame_info)[15]
    frameInfo.VideoCameraFrameIdHi = unpack(advFrameInfoFormat, frame_info)[16]
    frameInfo.HardwareTimerFrameIdLo = unpack(advFrameInfoFormat, frame_info)[17]
    frameInfo.HardwareTimerFrameIdHi = unpack(advFrameInfoFormat, frame_info)[18]

    frameInfo.SystemTimestampLo = unpack(advFrameInfoFormat, frame_info)[19]
    frameInfo.SystemTimestampHi = unpack(advFrameInfoFormat, frame_info)[20]

    frameInfo.ImageLayoutId = unpack(advFrameInfoFormat, frame_info)[21]
    frameInfo.RawDataBlockSize = unpack(advFrameInfoFormat, frame_info)[22]

    # ret_val is an int32.  We need to remove the sign-extension that happens during the int64 conversion
    return ret_val & 0xffffffff


def AdvVer2_GetTagPairValues(tagPairType: TagPairType, tagId: int) -> Tuple[int, str, str]:
    # Create big buffers of bytes to hold char string returns
    tagName = bytes('\0' * 256, 'utf8')
    tagValue = bytes('\0' * 256, 'utf8')
    ret_val = advDLL.AdvVer2_GetTagPairValues(
        c_int(tagPairType.value),
        c_int(tagId),
        c_char_p(tagName),
        c_char_p(tagValue)
    )
    tag_name_as_python_string = tagName.decode().strip('\0')    # This removes the null bytes
    tag_value_as_python_string = tagValue.decode().strip('\0')  # This removes the null bytes

    # ret_val is an int32.  We need to remove the sign-extension that happens during the int64 conversion
    return ret_val & 0xffffffff, tag_name_as_python_string, tag_value_as_python_string


def AdvVer2_GetIndexEntries(mainIndex, calibrationIndex) -> int:
    ret_val = advDLL.AdvVer2_GetIndexEntries(mainIndex, calibrationIndex)
    # ret_val is an int32.  We need to remove the sign-extension that happens during the int64 conversion
    return ret_val & 0xffffffff

def GetLibraryVersion() -> str:
    libVer = bytes('\0' * 256, 'utf8')
    advDLL.GetLibraryVersion(c_char_p(libVer))
    return libVer.decode().strip('\0')

def GetLibraryPlatformId() -> str:
    platform = bytes('\0' * 256, 'utf8')
    advDLL.GetLibraryPlatformId(c_char_p(platform))
    return platform.decode().strip('\0')

def GetLibraryBitness() -> int:
    ret_val = advDLL.GetLibraryBitness()
    return ret_val
