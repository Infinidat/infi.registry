
from .constants import MAX_KEYNAME_LENGTH, MAX_VALUENAME_LENGTH
from .dtypes import create_unicode_buffer
from .dtypes  import BYTE, LPVOID, DWORD, LONG, LPCWSTR, HKEY, LPWSTR, POINTER
from .dtypes import SECURITY_ATTRIBUTES, FILETIME
from .funcs import wrap_advapi32_function

class WrappedFunction(object):
    _return_value = LONG
    _parameters = ()

    @classmethod
    def __new__(cls, *args, **kwargs):
        function = cls._get_function()
        return_value = function(*args[1:], **kwargs)
        return return_value

    @classmethod
    def _get_function(cls):
        name = cls.__name__
        return_value = cls._return_value
        parameters = cls._get_parameters()
        function = wrap_advapi32_function(name, return_value, parameters)
        return function

    @classmethod
    def is_available_on_this_platform(cls):
        try:
            function = cls._get_function()
            return True
        except AttributeError:
            return False
        return True # pragma: no cover

class RegCloseKey(WrappedFunction):
    @classmethod
    def _get_parameters(cls):
        return (HKEY, 1, 'key',),

class RegConnectRegistryW(WrappedFunction):
    @classmethod
    def _get_parameters(cls):
        return (LPCWSTR, 1, 'computerName', None), \
            (HKEY, 1, 'key',), \
            (POINTER(HKEY), 2, 'result',),


class RegCreateKeyExW(WrappedFunction):
    @classmethod
    def _get_parameters(cls):
        return (HKEY, 1, 'key',), (LPCWSTR, 1, 'subKey',), \
            (DWORD, 1, 'reserved',), (LPCWSTR, 1, 'classType',), \
            (DWORD, 1, 'options',), (DWORD, 1, 'samDesired',), \
            (POINTER(SECURITY_ATTRIBUTES), 1, 'securityAttributes',), \
            (POINTER(HKEY), 2, 'result',), \
            (POINTER(DWORD), 2, 'disposition',),

class RegDeleteKeyW(WrappedFunction):
    @classmethod
    def _get_parameters(cls):
        return (HKEY, 1, 'key',), (LPWSTR, 1, 'subKey',),

class RegDeleteValueW(WrappedFunction):
    @classmethod
    def _get_parameters(cls):
        return (HKEY, 1, 'key',), (LPCWSTR, 1, "valueName"),

class RegEnumKeyExW(WrappedFunction):
    @classmethod
    def _get_parameters(cls):
        return (HKEY, 1, 'key',), (DWORD, 1, "index"), \
            (LPWSTR, 2, 'name', create_unicode_buffer(MAX_KEYNAME_LENGTH)), \
            (POINTER(DWORD), 3, 'nameSize', DWORD(MAX_KEYNAME_LENGTH)), \
            (POINTER(DWORD), 0, 'reserved', None), \
            (LPWSTR, 3, 'classType', create_unicode_buffer(MAX_KEYNAME_LENGTH)), \
            (POINTER(DWORD), 3, 'classTypeSize', DWORD(MAX_KEYNAME_LENGTH)), \
            (POINTER(FILETIME), 3, 'lastWriteTime', FILETIME())

class RegEnumValueW(WrappedFunction):
    @classmethod
    def _get_parameters(cls):
        return (HKEY, 1, 'key',), \
            (DWORD, 1, 'index',), \
            (LPWSTR, 2, 'name', create_unicode_buffer(MAX_VALUENAME_LENGTH)), \
            (POINTER(DWORD), 3, 'nameLength', DWORD(MAX_VALUENAME_LENGTH)), \
            (POINTER(DWORD), 0, 'reserved', None), \
            (POINTER(DWORD), 2, 'dataType', DWORD()), \
            (POINTER(BYTE), 3, 'data', (BYTE * 0).from_address(0)), \
            (POINTER(DWORD), 3, 'dataLength', DWORD())

class RegFlushKey(WrappedFunction):
    @classmethod
    def _get_parameters(cls):
        return (HKEY, 1, 'key',),

class RegGetValueW(WrappedFunction):
    @classmethod
    def _get_parameters(cls):
        return (HKEY, 1, 'key',), (LPCWSTR, 1, 'subKey',), \
            (LPCWSTR, 1, 'valueName',), (DWORD, 1, 'flags', 0), \
            (POINTER(DWORD), 2, 'dataType', DWORD()), \
            (POINTER(BYTE), 3, 'data', (BYTE * 0).from_address(0)), \
            (POINTER(DWORD), 3, 'dataLength', DWORD()),

class RegOpenKeyExW(WrappedFunction):
    @classmethod
    def _get_parameters(cls):
        return (HKEY, 1, 'key',), \
            (LPCWSTR, 1, 'subKey',), \
            (DWORD, 1, 'options', 0), (DWORD, 1, 'samDesired', 0), \
            (POINTER(HKEY), 2, 'result')

class RegQueryInfoKeyW(WrappedFunction):
    @classmethod
    def _get_parameters(cls):
        return (HKEY, 1, 'key',), \
                  (LPWSTR, 2, 'classType', create_unicode_buffer(MAX_KEYNAME_LENGTH)), \
                  (POINTER(DWORD), 3, 'classTypeLength', DWORD(MAX_KEYNAME_LENGTH)), \
                  (POINTER(DWORD), 0, 'reserved', None), \
                  (POINTER(DWORD), 2, 'subKeys',), \
                  (POINTER(DWORD), 2, 'maxSubKeyLength',), \
                  (POINTER(DWORD), 2, 'maxClassTypeLength',), \
                  (POINTER(DWORD), 2, 'values',), \
                  (POINTER(DWORD), 2, 'maxValueNameLength'), \
                  (POINTER(DWORD), 2, 'maxValueLength',), \
                  (POINTER(DWORD), 2, 'securityDescriptor'), \
                  (POINTER(DWORD), 2, 'lastWriteTime')

class RegQueryValueExW(WrappedFunction):
    @classmethod
    def _get_parameters(cls):
        return (HKEY, 1, 'key',), \
            (LPCWSTR, 1, 'name',), \
            (POINTER(DWORD), 0, 'reserved', None), \
            (POINTER(DWORD), 2, 'dataType', DWORD()), \
            (POINTER(BYTE), 3, 'data', (BYTE * 0).from_address(0)), \
            (POINTER(DWORD), 3, 'dataLength', DWORD())

class RegSetKeyValueW(WrappedFunction):
    @classmethod
    def _get_parameters(cls):
        return (HKEY, 1, 'key',), \
            (LPCWSTR, 1, 'subKey,',), \
            (LPCWSTR, 1, 'valueName',), \
            (DWORD, 1, 'dataType',), \
            (POINTER(BYTE), 1, 'data',), \
            (DWORD, 1, 'dataLength',)

class RegSetValueExW(WrappedFunction):
    @classmethod
    def _get_parameters(cls):
        return (HKEY, 1, 'key',), \
            (LPCWSTR, 1, 'name',), \
            (POINTER(DWORD), 0, 'reserved', None), \
            (DWORD, 1, 'dataType',), \
            (POINTER(BYTE), 1, 'data',), \
            (DWORD, 1, 'dataLength',)
