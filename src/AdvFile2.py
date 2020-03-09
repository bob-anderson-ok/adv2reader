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
from src.Adv import *
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
    MainStreamInfo = DataStreamDefinition()
    CalibrationStreamInfo = DataStreamDefinition()

    ImageLayouts: List[ImageLayoutDefinition] = []

    SystemMetaTags: Dict[str, str] = {}
    UserMetaTags: Dict[str, str] = {}
    ImageSectionTags: Dict[str, str] = {}

    MainIndex: List[AdvIndexEntry] = []
    CalibrationIndex: List[AdvIndexEntry] = []

    StatusTagDefinitions: List[Tuple[str, int, Adv2TagType]] = []

    Width: int = None
    Height: int = None
    DataBpp: int = None
    MaxPixValue: int = None
    IsColourImage: bool = None
    UtcTimestampAccuracyInNanoseconds: int = None

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


# bob = DataStreamDefinition()
# print(bob)
bob = AdvFile2(r'..\ver2-test-file.adv')
