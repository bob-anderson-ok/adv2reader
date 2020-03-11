# The naming conventions follow those used in github.com/AstroDigitalVideo/ADVlib
# While not exactly 'Pythonic' (i.e., not snake case), it was my judgement (Bob Anderson) that
# fewer errors would be introduced and would reduce the intellectual 'load' of comparing
# the Python code against the equivalent code in github.com/AstroDigitalVideo/ADVlib

# We use type hinting so that it is easy to see the intent as matching the C++ code

from typing import Tuple
from Adv import *
import AdvLib
import AdvError
from AdvError import AdvLibException
import os
from ctypes import *
import numpy as np


# @dataclass
# class DataStreamDefinition:
#     FrameCount: int = 0
#     ClockFrequency: int = 0  # Python ints can hold an int64
#     TimingAccuracy: int = 0
#     MetaDataTags: Dict[str, str] = field(default_factory=dict)
#
#
# @dataclass
# class ImageLayoutDefinition:
#     LayoutId: int = 0
#     Bpp: int = 0
#     ImageLayoutTags: Dict[str, str] = field(default_factory=dict)


class Adv2reader:
    def __init__(self, filename: str):
        if not os.path.isfile(filename):
            raise AdvLibException(f'Error: cannot find file ... {filename}')

        fileInfo = AdvFileInfo()
        fileVersionErrorCode = AdvLib.AdvOpenFile(filename, fileInfo)

        if fileVersionErrorCode > 0x70000000:
            raise AdvLibException(f'There was an error opening {filename}: '
                                  f'{AdvError.ResolveErrorMessage(fileVersionErrorCode)}')
        if not fileVersionErrorCode == 2:
            raise AdvLibException(f'{filename} is not an ADV version 2 file')

        self.Width = fileInfo.Width
        self.Height = fileInfo.Height
        self.CountMainFrames = fileInfo.CountMainFrames

        self.FileInfo = fileInfo

        # Create an array of c_uint to hold the pixel values
        # TODO Adapt to colour required
        self.pixels = (c_uint * (fileInfo.Width * fileInfo.Height))()
        self.sysErrLength: int = 0
        self.frameInfo = AdvFrameInfo()

    def getMainImageData(self, frameNumber: int) -> Tuple[str, Array, AdvFrameInfo]:
        err_msg = ''

        ret_val = AdvLib.AdvVer2_GetFramePixels(
            streamId=StreamId.Main, frameNo=frameNumber,
            pixels=self.pixels, frameInfo=self.frameInfo, systemErrorLen=self.sysErrLength
        )
        if not ret_val == AdvError.S_OK:
            err_msg = AdvError.ResolveErrorMessage(ret_val)
            return err_msg, self.pixels, self.frameInfo

        return err_msg, self.pixels, self.frameInfo

    @staticmethod
    def closeFile():
        return AdvLib.AdvCloseFile()


rdr = None
try:
    rdr = Adv2reader(r'..\ver2-test-file.adv')
except AdvLibException as adverr:
    print(repr(adverr))
    exit()

print(f'Width: {rdr.Width}  Height: {rdr.Height}  NumMainFrames: {rdr.CountMainFrames}')

for frame in range(rdr.CountMainFrames):
    err, image, frameInfo = rdr.getMainImageData(frameNumber=frame)

    if not err:
        print(f'\nframe: {frame}')
        print(frameInfo.UtcMidExposureTimestampLo)
        print(frameInfo.UtcMidExposureTimestampHi)
        print(np.min(image), np.max(image), np.mean(image))

print('SysMetaNum: ', rdr.FileInfo.SystemMetadataTagsCount)
print(f'closeFile returned: {rdr.closeFile()}')
