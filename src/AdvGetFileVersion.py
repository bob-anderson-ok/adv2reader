# The naming conventions follow those used in github.com/AstroDigitalVideo/ADVlib
# The Python code is closely modelled after the C# code written by Hristo Pavlov
# with the intent of matching names, semantics, and code flow as closely as
# possible. While not exactly 'Pythonic', it was my judgement (Bob Anderson) that
# fewer errors would be introduced and it would reduce the intellectual 'load' of comparing
# the well-tested C# code against its (supposedly) equivalent Python version.

from ctypes import *
import os

adv2lib = CDLL(r'..\AdvLib\AdvLib.Core64.dll')


def AdvGetFileVersion(filepath: str) -> (str, int):
    if not os.path.isfile(filepath):
        return f'Error - cannot find file: "{filepath}"', 0
    else:
        file_path_as_bytes = bytes(filepath, 'utf-8')
        fname_ptr = c_char_p(file_path_as_bytes)  # fname_ptr: const char* fileName
        version_num = adv2lib.AdvGetFileVersion(fname_ptr)
        if version_num == 0:
            return f'Error - not an FSTF file: "{filepath}"', 0
        else:
            return '', version_num
