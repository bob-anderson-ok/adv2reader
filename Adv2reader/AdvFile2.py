# The naming conventions follow those used in github.com/AstroDigitalVideo/ADVlib
# While not exactly 'Pythonic' (i.e., not snake case), it was my judgement (Bob Anderson) that
# fewer errors would be introduced and would reduce the intellectual 'load' of comparing
# the Python code against the equivalent code in github.com/AstroDigitalVideo/ADVlib

# We use type hinting so that it is easy to see the intent as matching the C++ code

import os
import pathlib
from ctypes import c_int, c_uint
from typing import Dict, List, Tuple

import numpy as np

import AdvError
import AdvLib
from Adv import (AdvFileInfo, AdvFrameInfo, AdvIndexEntry,
                 StreamId, TagPairType)
from AdvError import AdvLibException

import matplotlib.pyplot as plt


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
        self.CountCalibrationFrames = fileInfo.CountCalibrationFrames

        self.FileInfo = fileInfo

        self.pixels = None
        self.sysErrLength: int = 0
        self.frameInfo = AdvFrameInfo()

    def getMainImageData(self, frameNumber: int) -> Tuple[str, np.ndarray, AdvFrameInfo]:
        err_msg = ''
        # Create an array of c_uint to hold the pixel values
        pixel_array = (c_uint * (self.Width * self.Height))()

        ret_val = AdvLib.AdvVer2_GetFramePixels(
            streamId=StreamId.Main, frameNo=frameNumber,
            pixels=pixel_array, frameInfo=self.frameInfo, systemErrorLen=self.sysErrLength
        )

        # Convert pixel_array to 1D numpy array, then reshape into 2D numpy array
        self.pixels = np.reshape(np.array(pixel_array, dtype='uint16'), newshape=(self.Height, self.Width))

        if not ret_val == AdvError.S_OK:
            err_msg = AdvError.ResolveErrorMessage(ret_val)
            return err_msg, self.pixels, self.frameInfo

        return err_msg, self.pixels, self.frameInfo

    def getMetaData(self) -> Dict[str, str]:
        meta_dict = {}
        if self.FileInfo.SystemMetadataTagsCount > 0:
            for entryNum in range(self.FileInfo.SystemMetadataTagsCount):
                err_msg, name, value = AdvLib.AdvVer2_GetTagPairValues(TagPairType.SystemMetaData, entryNum)
                if not err_msg:
                    meta_dict.update({name: value})
        return meta_dict

    def getIndexEntries(self) -> Tuple[List[AdvIndexEntry], List[AdvIndexEntry]]:
        # Create C compatible buffers that hold the correct number of AdvIndexEntry instances.
        # Although an AdvIndexEntry is 2 int64 and an int32, we have to allow for 'alignment' on int64
        # boundaries - that's the reason for the 6 c_int rather than 5 c_int in the buffer construction
        mainIndex = (c_int * (6 * self.CountMainFrames))()
        calibIndex = (c_int * (6 * self.CountCalibrationFrames))()

        ret_val = AdvLib.AdvVer2_GetIndexEntries(mainIndex, calibIndex)

        if ret_val == AdvError.S_OK:
            mainList = []
            calibList = []

            base = 0
            for _ in range(self.CountMainFrames):
                ticks = mainIndex[base] + (mainIndex[base + 1] << 32)
                offset = mainIndex[base + 2] + (mainIndex[base + 3] << 32)
                byte_count = mainIndex[base + 4]

                new_index_entry = AdvIndexEntry()
                new_index_entry.ElapsedTicks = ticks
                new_index_entry.FrameOffset = offset
                new_index_entry.BytesCount = byte_count

                mainList.append(new_index_entry)
                base += 6

            base = 0
            for _ in range(self.CountCalibrationFrames):
                ticks = calibIndex[base] + (calibIndex[base + 1] << 32)
                offset = calibIndex[base + 2] + (calibIndex[base + 3] << 32)
                byte_count = calibIndex[base + 4]

                new_index_entry = AdvIndexEntry()
                new_index_entry.ElapsedTicks = ticks
                new_index_entry.FrameOffset = offset
                new_index_entry.BytesCount = byte_count

                calibList.append(new_index_entry)
                base += 6

            return mainList, calibList
        else:
            raise AdvLibException(f'{AdvError.ResolveErrorMessage(ret_val)}')

    @staticmethod
    def closeFile():
        return AdvLib.AdvCloseFile()


def exerciser():
    print(f'\nlibrary: {AdvLib.GetLibraryVersion()}')
    print(f'\nplatform: {AdvLib.GetLibraryPlatformId()}')
    print(f'\nbitness: {AdvLib.GetLibraryBitness()}\n')

    rdr = None
    try:
        # file_path = str(pathlib.Path('../ver2-test-file.adv'))  # Platform agnostic way to specify a file path
        file_path = str(pathlib.Path('../UnitTestSample.adv'))  # Platform agnostic way to specify a file path
        rdr = Adv2reader(file_path)
    except AdvLibException as adverr:
        print(repr(adverr))
        exit()

    # Show some top level instance variables
    print(f'Width: {rdr.Width}  Height: {rdr.Height}  NumMainFrames: {rdr.CountMainFrames}')

    print(f'\nis color image: {rdr.FileInfo.IsColourImage}\n')
    # Show a few main index entries
    mainIndexList, _ = rdr.getIndexEntries()
    for i in range(len(mainIndexList)):
    # for i in range(3):
        print(f'\nindex: {i:2d} ElapsedTicks: {mainIndexList[i].ElapsedTicks}')
        print(f'index: {i:2d}  FrameOffset: {mainIndexList[i].FrameOffset}')
        print(f'index: {i:2d}   BytesCount: {mainIndexList[i].BytesCount}')

    image = None
    for frame in range(rdr.CountMainFrames):
    # for frame in range(4):
        err, image, frameInfo = rdr.getMainImageData(frameNumber=frame)

        if not err:
            print(f'\nframe:       {frame}')
            print(f'UtcMidLo:    {frameInfo.UtcMidExposureTimestampLo}')
            print(f'UtcMidHi:    {frameInfo.UtcMidExposureTimestampHi}')
            print(f'Exposure:    {frameInfo.Exposure}')
            print(f'RawDataSize: {frameInfo.RawDataBlockSize}')
            # print(np.min(image), np.max(image))
            plt.imshow(image)
            plt.show()
        else:
            print(err)

    plt.imshow(image)
    plt.show()
    print(f'\nimage.shape: {image.shape}  image.dtype: {image.dtype}\n')
    meta_data = rdr.getMetaData()
    for key in meta_data.keys():
        print(f'{key}: {meta_data[key]}')
    print(f'\ncloseFile returned: {rdr.closeFile()}')
    print(f'\nun-needed closeFile returned: {rdr.closeFile()}\n')


if __name__ == "__main__":
    exerciser()
