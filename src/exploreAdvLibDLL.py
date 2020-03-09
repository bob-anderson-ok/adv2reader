from ctypes import *   # CDLL

AdvLib = CDLL(r'..\AdvLib\AdvLib.dll')
print(AdvLib)

from subprocess import Popen, PIPE

out = Popen(
    args=r"nm ..\AdvLib\AdvLib.dll",
    shell=True,
    stdout=PIPE
).communicate()[0].decode("utf-8")

attrs = [
    i.split(" ")[-1].replace("\r", "")
    for i in out.split("\n") if " T " in i
]

functions = [i for i in attrs if hasattr(AdvLib, i)]
for entry in AdvLib:
    print(entry)
