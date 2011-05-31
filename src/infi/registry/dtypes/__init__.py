__import__("pkg_resources").declare_namespace(__name__)

from ctypes import Structure, create_unicode_buffer
from ctypes import POINTER
from ctypes import c_byte as BYTE
from ctypes import c_void_p as LPVOID
from ctypes import c_void_p as HKEY
from ctypes import c_wchar_p as LPCWSTR
from ctypes import c_wchar_p as LPWSTR
from ctypes import c_long as BOOL
from ctypes import c_long as LONG
from ctypes import c_ulong as DWORD

class SECURITY_ATTRIBUTES(Structure):
    _fields = [("nLength", DWORD),
               ("lpSecurityDescriptior", LPVOID),
               ('bInheritHandle', BOOL)]

class FILETIME(Structure):
    _fields = [("dwLowDateTime", DWORD),
               ("dwHighDateTime", DWORD)]


from .value import RegBinary, RegDword, RegExpandSz, RegistryValue, \
                   RegistryValueFactory, RegLink, RegMultiSz, RegQword, RegSz
