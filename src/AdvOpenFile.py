# The naming conventions follow those used in github.com/AstroDigitalVideo/ADVlib
# The Python code is closely modelled after the C# code written by Hristo Pavlov
# with the intent of matching names, semantics, and code flow as closely as
# possible. While not exactly 'Pythonic', it was my judgement (Bob Anderson) that
# fewer errors would be introduced and it would reduce the intellectual 'load' of comparing
# the well-tested C# code against its (supposedly) equivalent Python version.

from ctypes import *
from struct import unpack, pack
from dataclasses import dataclass

adv2lib = CDLL(r'..\AdvLib\AdvLib.Core64.dll')


# The 'dataclass' is equivalent to a struct in C#
# Here I've given initial values to all members to simplify creating a new copy.
# Some of the entries in the C# version are just byte values, but we lose nothing by using
# an int for those as a byte is always contained in an int.
@dataclass
class AdvFileInfo:
    Width: int = 0
    Height: int = 0
    CountMaintFrames: int = 0
    CountCalibrationFrames: int = 0
    DataBpp: int = 0
    MaxPixelValue: int = 0
    MainClockFrequency: c_int64 = 0
    MainStreamAccuracy: int = 0
    CalibrationClockFrequency: c_int64 = 0
    CalibrationStreamAccuracy: int = 0
    MainStreamTagsCount: int = 0
    CalibrationStreamTagsCount: int = 0
    SystemMetadataTagsCount: int = 0
    UserMetadataTagsCount: int = 0
    UtcTimestampAccuracyInNanoseconds: c_int64 = 0
    IsColourImage: bool = False
    ImageLayoutsCount: int = 0
    StatusTagsCount: int = 0
    ImageSectionTagsCount: int = 0
    ErrorStatusTagId: int = 0


def AdvOpenFile(filepath: str, fileinfo: AdvFileInfo) -> int:
    info_format = '6iQiQi4BQ?4i'
    # The above format specifies 6*int32 int64 int32 int64 4*uint8 int64 bool 4*uint32
    info_param = pack(info_format,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    file_path_as_bytes = bytes(filepath, 'utf-8')
    fname_ptr = c_char_p(file_path_as_bytes)  # fname_ptr: const char* fileName

    ret_val = adv2lib.AdvOpenFile(fname_ptr, c_char_p(info_param))

    # print(ret_val, ":".join("{:02x}".format(hh) for hh in info_param))
    fileinfo.Width = unpack(info_format, info_param)[0]
    fileinfo.Height = unpack(info_format, info_param)[1]
    fileinfo.CountMaintFrames = unpack(info_format, info_param)[2]
    fileinfo.CountCalibrationFrames = unpack(info_format, info_param)[3]
    fileinfo.DataBpp = unpack(info_format, info_param)[4]
    fileinfo.MaxPixelValue = unpack(info_format, info_param)[5]
    fileinfo.MainClockFrequency = unpack(info_format, info_param)[6]
    fileinfo.MainStreamAccuracy = unpack(info_format, info_param)[7]
    fileinfo.CalibrationClockFrequency = unpack(info_format, info_param)[8]
    fileinfo.CalibrationStreamAccuracy = unpack(info_format, info_param)[9]
    fileinfo.MainStreamTagsCount = unpack(info_format, info_param)[10]
    fileinfo.CalibrationStreamTagsCount = unpack(info_format, info_param)[11]
    fileinfo.SystemMetadataTagsCount = unpack(info_format, info_param)[12]
    fileinfo.UserMetadataTagsCount = unpack(info_format, info_param)[13]
    fileinfo.UtcTimestampAccuracyInNanoseconds = unpack(info_format, info_param)[14]
    fileinfo.IsColourImage = unpack(info_format, info_param)[15]
    fileinfo.ImageLayoutsCount = unpack(info_format, info_param)[16]
    fileinfo.StatusTagsCount = unpack(info_format, info_param)[17]
    fileinfo.ImageSectionTagsCount = unpack(info_format, info_param)[18]
    fileinfo.ErrorStatusTagId = unpack(info_format, info_param)[19]
    return ret_val


info_from_file = AdvFileInfo()
# print(info_from_file)

answer = AdvOpenFile(r'..\ver2-test-file.adv', info_from_file)

print(answer)
print(info_from_file)
import dataclasses
# for field in dataclasses.fields(info_from_file):
#     print(field.name)
bob = dataclasses.asdict(info_from_file)
print(bob)
for item in bob:
    # if bob[item] is not 0:
    print(f'{item:>35} {bob[item]}')