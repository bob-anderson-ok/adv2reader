# The naming conventions follow those used in github.com/AstroDigitalVideo/ADVlib
# While not exactly 'Pythonic' (i.e., not snake case), it was my judgement (Bob Anderson) that
# fewer errors would be introduced and would reduce the intellectual 'load' of comparing
# the Python code against the equivalent code in github.com/AstroDigitalVideo/ADVlib

# We use type hinting so that it is easy to see the intent as matching the C++/C# code

# This module holds all of the static methods that are defined
# in the C# file PInvoke.cs via 'public static class Adv2DLLlibs' (the pythonic equivalent is
# a module with the methods defined at the top level)

from Adv import *
from ctypes import *
from struct import unpack, pack
import platform
import pathlib

# The following tests will run at import time (startup) and raise/throw an exception if we can cannot
# distinguish Windows 64bit/32bit from Mac 64bit/32bit from Linux 64bit/32bit or find libraries.  We
# allow such an event to be a fatal error.

if platform.system().lower().startswith('windows'):
    # We're running on a on a Windows system
    if platform.architecture()[0] == '64bit':
        advDLL = CDLL(r'..\Adv2DLLlibs\AdvLib.Core64.dll')
    elif platform.architecture()[0] == '32bit':
        advDLL = CDLL(r'..\Adv2DLLlibs\AdvLib.Core32.dll')
    else:
        raise ImportWarning("System is neither 64 bit nor 32 bit.")
elif platform.system().lower().startswith('darwin'):
    # We're running on MacOS
    if platform.architecture()[0] == '64bit':
        advDLL = CDLL(r'..\Adv2DLLlibs\AdvLibMac.Core64.dll')
    elif platform.architecture()[0] == '32bit':
        advDLL = CDLL(r'..\Adv2DLLlibs\AdvLibMac.Core32.dll')
    else:
        raise ImportWarning("System is neither 64 bit nor 32 bit.")
elif platform.system().lower().startswith('linux'):
    # We're running on a linux system
    if platform.architecture()[0] == '64bit':
        advDLL = CDLL(r'..\Adv2DLLlibs\AdvLibLinux.Core64.dll')
    elif platform.architecture()[0] == '32bit':
        advDLL = CDLL(r'..\Adv2DLLlibs\AdvLibLinux.Core32.dll')
    else:
        raise ImportWarning("System is neither 64 bit nor 32 bit.")


def AdvOpenFile(filepath: str, fileinfo: AdvFileInfo) -> int:
    advFileInfoFormat = '6iQiQi4BQ?4i'  # format of AdvFileInfo structure
    # The above format specifies 6*int32 int64 int32 int64 4*uint8 int64 bool 4*uint32
    # Create a c style structure per the supplied format string
    file_info = pack(advFileInfoFormat,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    file_path_as_bytes = bytes(filepath, 'utf-8')
    fname_ptr = c_char_p(file_path_as_bytes)  # fname_ptr equivalent to: const char* fileName

    ret_val = advDLL.AdvOpenFile(fname_ptr, c_char_p(file_info))

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
    return ret_val


def AdvCloseFile() -> int:
    ret_val = advDLL.AdvCloseFile()
    return ret_val


def AdvGetFileVersion(filepath: str) -> (str, int):
    if not pathlib.Path(filepath).is_file():
        return f'Error - cannot find file: {filepath}', 0
    else:
        file_path_as_bytes = bytes(filepath, 'utf-8')
        fname_ptr = c_char_p(file_path_as_bytes)  # fname_ptr: const char* fileName
        version_num = advDLL.AdvGetFileVersion(fname_ptr)
        if version_num == 0:
            return f'Error - not an FSTF file: {filepath}', 0
        else:
            return '', version_num


def AdvVer2_GetFramePixels(streamId: StreamId, frameNo: int,
                           pixels: Array, frameInfo: AdvFrameInfo, systemErrorLen: int) -> int:
    advFrameInfoFormat = '7I4f3Bb8I'
    frame_info = pack(advFrameInfoFormat, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

    ret_val = advDLL.AdvVer2_GetFramePixels(c_int(streamId.value), c_int(frameNo), pixels,
                                            c_char_p(frame_info), byref(c_int(systemErrorLen)))

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

    return ret_val
