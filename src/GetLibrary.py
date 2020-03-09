# The naming conventions follow those used in github.com/AstroDigitalVideo/ADVlib
# The Python code is closely modelled after the C# code written by Hristo Pavlov
# with the intent of matching names, semantics, and code flow as closely as
# possible. While not exactly 'Pythonic', it was my judgement (Bob Anderson) that
# fewer errors would be introduced and it would reduce the intellectual 'load' of comparing
# the well-tested C# code against its (supposedly) equivalent Python version.

from ctypes import *

adv2lib = CDLL(r'..\AdvLib\AdvLib.Core64.dll')


def GetLibraryVersion() -> str:
    adv2lib.GetLibraryVersion()
    return 'to be defined'
