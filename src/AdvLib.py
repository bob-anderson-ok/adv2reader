# The naming conventions follow those used in github.com/AstroDigitalVideo/ADVlib
# The Python code is closely modelled after the C# code written by Hristo Pavlov
# with the intent of matching names, semantics, and code flow as closely as
# possible. While not exactly 'Pythonic', it was my judgement (Bob Anderson) that
# fewer errors would be introduced and it would reduce the intellectual 'load' of comparing
# the well-tested C# code against its (supposedly) equivalent Python version.

# This module holds all of the static methods that are defined
# in the C# file PInvoke.cs via 'public static class AdvLib' (this is the pythonic equivalent)

from src.Adv import *
from ctypes import *
from struct import unpack, pack
import platform

# The following tests will run at import time (startup) and raise/throw an exception if we can cannot
# distinguish Windows 64bit/32bit from Mac 64bit/32bit from Linux 64bit/32bit.  We
# make that event a fatal error.
if platform.system().lower().startswith('windows'):
    # We're running on a on a Windows system
    if platform.architecture()[0] == '64bit':
        advDLL = CDLL(r'..\AdvLib\AdvLib.Core64.dll')
    elif platform.architecture()[0] == '32bit':
        advDLL = CDLL(r'..\AdvLib\AdvLib.Core32.dll')
    else:
        raise ImportWarning("System is neither 64 bit nor 32 bit.")
elif platform.system().lower().startswith('darwin'):
    # We're running on MacOS
    if platform.architecture()[0] == '64bit':
        advDLL = CDLL(r'..\AdvLib\AdvLibMac.Core64.dll')
    elif platform.architecture()[0] == '32bit':
        advDLL = CDLL(r'..\AdvLib\AdvLibMac.Core32.dll')
    else:
        raise ImportWarning("System is neither 64 bit nor 32 bit.")
elif platform.system().lower().startswith('linux'):
    # We're running on a linux system
    if platform.architecture()[0] == '64bit':
        advDLL = CDLL(r'..\AdvLib\AdvLibLinux.Core64.dll')
    elif platform.architecture()[0] == '32bit':
        advDLL = CDLL(r'..\AdvLib\AdvLibLinux.Core32.dll')
    else:
        raise ImportWarning("System is neither 64 bit nor 32 bit.")


def OpenFile(filepath: str, fileinfo: AdvFileInfo) -> int:
    info_format = '6iQiQi4BQ?4i'
    # The above format specifies 6*int32 int64 int32 int64 4*uint8 int64 bool 4*uint32
    # Create a structure per the supplied format string
    file_info = pack(info_format,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    file_path_as_bytes = bytes(filepath, 'utf-8')
    fname_ptr = c_char_p(file_path_as_bytes)  # fname_ptr: const char* fileName

    ret_val = advDLL.AdvOpenFile(fname_ptr, c_char_p(file_info))

    fileinfo.Width = unpack(info_format, file_info)[0]
    fileinfo.Height = unpack(info_format, file_info)[1]
    fileinfo.CountMaintFrames = unpack(info_format, file_info)[2]
    fileinfo.CountCalibrationFrames = unpack(info_format, file_info)[3]
    fileinfo.DataBpp = unpack(info_format, file_info)[4]
    fileinfo.MaxPixelValue = unpack(info_format, file_info)[5]
    fileinfo.MainClockFrequency = unpack(info_format, file_info)[6]
    fileinfo.MainStreamAccuracy = unpack(info_format, file_info)[7]
    fileinfo.CalibrationClockFrequency = unpack(info_format, file_info)[8]
    fileinfo.CalibrationStreamAccuracy = unpack(info_format, file_info)[9]
    fileinfo.MainStreamTagsCount = unpack(info_format, file_info)[10]
    fileinfo.CalibrationStreamTagsCount = unpack(info_format, file_info)[11]
    fileinfo.SystemMetadataTagsCount = unpack(info_format, file_info)[12]
    fileinfo.UserMetadataTagsCount = unpack(info_format, file_info)[13]
    fileinfo.UtcTimestampAccuracyInNanoseconds = unpack(info_format, file_info)[14]
    fileinfo.IsColourImage = unpack(info_format, file_info)[15]
    fileinfo.ImageLayoutsCount = unpack(info_format, file_info)[16]
    fileinfo.StatusTagsCount = unpack(info_format, file_info)[17]
    fileinfo.ImageSectionTagsCount = unpack(info_format, file_info)[18]
    fileinfo.ErrorStatusTagId = unpack(info_format, file_info)[19]
    return ret_val
