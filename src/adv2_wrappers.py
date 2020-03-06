from ctypes import *
import os
import struct

adv2lib = CDLL(r'..\AdvLib\AdvLib.Core64.dll')

# Format string that defines the AdvFileInfo structure
# native byte order: int16(6 times) int32 int16 int32 int16 char(4 times) int32 bool int16(4 times)
# fileInfoStructFormat = '6HLHLH4BL?4H'
# fileInfoStructFormat = '6HLHLH4BL?4H'


def AdvGetFileVersion(filepath: str) -> (str, int):
    if not os.path.isfile(filepath):
        return f'Error: cannot find file ... {filepath}', 0
    else:
        file_path_as_bytes = bytes(filepath, 'utf-8')
        fname_ptr = c_char_p(file_path_as_bytes)  # fname_ptr: const char* fileName
        version_num = adv2lib.AdvGetFileVersion(fname_ptr)
        if version_num == 0:
            return f'Error: not an FSTF file ... {filepath}', 0
        else:
            return '', version_num


fileInfoStructFormat = '6iQiQi4BQ?4H'

fileInfo = struct.pack(fileInfoStructFormat,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
print('1', fileInfo)

file_path_as_bytes2 = bytes(r'..\ver2-test-file.adv', 'utf-8')
print('2', id(file_path_as_bytes2))
fname_ptr2 = c_char_p(file_path_as_bytes2)  # fname_ptr: const char* fileName
print('3', fname_ptr2)
print('4', id(fileInfo))
print('5', c_char_p(fileInfo))
print('6', adv2lib.AdvOpenFile(fname_ptr2, c_char_p(fileInfo)))
print('7', ":".join("{:02x}".format(hh) for hh in fileInfo))
width, height, frameCount, calFrameCount, dataBpp, maxpix, clk, acc, calfreq, cals,\
 tcount, cscount, mtcount, umcount, utc, iscolor, imlaycount, statuscount, \
 imgsectag, errtagid = struct.unpack(fileInfoStructFormat, fileInfo)
print(width, height, frameCount, calFrameCount, dataBpp, maxpix)
print(clk, acc, calfreq, cals, tcount, cscount, mtcount, umcount, utc)
print(iscolor, imlaycount, statuscount, imgsectag, errtagid)
