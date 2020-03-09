from dataclasses import dataclass, field
from typing import List, Dict, Any
from ctypes import *
# import numpy as np

# Just something to change file


@dataclass
class Bob:
    Classmates: List[str] = field(default_factory=list)
    Teachers: Dict[str, int] = field(default_factory=dict)
    Age: int = None
    Guess: Any = None


# bob = Bob()
# print(bob)
#
# print(bob.Teachers)
# bob.Teachers['Goofy'] = 89
# print(bob.Teachers['Goofy'])
# bob.Guess = [1, 2, 3]
# print(bob)

bob = bytes([0 for i in range(20)])
print(c_char_p(bob))
print(len(bob))
print(bob)
print(sizeof(c_int64))
