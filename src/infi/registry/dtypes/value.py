
import logging
from ctypes import addressof, sizeof, c_wchar, create_unicode_buffer
from .. import constants
from ..dtypes import BYTE

INTERVAL = sizeof(c_wchar)

class RegistryValue(object):
    """ A registry value can store data in various formats.
    This class and its sub-class helps translate registry values and their Python objects.
    
    The following table describes the convertion between Registry value types and Python:
    | Registry Value Type    | Python Representation | Notes |
    -------------------------------------------------|-------|
    | REG_BINARY             | (int, )               | 32bit |
    | REG_DWORD              | int                   |       |
    | REG_EXPAND_SZ          | unicode               |       |
    | REG_LINK               | unicode               |       |
    | REG_MULTI_SZ           | [unicode, ]           |       |
    | REG_QWORD              | (int, )               | 64bit | 
    | REG_SZ                 | unicode               |       | 
    """

    def __init__(self, value):
        from ctypes import Array
        self._value = self.from_byte_array(value) if isinstance(value, Array) else value

    def to_python_object(self):
        return self._value

    @property
    def registry_type(self):
        raise NotImplementedError # pragma: no cover

    def to_byte_array(self):
        raise NotImplementedError # pragma: no cover

    def from_byte_array(self, byte_array):
        raise NotImplementedError # pragma: no cover

class RegSz(RegistryValue):
    @property
    def registry_type(self):
        return constants.REG_SZ

    def to_byte_array(self):
        c_unicode_string = create_unicode_buffer(self._value)
        factory = BYTE * sizeof(c_unicode_string)
        byte_array = factory.from_buffer_copy(factory.from_address(addressof(c_unicode_string)))
        return byte_array

    def from_byte_array(self, byte_array):
        value = u''
        for index in range(0, sizeof(byte_array) - INTERVAL, INTERVAL):
            value += c_wchar.from_address(addressof(byte_array) + index).value
        return value

class RegExpandSz(RegSz):
    @property
    def registry_type(self):
        return constants.REG_EXPAND_SZ

class RegLink(RegSz):
    @property
    def registry_type(self):
        return constants.REG_LINK

class RegMultiSz(RegistryValue):
    @property
    def registry_type(self):
        return constants.REG_MULTI_SZ

    def to_byte_array(self):
        strings = filter(lambda x: len(x), self._value)
        value = (u'\x00'.join(strings) + u'\x00') if len(strings) else ''
        c_unicode_string = create_unicode_buffer(value)
        factory = BYTE * sizeof(c_unicode_string)
        byte_array = factory.from_address(addressof(c_unicode_string))
        return factory.from_buffer_copy(byte_array)

    def from_byte_array(self, byte_array):
        value = u''
        for index in range(0, sizeof(byte_array) - INTERVAL, INTERVAL):
            wide_character = c_wchar.from_address(addressof(byte_array) + index).value
            value += wide_character
        result = value.replace('\x00', u'\n').splitlines()
        while u'' in result:
            result.remove(u'')
        return result

class RegDword(RegistryValue):
    _size_in_bytes = 4

    @property
    def registry_type(self):
        return constants.REG_DWORD

    def to_byte_array(self):
        from ctypes import c_ubyte
        ubyte_array = (c_ubyte * self._size_in_bytes)()
        for index in range (0, self._size_in_bytes):
            byte = (self._value >> index * 8) & 0xff
            ubyte_array[index] = byte
        factory = BYTE * self._size_in_bytes
        return factory.from_buffer_copy(ubyte_array)

    def from_byte_array(self, byte_array):
        from ctypes import c_ubyte
        factory = c_ubyte * self._size_in_bytes
        ubyte_array = factory.from_buffer_copy(byte_array)
        offset, number = (0, 0,)
        for byte in ubyte_array:
            number += byte << (offset * 8)
            offset += 1
        return number

class RegQword(RegDword):
    _size_in_bytes = 8

    @property
    def registry_type(self):
        return constants.REG_QWORD

class RegBinary(RegistryValue):
    @property
    def registry_type(self):
        return constants.REG_BINARY

    def to_byte_array(self):
        from ctypes import c_ubyte
        array_length = len(self._value)
        ubyte_array = (c_ubyte * array_length)()
        for index in range(0, array_length):
            ubyte_array[index] = self._value[index]
        factory = BYTE * sizeof(ubyte_array)
        return factory.from_buffer_copy(ubyte_array)

    def from_byte_array(self, byte_array):
        from ctypes import c_ubyte
        factory = c_ubyte * sizeof(byte_array)
        return tuple([byte for byte in factory.from_buffer_copy(byte_array)])

class RegNone(RegBinary):
    @property
    def registry_type(self):
        return constants.REG_NONE

class RegFullResourceDescriptor(RegBinary):
    @property
    def registry_type(self):
        return constants.REG_FULL_RESOURCE_DESCRIPTOR

class RegResourcelist(RegBinary):
    @property
    def registry_type(self):
        return constants.REG_RESOURCE_LIST

class RegResourceRequirementsList(RegBinary):
    @property
    def registry_type(self):
        return constants.REG_RESOURCE_REQUIREMENTS_LIST


class RegistryValueFactory(object):
    _FACTORY_DICT = {
        constants.REG_SZ: RegSz,
        constants.REG_EXPAND_SZ: RegExpandSz,
        constants.REG_MULTI_SZ: RegMultiSz,
        constants.REG_DWORD: RegDword,
        constants.REG_QWORD: RegQword,
        constants.REG_LINK: RegLink,
        constants.REG_BINARY: RegBinary,
        constants.REG_NONE: RegNone,
        constants.REG_FULL_RESOURCE_DESCRIPTOR: RegFullResourceDescriptor,
        constants.REG_RESOURCE_LIST: RegResourcelist,
        constants.REG_RESOURCE_REQUIREMENTS_LIST: RegResourceRequirementsList, }

    def by_type(self, value_type, value=None):
        from ctypes import Array
        factory = self._FACTORY_DICT[value_type]
        if value is None or isinstance(value, Array):
            return factory
        return factory(value)

    def by_value(self, value, return_instance_instead_of_class=True):
        cls = None
        if isinstance(value, (str, unicode,)):
            if value.count('%') >= 2:
                return self.by_type(constants.REG_EXPAND_SZ)(value)
            # TODO identify symbolic link
            cls = self.by_type(constants.REG_SZ)
        elif isinstance(value, (tuple,)):
            for item in value:
                if not isinstance(item, int):
                    raise TypeError
            cls = self.by_type(constants.REG_BINARY)
        elif isinstance(value, (list,)):
            for item in value:
                if not isinstance(item, (str, unicode)):
                    raise TypeError
            # TODO add test that checks the loop here
            cls = self.by_type(constants.REG_MULTI_SZ)
        elif isinstance(value, (int, long,)):
            if value < 2 ** 32:
                cls = self.by_type(constants.REG_DWORD)
            else:
                cls = self.by_type(constants.REG_QWORD)
        if cls is None:
            raise TypeError
        logging.debug(cls)
        return cls(value) if return_instance_instead_of_class else cls
