import ctypes
import os

# https://sudonull.com/post/145181-Python-threading-or-GIL-is-almost-no-hindrance

PROCESS_SET_INFORMATION   =  512
PROCESS_QUERY_INFORMATION = 1024

__setaffinity = ctypes.windll.kernel32.SetProcessAffinityMask
__setaffinity.argtypes = [ctypes.c_uint, ctypes.c_uint]
__close_handle = ctypes.windll.kernel32.CloseHandle

def __open_process(pid, ro=True):
    if not pid:
        pid = os.getpid()
    access = PROCESS_QUERY_INFORMATION
    if not ro:
        access |= PROCESS_SET_INFORMATION
    hProc = ctypes.windll.kernel32.OpenProcess(access, 0, pid)
    if not hProc:
        raise OSError
    return hProc

def set_cpu_affinity(pid=0, mask=1):
    hProc = __open_process(pid, ro=False)
    mask_proc = ctypes.c_uint(mask)
    res = __setaffinity(hProc, mask_proc)
    __close_handle(hProc)
    if not res:
        raise OSError
    return