
import logging
from .. import funcs, errors, constants, dtypes, interface

ITER_KEYS = 0
ITER_VALUES = 1
ITER_ITEMS = 2

# TODO more to funcs

class Null(object):
    pass

class DictLikeInterface(object):
    def __iter__(self):
        return self.iteritems() #pragma: no cover

    def __contains__(self, key):
        return self.has_key(key)

    def __getitem__(self, item):
        raise NotImplementedError #pragma: no cover

    def __setitem__(self, item, value):
        raise NotImplementedError #pragma: no cover

    def __delitem__(self, item):
        raise NotImplementedError #pragma: no cover

    def keys(self):
        return [key for key in self.iterkeys()]

    def values(self):
        return [value for value in self.itervalues()]

    def items(self):
        return [item for item in self.iteritems()]

    def setdefault(self, key, default_value=None):
        raise NotImplementedError #pragma: no cover

    def copy(self):
        raise NotImplementedError #pragma: no cover

    def get(self, key, default_value=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            pass
        return default_value

    def has_key(self, key):
        try:
            value = self.__getitem__(key)
            return True
        except KeyError:
            pass
        return False

    def pop(self, key, default=Null):
        if self.has_key(key):
            default = self.__getitem__(key)
            self.__delitem__(key)
            return default
        if default is Null:
            raise KeyError
        return default

    def clear(self):
        for key in self.keys():
            self.__delitem__(key)

    def popitem(self):
        raise NotImplementedError #pragma: no cover

    def update(self, other):
        raise NotImplementedError #pragma: no cover

    def viewitems(self):
        raise NotImplementedError #pragma: no cover

    def viewkeys(self):
        raise NotImplementedError #pragma: no cover

    def viewvalues(self):
        raise NotImplementedError #pragma: no cover

class ValueStore(DictLikeInterface):
    def __init__(self, key_store):
        self._key_store = key_store

    def __len__(self):
        return self._query_info_about_key(3)

    def __getitem__(self, item):
        return self._key_store._getitem_registry_value(item)

    def __setitem__(self, item, value):
        if isinstance(value, (dtypes.value.RegistryValue,)):
            self._key_store._write_registry_value(item, value)
        else:
            return self.__setitem__(item, dtypes.value.RegistryValueFactory().by_value(value))

    def __delitem__(self, item):
        self._key_store._delete_registry_value(item)

    def iteritems(self):
        for index in range(0, self._key_store._query_info_about_key(3)):
            name, value = interface.RegEnumValue(self._key_store._handle, index)
            yield name, value

    def iterkeys(self):
        for index in range(0, self._key_store._query_info_about_key(3)):
            name, value = interface.RegEnumValue(self._key_store._handle, index)
            yield name

    def itervalues(self):
        for index in range(0, self._key_store._query_info_about_key(3)):
            name, value = interface.RegEnumValue(self._key_store._handle, index)
            yield value

class KeyStore(DictLikeInterface):
    def __init__(self, parent=None, path=None, sam=None):
        self._parent = parent
        self._relapath = path
        self._abspath = '\\'.join([parent._abspath if parent is not None else '',
                                   path if path is not None else '']).strip('\\')
        self._sam = sam if sam else self._parent._sam
        self._handle = self._get_handle()

    @property
    def values_store(self):
        return ValueStore(self)

    def _get_handle(self):
        return interface.RegOpenKeyEx(self._parent._handle, self._relapath, self._sam)

    def change_permissions(self, sam):
        old_sam = self._sam
        self._sam = sam
        try:
            new_handle = self._get_handle()
        except:
            self._sam = old_sam
            raise
        interface.RegCloseKey(self._handle)
        self._handle = new_handle

    def _query_info_about_key(self, return_index_from_result):
        result = interface.RegQueryInfoKey(self._handle)
        return result[return_index_from_result]

    def __len__(self):
        return self._query_info_about_key(0)

    def _getitem_registry_value(self, item):
        return interface.RegQueryValueEx(self._handle, item)

    def _getitem_registry_key(self, item):
        return KeyStore(self, path=funcs.item_to_unicode(item), sam=self._sam)

    def __getitem__(self, item):
        return self._getitem_registry_key(item)

    def _create_registry_subkey(self, key):
        subkey_handle = interface.RegCreateKeyEx(self._handle, key, self._sam)

    def _write_registry_value(self, key, value):
        interface.RegSetValueEx(self._handle, key, value.to_python_object())

    def __setitem__(self, item, value=None):
        self._create_registry_subkey(item)

    def _delete_registry_key(self, item):
        interface.RegDeleteKey(self._handle, funcs.item_to_unicode(item))

    def _delete_registry_value(self, item):
        interface.RegDeleteValue(self._handle, funcs.item_to_unicode(item))

    def __delitem__(self, item):
        self._delete_registry_key(item)

    def __del__(self):
        if not hasattr(self, '_handle'):
            return
        interface.RegCloseKey(self._handle)

    def iteritems(self):
        for index in range(0, self._query_info_about_key(0)):
            name = interface.RegEnumKeyEx(self._handle, index)
            value = KeyStore(self, name, self._sam)
            yield name, value

    def iterkeys(self):
        for index in range(0, self._query_info_about_key(0)):
            name = interface.RegEnumKeyEx(self._handle, index)
            yield name

    def itervalues(self):
        for index in range(0, self._query_info_about_key(0)):
            name = interface.RegEnumKeyEx(self._handle, index)
            value = KeyStore(self, name, self._sam)
            yield value

class RegistryHive(KeyStore):
    def __init__(self, computer_name, key, sam):
        self._computer_name = computer_name
        self._key = key
        self._sam = sam
        self._relapath = u''
        self._abspath = u''
        self._handle = self._get_handle()

    def _get_handle(self):
        key_without_sam = interface.RegConnectRegistry(self._computer_name, self._key)
        return interface.RegOpenKeyEx(key_without_sam, None, self._sam)

class RegistryComputer(object):
    """ This is the base class holds the registry hives that are common to remote and local computers:
    HKEY_LOCAL_MACHINE, which is access by 'local_machine' property,
    and HKEY_USERS is similarly accessed by the 'users' property'
    """
    def __init__(self, computer_name, sam):
        """ Constructor method for accessing the registry.
        If you wish to connect to a remote computer, pass its name.
        The computer_name argument accepts r'\\computername' as valid parameters.
        Hand in the required permission scheme into the sam argument
        """
        self._computer_name = computer_name
        self._sam = sam

    def _get_registry_hive(self, key):
        return RegistryHive(self._computer_name, key, self._sam)

    @property
    def local_machine(self):
        """ interface to HKEY_LOCAL_MACHINE
        """
        return self._get_registry_hive(constants.HKEY_LOCAL_MACHINE)

    @property
    def users(self):
        """ interface to HKEY_USERS
        """
        return self._get_registry_hive(constants.HKEY_USERS)

class LocalComputer(RegistryComputer):
    """ Local computers have some additional hives that are not accessible remotely:
    HKEY_CURRENT_USER, which is represented by 'current_user', and similarly others.
    """

    def __init__(self, sam=constants.KEY_ALL_ACCESS):
        """ Constrcuctor method for the Registry of the local machine
        By default, the registry is being access with "full control" permissions.
        If you wish to work with a different set of permissions,
        pass them through the sam paramater.
        You can find the available permissions under the constants module.
        """
        RegistryComputer.__init__(self, None, sam)

    @property
    def current_user(self):
        """ interface to HKEY_CURRENT_USER
        """
        return self._get_registry_hive(constants.HKEY_CURRENT_USER)

    @property
    def classes_root(self):
        """ interface to HKEY_CLASSES_ROOT
        """
        return self._get_registry_hive(constants.HKEY_CLASSES_ROOT)

    @property
    def current_config(self):
        """ interface to HKEY_CURRENT_CONFIG
        """
        return self._get_registry_hive(constants.HKEY_CURRENT_CONFIG)

__all__ = ('KeyStore', 'ValueStore', 'RegistryHive', 'RegistryComputer', 'LocalMachine',)
