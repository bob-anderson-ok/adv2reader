# The naming conventions follow those used in github.com/AstroDigitalVideo/ADVlib
# The Python code is closely modelled after the C# code written by Hristo Pavlov
# with the intent of matching names, semantics, and code flow as closely as
# possible. While not exactly 'Pythonic', it was my judgement (Bob Anderson) that
# fewer errors would be introduced and it would reduce the intellectual 'load' of comparing
# the well-tested C# code against its (supposedly) equivalent Python version.

# We use type hinting so that it is easy to see the intent as matching the C# code

# from ctypes import *
from dataclasses import field
from typing import Dict, List, Tuple
from .Adv import *
import AdvLib
import src.AdvError as AdvError
import os


@dataclass
class DataStreamDefinition:
    FrameCount: int = 0
    ClockFrequency: int = 0  # Python ints can hold an int64
    TimingAccuracy: int = 0
    MetaDataTags: Dict[str, str] = field(default_factory=dict)


@dataclass
class ImageLayoutDefinition:
    LayoutId: int = 0
    Bpp: int = 0
    ImageLayoutTags: Dict[str, str] = field(default_factory=dict)


class AdvFile2:
    def __init__(self, filename: str):
        if not os.path.isfile(filename):
            raise IOError(f'Error: cannot find file ... {filename}')

        fileInfo = AdvFileInfo()
        fileVersionErrorCode = AdvLib.OpenFile(filename, fileInfo)

        if fileVersionErrorCode > 0x70000000:
            raise IOError(f'There was an error opening {filename}: '
                          f'{AdvError.ResolveErrorMessage(fileVersionErrorCode)}')
        if not fileVersionErrorCode == 2:
            raise IOError(f'{filename} is not an ADV version 2 file')

        # Spelling change --- in C# MainSteamInfo was used
        self.MainStreamInfo = DataStreamDefinition()
        self.MainStreamInfo.FrameCount = fileInfo.CountMainFrames
        self.MainStreamInfo.ClockFrequency = fileInfo.MainClockFrequency
        self.MainStreamInfo.TimingAccuracy = fileInfo.CalibrationStreamAccuracy

        self.CalibrationStreamInfo = DataStreamDefinition()
        self.CalibrationStreamInfo.FrameCount = fileInfo.CountCalibrationFrames
        self.CalibrationStreamInfo.ClockFrequency = fileInfo.CalibrationClockFrequency
        self.CalibrationStreamInfo.TimingAccuracy = fileInfo.CalibrationStreamAccuracy

        self.Width = fileInfo.Width
        self.Height = fileInfo.Height

        self.DataBpp = fileInfo.DataBpp
        self.MaxPixelValue = fileInfo.MaxPixelValue
        self.IsColourImage = fileInfo.IsColourImage
        self.UtcTimestampAccuracyNanoseconds = fileInfo.UtcTimestampAccuracyInNanoseconds

        self.ImageLayouts: List[ImageLayoutDefinition] = []
        self.SystemMetaTags: Dict[str, str] = {}
        self.UserMetaTags: Dict[str, str] = {}
        self.ImageSectionTags: Dict[str, str] = {}
        self.StatusTagDefinitions: List[Tuple[str, int, Adv2TagType]] = []

        # In Python, the leading double-underscore identifies a method meant for private use only
        self.__LoadImageLayout(fileInfo)
        self.__LoadTags(fileInfo)
        self.__EnsureStatusTagsDefinitions(fileInfo)

        self.MainIndex: List[AdvIndexEntry] = []
        self.CalibIndex: List[AdvIndexEntry] = []
        AdvLib.GetIndexEntries(self.MainStreamInfo.FrameCount,
                               self.CalibrationStreamInfo.FrameCount,
                               self.MainIndex,
                               self.CalibIndex)

    def __LoadImageLayout(self, fileInfo: AdvFileInfo) -> None:  # Private method
        self.Height = fileInfo.Height  # Just to convince PyCharm that this cannot be a static method
        print('LoadImageLayout called')
        return

    def __LoadTags(self, fileInfo: AdvFileInfo) -> None:  # Private method
        self.Height = fileInfo.Height  # Just to convince PyCharm that this cannot be a static method
        print('LoadTags called')
        return

    def __EnsureStatusTagsDefinitions(self, fileInfo: AdvFileInfo) -> None:  # Private method
        self.Height = fileInfo.Height  # Just to convince PyCharm that this cannot be a static method
        print('EnsureStatusTagsDefinitions called')
        return


# bob = DataStreamDefinition()
# print(bob)
bob = AdvFile2(r'..\ver2-test-file.adv')
print('bob.Height: ', bob.Height)
