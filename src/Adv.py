# The naming conventions follow those used in github.com/AstroDigitalVideo/ADVlib
# The Python code is closely modelled after the C# code written by Hristo Pavlov
# with the intent of matching names, semantics, and code flow as closely as
# possible. While not exactly 'Pythonic', it was my judgement (Bob Anderson) that
# fewer errors would be introduced and it would reduce the intellectual 'load' of comparing
# the well-tested C# code against its (supposedly) equivalent Python version.

# This module holds all of the enums and structures that are defined
# in the C# file PInvoke.cs in the namespace Adv (equivalent to a Python module/file)

# We use type hinting so that it is easy to see the intent as matching the C# code

from dataclasses import dataclass
from enum import Enum


class Adv2TagType(Enum):
    Int8 = 0
    Int16 = 1
    Int32 = 2
    Int64 = 3
    Real = 4
    UTF8String = 5


@dataclass
class AdvIndexEntry:
    ElapsedTicks: int = 0
    FrameOffset: int = 0
    BytesCount: int = 0


@dataclass
class AdvFileInfo:
    Width: int = 0
    Height: int = 0
    CountMaintFrames: int = 0
    CountCalibrationFrames: int = 0
    DataBpp: int = 0
    MaxPixelValue: int = 0
    MainClockFrequency: int = 0
    MainStreamAccuracy: int = 0
    CalibrationClockFrequency: int = 0
    CalibrationStreamAccuracy: int = 0
    MainStreamTagsCount: int = 0
    CalibrationStreamTagsCount: int = 0
    SystemMetadataTagsCount: int = 0
    UserMetadataTagsCount: int = 0
    UtcTimestampAccuracyInNanoseconds: int = 0
    IsColourImage: bool = False
    ImageLayoutsCount: int = 0
    StatusTagsCount: int = 0
    ImageSectionTagsCount: int = 0
    ErrorStatusTagId: int = 0

