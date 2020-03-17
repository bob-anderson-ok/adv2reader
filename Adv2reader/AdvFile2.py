# The naming conventions follow those used in github.com/AstroDigitalVideo/ADVlib
# While not exactly 'Pythonic' (i.e., not snake case), it was my judgement (Bob Anderson) that
# fewer errors would be introduced and would reduce the intellectual 'load' of comparing
# the Python code against the equivalent code in github.com/AstroDigitalVideo/ADVlib

# We use type hinting so that it is easy to see the intent as matching the C++ code

import os
import pathlib
from ctypes import c_int, c_uint
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import numpy as np
from AdvError import ResolveErrorMessage, S_OK
import AdvLib
from Adv import AdvFileInfo, AdvFrameInfo, AdvIndexEntry, StreamId, TagPairType, Adv2TagType
from AdvError import AdvLibException
import cv2   # Used by exerciser() only


class Adv2reader:
    def __init__(self, filename: str):
        if not os.path.isfile(filename):
            raise AdvLibException(f'Error: cannot find file ... {filename}')

        fileInfo = AdvFileInfo()
        fileVersionErrorCode = AdvLib.AdvOpenFile(filename, fileInfo)

        if fileVersionErrorCode > 0x70000000:
            raise AdvLibException(f'There was an error opening {filename}: '
                                  f'{ResolveErrorMessage(fileVersionErrorCode)}')

        if not fileVersionErrorCode == 2:
            raise AdvLibException(f'{filename} is not an ADV version 2 file')

        if fileInfo.IsColourImage:
            raise AdvLibException(f'This file contains color images: not yet supported.')

        # Provide a few useful top-level instance variables
        self.Width = fileInfo.Width
        self.Height = fileInfo.Height
        self.CountMainFrames = fileInfo.CountMainFrames
        self.CountCalibrationFrames = fileInfo.CountCalibrationFrames

        # This instance variable gives the user access all file information, including the above items
        self.FileInfo = fileInfo

        self.pixels = None
        self.sysErrLength: int = 0
        self.frameInfo = AdvFrameInfo()
        self.statusTagInfo = []

        for tagId in range(fileInfo.StatusTagsCount):
            tagType, tagName = AdvLib.AdvVer2_GetStatusTagInfo(tagId)
            if tagName:
                self.statusTagInfo.append((tagType, tagName))

    def getMainImageAndStatusData(self, frameNumber: int) -> Tuple[str, np.ndarray, AdvFrameInfo, Dict[str, any]]:
        return self._getGenericImageAndStatusData(frameNumber=frameNumber, streamType=StreamId.Main)

    def getCalibImageAndStatusData(self, frameNumber: int) -> Tuple[str, np.ndarray, AdvFrameInfo, Dict[str, any]]:
        return self._getGenericImageAndStatusData(frameNumber=frameNumber, streamType=StreamId.Calibration)

    def _getGenericImageAndStatusData(self, frameNumber: int, streamType: StreamId) -> \
            Tuple[str, np.ndarray, AdvFrameInfo, Dict[str, any]]:
        err_msg = ''
        # Create an array of c_uint to hold the pixel values
        pixel_array = (c_uint * (self.Width * self.Height))()

        ret_val = AdvLib.AdvVer2_GetFramePixels(
            streamId=streamType, frameNo=frameNumber,
            pixels=pixel_array, frameInfo=self.frameInfo, systemErrorLen=self.sysErrLength
        )

        # Convert pixel_array to 1D numpy array, then reshape into 2D numpy array
        self.pixels = np.reshape(np.array(pixel_array, dtype='uint16'), newshape=(self.Height, self.Width))

        if ret_val is not S_OK:
            err_msg = ResolveErrorMessage(ret_val)
            return err_msg, self.pixels, self.frameInfo, {}

        # This code block adds date and start-of-exposure timestamp strings to self.frameInfo

        datetime64 = self.frameInfo.UtcMidExposureTimestampLo + (self.frameInfo.UtcMidExposureTimestampHi << 32)
        # Adjust from mid exposure to start-exposure
        datetime64 -= self.frameInfo.Exposure // 2

        usecs = datetime64 // 1000  # Convert nanoseconds to microseconds - needed for call to timedelta
        ts = datetime(2010, 1, 1) + timedelta(microseconds=usecs)

        self.frameInfo.DateString = f'{ts.year:04d}-{ts.month:02d}-{ts.day:02d}'
        # This string below is in the form needed for direct insertion into a csv file column (Excel safe format)
        self.frameInfo.StartOfExposureTimestampString = \
            f'[{ts.hour:02d}:{ts.minute:02d}:{ts.second:02d}.{ts.microsecond:06d}]'

        # end code block

        status_dict = {}
        for i in range(len(self.statusTagInfo)):
            tagType, tagName = self.statusTagInfo[i]
            if tagType == Adv2TagType.Int8:
                val = AdvLib.AdvVer2_GetStatusTagUInt8(i)
                status_dict.update({tagName: val})
            if tagType == Adv2TagType.Int16:
                val = AdvLib.AdvVer2_GetStatusTagInt16(i)
                status_dict.update({tagName: val})
            if tagType == Adv2TagType.Int32:
                val = AdvLib.AdvVer2_GetStatusTagInt32(i)
                status_dict.update({tagName: val})
            if tagType == Adv2TagType.Int64:
                val = AdvLib.AdvVer2_GetStatusTagInt64(i)
                if tagName == 'SystemTime':
                    usecs = val // 1000  # Convert nanoseconds to microseconds - for timedelta
                    ts = datetime(2010, 1, 1) + timedelta(microseconds=usecs)
                    val_str = (f'{ts.year:04d}-{ts.month:02d}-{ts.day:02d} '
                               f'[{ts.hour:02d}:{ts.minute:02d}:{ts.second:02d}.{ts.microsecond:06d}]')
                    status_dict.update({tagName: val_str})
                else:
                    status_dict.update({tagName: val})
            if tagType == Adv2TagType.Real:
                val = AdvLib.AdvVer2_GetStatusTagReal(i)
                status_dict.update({tagName: val})
            if tagType == Adv2TagType.UTF8String:
                val = AdvLib.AdvVer2_GetStatusTagUTF8String(i)
                status_dict.update({tagName: val})

        return err_msg, self.pixels, self.frameInfo, status_dict

    def getAdvFileMetaData(self) -> Dict[str, str]:
        meta_dict = {}
        if self.FileInfo.SystemMetadataTagsCount > 0:
            for entryNum in range(self.FileInfo.SystemMetadataTagsCount):
                err_msg, name, value = AdvLib.AdvVer2_GetTagPairValues(TagPairType.SystemMetaData, entryNum)
                if not err_msg:
                    meta_dict.update({name: value})
        if self.FileInfo.UserMetadataTagsCount > 0:
            for entryNum in range(self.FileInfo.UserMetadataTagsCount):
                err_msg, name, value = AdvLib.AdvVer2_GetTagPairValues(TagPairType.UserMetaData, entryNum)
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

        if ret_val is S_OK:
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
            raise AdvLibException(f'{ResolveErrorMessage(ret_val)}')

    @staticmethod
    def closeFile():
        return AdvLib.AdvCloseFile()


def exerciser():
    print(f'\nGeneral information:')
    print(f'    library: {AdvLib.GetLibraryVersion()}')
    print(f'    platform: {AdvLib.GetLibraryPlatformId()}')
    print(f'    bitness: {AdvLib.GetLibraryBitness()}\n')

    rdr = None
    try:
        file_path = str(pathlib.Path('../ver2-test-file.adv'))  # Platform agnostic way to specify a file path
        # file_path = str(pathlib.Path('../UnitTestSample.adv'))  # Platform agnostic way to specify a file path
        rdr = Adv2reader(file_path)
    except AdvLibException as adverr:
        print(repr(adverr))
        exit()

    # Show some top level instance variables
    print(f'A few top-level instance variables of general interest:')
    print(f'    Width: {rdr.Width}  Height: {rdr.Height}  NumMainFrames: {rdr.CountMainFrames}'
          f'  NumCalibFrames: {rdr.CountCalibrationFrames}')
    print(f'    Color image: {rdr.FileInfo.IsColourImage}')
    mainIndexList, calibIndexList = rdr.getIndexEntries()
    print(f'    mainIndexList has {len(mainIndexList)} entries')
    print(f'    calibIndexList has {len(calibIndexList)} entries\n')

    # Show the status tag name and types associated with each DATA_FRAME This is the layout of the STATUS_SECTION
    print(f'STATUS_SECTION layout:')
    for entry in rdr.statusTagInfo:
        tagType, tagName = entry
        print(f'    {tagName}: {tagType}')

    print(f'\nADV_FILE_META_DATA:')
    meta_data = rdr.getAdvFileMetaData()
    for key in meta_data:
        print(f'    {key}: {meta_data[key]}')

    # Show a few main index entries
    # for i in range(len(mainIndexList)):
    # for i in range(3):
    #     print(f'\nindex: {i:2d} ElapsedTicks: {mainIndexList[i].ElapsedTicks}')
    #     print(f'index: {i:2d}  FrameOffset: {mainIndexList[i].FrameOffset}')
    #     print(f'index: {i:2d}   BytesCount: {mainIndexList[i].BytesCount}')

    image = None
    # for frame in range(rdr.CountMainFrames):
    for frame in range(4):
        err, image, frameInfo, status = rdr.getMainImageAndStatusData(frameNumber=frame)

        if not err:
            print(f'\nframe: {frame} STATUS:')
            # print(frameInfo.DateString, frameInfo.StartOfExposureTimestampString)
            # print(f'RawDataSize: {frameInfo.RawDataBlockSize}')
            for k in status:
                print(f'    {k}: {status[k]}')
            cv2.imshow('Test image', image)
            cv2.waitKey(0)  # You must press a key while the image is topmost to advance
        else:
            print(err)

    # print(f'\nimage.shape: {image.shape}  image.dtype: {image.dtype}\n')
    print(f'\ncloseFile returned: {rdr.closeFile()}')
    # print(f'\nun-needed closeFile returned: {rdr.closeFile()}\n')


if __name__ == "__main__":
    exerciser()
