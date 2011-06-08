
# -*- coding: utf-8 -*-

import logging
import unittest2
import mock
import os
from .. import interface, constants, dtypes, errors, funcs, c_api
from ..dtypes import LPWSTR, LPCWSTR


class BaseTestCase(unittest2.TestCase):
    def _get_tested_function(self):
        return getattr(interface, self.__class__.__name__, None)

    def _get_tested_api_function(self):
        return getattr(c_api, self.__class__.__name__, None) or \
                getattr(c_api, '%sW' % self.__class__.__name__) or \
                False

    def setUp(self):
        if os.name != 'nt':
            raise unittest2.SkipTest
        if not self._get_tested_api_function().is_available_on_this_platform():
            raise unittest2.SkipTest

    def tearDown(self):
        pass

    def _assert_func_raises(self, exception, kwargs):
        self.assertRaises(exception, self._get_tested_function(), **kwargs)

    def _test_base_exception(self, kwargs, expected_exception):
        api_function = self._get_tested_api_function()
        @mock.patch("infi.registry.c_api.%s" % api_function.__name__)
        def _test(mocked_api_function):
            mocked_api_function.side_effect = WindowsError(-1)
            self._assert_func_raises(expected_exception, kwargs)
        _test()

class RegCloseKey(BaseTestCase):
    def test_invalid_key_1(self):
        kwargs = {'key': 0}
        self._assert_func_raises(errors.InvalidHandleException, kwargs)

    def test_invalid_key_2(self):
        kwargs = {'key': 4000}
        self._assert_func_raises(errors.InvalidHandleException, kwargs)

    def test_valid_close(self):
        open_key = self._get_open_key()
        self.assertEqual(None, interface.RegCloseKey(open_key))

    def _get_open_key(self):
        raise unittest2.SkipTest
        HKLM = interface.RegConnectRegistry(None, constants.HKEY_LOCAL_MACHINE)
        return interface.RegCreateKeyEx(HKLM, 'SOFTWARE')

    def test_double_close(self):
        open_key = self._get_open_key()
        self.assertEqual(None, interface.RegCloseKey(open_key))
        self.assertEqual(None, interface.RegCloseKey(open_key))

    def test_base_exception(self):
        kwargs = {'key':-1}
        self._test_base_exception(kwargs, errors.CloseKeyFailed)

class RegConnectRegistry(BaseTestCase):
    def test_invalid_local_key(self):
        kwargs = {'machineName': None,
                  'key': 0}
        self._assert_func_raises(ValueError, kwargs)

    def test_invalid_remote_key(self):
        kwargs = {'machineName': 'remoteComputer',
                  'key': constants.HKEY_CURRENT_USER}
        self._assert_func_raises(ValueError, kwargs)

    @mock.patch("infi.registry.c_api.RegConnectRegistryW")
    def test_valid_remote_keys(self, mocked_function):
        mocked_function.return_value = None
        kwargs = {'machineName': 'remoteComputer'}
        for key in [constants.HKEY_LOCAL_MACHINE, constants.HKEY_USERS]:
            kwargs['key'] = key
            self.assertEqual(None, interface.RegConnectRegistry(**kwargs))
        self.assertEqual(2, mocked_function.call_count)

    @mock.patch("infi.registry.c_api.RegConnectRegistryW")
    def test_valid_local_keys(self, mocked_function):
        mocked_function.return_value = None
        kwargs = {'machineName': None}
        for key in [constants.HKEY_LOCAL_MACHINE, constants.HKEY_USERS, constants.HKEY_CURRENT_CONFIG,
                    constants.HKEY_CURRENT_USER, constants.HKEY_CLASSES_ROOT]:
            kwargs['key'] = key
            self.assertEqual(None, interface.RegConnectRegistry(**kwargs))
        self.assertEqual(5, mocked_function.call_count)

    def test_connect_to_local_machine(self):
        key = interface.RegConnectRegistry(None, constants.HKEY_LOCAL_MACHINE)
        self.assertGreater(key, 0)

    def test_connect_to_remote_machine(self):
        import socket
        key = interface.RegConnectRegistry(r'\\%s' % socket.gethostname(), constants.HKEY_LOCAL_MACHINE)
        self.assertGreater(key, 0)

    def test_connect_to_invalid_remote(self):
        kwargs = {'machineName': r'\\0.0.0.0',
                  'key': constants.HKEY_LOCAL_MACHINE}
        self._assert_func_raises(errors.RemoteRegistryConnectionFailed, kwargs)

    def test_base_exception(self):
        kwargs = {'machineName':None, 'key':constants.HKEY_LOCAL_MACHINE}
        self._test_base_exception(kwargs, errors.ConnectRegistryFailed)

class TestCaseLocalMachine(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        self.key = interface.RegConnectRegistry(None, constants.HKEY_LOCAL_MACHINE)

    def tearDown(self):
        interface.RegCloseKey(self.key)
        BaseTestCase.tearDown(self)

class RegFlushKey(BaseTestCase):
    def test_flush_key(self):
        self.key = interface.RegConnectRegistry(None, constants.HKEY_LOCAL_MACHINE)
        self.key = interface.RegCreateKeyEx(self.key, 'SOFTWARE')
        interface.RegFlushKey(self.key)
        interface.RegCloseKey(self.key)

    def test_base_exception(self):
        kwargs = {'key':-1}
        self._test_base_exception(kwargs, errors.FlushKeyError)

class RegCreateKeyEx(TestCaseLocalMachine):
    def test_create_existing_subkey(self):
        self.assertGreater(interface.RegCreateKeyEx(self.key, 'SOFTWARE'), 0)

    def test_access_denied(self):
        # TODO Implement test_access_denied
        raise unittest2.SkipTest

    def test_closed_key(self):
        self.tearDown()
        kwargs = {'key': self.key,
                  'subKey': 'SOFTWARE'}
        self._assert_func_raises(errors.InvalidHandleException, kwargs)
        self.setUp()

    def test_unicode_subkey_1(self):
        self.assertGreater(interface.RegCreateKeyEx(self.key, u'SOFTWARE'), 0)

    def test_deep_subkey(self):
        self.assertGreater(interface.RegCreateKeyEx(self.key, r'SOFTWARE\Microsoft'), 0)

    def test_unicode_subkey_2(self):
        self.assertGreater(interface.RegCreateKeyEx(self.key, u'SOFTWARE\\\xe2\x9f\xb2'), 0)

    def test_base_exception(self):
        kwargs = {'key':-1, 'subKey':'Foo'}
        self._test_base_exception(kwargs, errors.CreateKeyFailed)

class RegDeleteKey(TestCaseLocalMachine):
    def setUp(self):
        TestCaseLocalMachine.setUp(self)
        self.key = interface.RegCreateKeyEx(self.key, 'SOFTWARE')

    def tearDown(self):
        TestCaseLocalMachine.tearDown(self)

    def test_delete_nonexisting_subkey(self):
        kwargs = {'key': self.key,
                  'subKey': 'DoesNotExist'}
        self._assert_func_raises(KeyError, kwargs)

    def test_delete_with_closed_key(self):
        kwargs = {'key': self.key,
                  'subKey': 'DoesNotExist'}
        self.tearDown()
        self._assert_func_raises(errors.InvalidHandleException, kwargs)
        self.setUp()

    def test_delete_existing_subkey(self):
        key = interface.RegCreateKeyEx(self.key, 'TestDeleteExistingSubkey')
        interface.RegCloseKey(key)
        kwargs = {'key': self.key,
                  'subKey': 'TestDeleteExistingSubkey'}
        self.assertEqual(None, interface.RegDeleteKey(**kwargs))

    def test_delete_None_as_subkey(self):
        kwargs = {'key': self.key,
                  'subKey': None}
        self.tearDown()
        self._assert_func_raises(errors.InvalidParameterException, kwargs)
        self.setUp()

    def test_delete_subkey_with_subkeys(self):
        key = interface.RegCreateKeyEx(self.key, 'TestDeleteSubkeyWithSubkeys')
        interface.RegCloseKey(interface.RegCreateKeyEx(key, 'TestDeleteSubkeyWithSubkeys'))
        interface.RegCloseKey(key)
        kwargs = {'key': self.key,
                  'subKey': 'TestDeleteSubkeyWithSubkeys'}
        self._assert_func_raises(errors.AccessDeniedException, kwargs)

    def test_delete_subkey_with_values(self):
        key = interface.RegCreateKeyEx(self.key, u'TestDeleteSubKeyWithValues')
        interface.RegSetValueEx(key, 'someValue', 'fooBar')
        interface.RegCloseKey(key)
        kwargs = {'key': self.key,
                  'subKey': 'TestDeleteSubKeyWithValues'}
        self.assertEqual(None, interface.RegDeleteKey(**kwargs))

    def test_delete_existing_subkey_in_unicode(self):
        key = interface.RegCreateKeyEx(self.key, u'\xe2\x9f\xb2')
        interface.RegCloseKey(key)
        kwargs = {'key': self.key,
                  'subKey': u'\xe2\x9f\xb2'}
        self.assertEqual(None, interface.RegDeleteKey(**kwargs))

    def test_base_exception(self):
        kwargs = {'key':-1, 'subKey': u'fooBar'}
        self._test_base_exception(kwargs, errors.DeleteKeyFailed)

class RegDeleteValue(TestCaseLocalMachine):
    def setUp(self):
        TestCaseLocalMachine.setUp(self)
        self.key = interface.RegCreateKeyEx(self.key, 'SOFTWARE')
        self.key = interface.RegCreateKeyEx(self.key , 'RegDeleteValue')

    def test_invalid_key(self):
        kwargs = {'key': 0, }
        self._assert_func_raises(errors.InvalidHandleException, kwargs)

    def test_invalid_value_name(self):
        kwargs = {'key': self.key,
                  'valueName': 'DoesNotExist'}
        self._assert_func_raises(KeyError, kwargs)

    def test_valid_value_name(self):
        raise unittest2.SkipTest

    def test_access_denied(self):
        raise unittest2.SkipTest

    def test_null_value_name(self):
        kwargs = {'key': self.key,
                  'valueName': None}
        self._assert_func_raises(KeyError, kwargs)

    def test_base_exception(self):
        kwargs = {'key':-1, 'valueName':'m0she'}
        self._test_base_exception(kwargs, errors.DeleteValueFailed)

class RegEnumKeyEx(TestCaseLocalMachine):
    def setUp(self):
        TestCaseLocalMachine.setUp(self)
        self.key = interface.RegCreateKeyEx(self.key, 'SOFTWARE')

    def test_index_0(self):
        result = interface.RegEnumKeyEx(self.key, 0)
        self.assertNotEquals(None, result)
        self.assertGreater(len(result), 0)

    def test_index_valid_range(self):
        for index in range(0, 4):
            result = interface.RegEnumKeyEx(self.key, index)
            self.assertNotEquals(None, result)
            self.assertGreater(len(result), 0)

    def test_index_outbound_index(self):
        kwargs = {'key': self.key,
                  'index': 100}
        self._assert_func_raises(IndexError, kwargs)

    def test_index_bad_index(self):
        kwargs = {'key': self.key,
                  'index':-1}
        self._assert_func_raises(IndexError, kwargs)

    def test_base_exception(self):
        kwargs = {'key':-1, 'index':-1}
        self._test_base_exception(kwargs, errors.RegistryBaseException)

class RegEnumValue(TestCaseLocalMachine):
    def setUp(self):
        TestCaseLocalMachine.setUp(self)
        self.key = interface.RegCreateKeyEx(self.key, r'SOFTWARE\Microsoft\Windows NT\CurrentVersion')

    def test_index_0(self):
        name, data = interface.RegEnumValue(self.key, 0)
        self.assertNotEqual(None, data, "'%s' value None, it shouldn't be" % name)

    def test_index_1(self):
        name, data = interface.RegEnumValue(self.key, 1)
        self.assertNotEqual(None, data)

    def test_index_outbound_index(self):
        kwargs = {'key': self.key,
                  'index': 1024}
        self._assert_func_raises(IndexError, kwargs)

    def test_index_bad_index(self):
        kwargs = {'key': self.key,
                  'index':-1}
        self._assert_func_raises(IndexError, kwargs)

    def _test_for_specific_value(self, expected_name, expected_data, key=None):
        index = 0
        while True:
            name, data = interface.RegEnumValue(key or self.key, index)
            if name == expected_name:
                self.assertTrue(data, expected_data)
                return
            index += 1
        if key:
            interface.RegCloseKey(key)
        self.assertTrue(False)

    def test_system_root(self):
        # TODO add tests that cover more value types
        self._test_for_specific_value("SystemRoot", r'C:\WINDOWS')

    def test_base_exception(self):
        kwargs = {'key':-1, 'index':-1}
        self._test_base_exception(kwargs, errors.RegistryBaseException)

class RegQueryValueEx(TestCaseLocalMachine):
    def setUp(self):
        TestCaseLocalMachine.setUp(self)
        self.key = interface.RegCreateKeyEx(self.key, r'SYSTEM\CurrentControlSet\Services\Netlogon')

    def test_invalid_key(self):
        kwargs = {'key': 0, }
        self._assert_func_raises(errors.InvalidHandleException, kwargs)

    def test_invalid_value(self):
        kwargs = {'key': self.key,
                  'valueName': 'DoesNotExist'}
        self._assert_func_raises(KeyError, kwargs)

    def test_access_denied(self):
        raise unittest2.SkipTest

    def test_null_value_name(self):
        # TODO add more tests on more value
        kwargs = {'key': self.key,
                  'valueName': None}
        self._assert_func_raises(KeyError, kwargs)

    def test_string(self):
        kwargs = {'key': self.key,
                  'valueName': 'ObjectName'}
        self.assertEqual('LocalSystem', interface.RegQueryValueEx(**kwargs).to_python_object())

    def test_dword(self):
        kwargs = {'key': self.key,
                  'valueName': 'start'}
        self.assertEqual(3, interface.RegQueryValueEx(**kwargs).to_python_object())

    def test_exand_sz(self):
        kwargs = {'key': self.key,
                  'valueName': 'ImagePath'}
        self.assertEqual(u'%SystemRoot%\system32\lsass.exe'.lower(),
                         interface.RegQueryValueEx(**kwargs).to_python_object().lower())

    def test_base_exception(self):
        kwargs = {'key':-1, 'valueName':'m0she'}
        self._test_base_exception(kwargs, errors.RegistryBaseException)

class RegOpenKeyEx(TestCaseLocalMachine):
    def setUp(self):
        TestCaseLocalMachine.setUp(self)
        self.key = interface.RegCreateKeyEx(self.key, r'SOFTWARE\Microsoft\Windows NT\CurrentVersion')

    def test_invalid_key(self):
        kwargs = {'key': 0,
                  'subKey': None }
        self._assert_func_raises(errors.InvalidHandleException, kwargs)

    def test_invalid_subkey(self):
        kwargs = {'key': self.key,
                  'subKey': 'DoesNotExist'}
        self._assert_func_raises(KeyError, kwargs)

    def test_none_as_subkey(self):
        kwargs = {'key': self.key,
                  'subKey': None}
        self.assertGreater(interface.RegOpenKeyEx(**kwargs), 0)

    def test_valid_key(self):
        kwargs = {'key': self.key,
                  'subKey': 'Terminal Server'}
        self.assertGreater(interface.RegOpenKeyEx(**kwargs), 0)

    def test_base_exception(self):
        kwargs = {'key':-1, 'subKey':'m0she'}
        self._test_base_exception(kwargs, errors.OpenKeyFailed)

class RegQueryInfoKey(TestCaseLocalMachine):
    def setUp(self):
        TestCaseLocalMachine.setUp(self)
        self.key = interface.RegCreateKeyEx(self.key, r'SOFTWARE\Microsoft\Windows NT\CurrentVersion')

    def test_invalid_key(self):
        kwargs = {'key': 0 }
        self._assert_func_raises(errors.InvalidHandleException, kwargs)

    def test_valid_key(self):
        result = interface.RegQueryInfoKey(self.key)
        self.assertGreater(result[0], 0)

    def test_base_exception(self):
        kwargs = {'key':-1}
        self._test_base_exception(kwargs, errors.QueryInfoKeyFailed)

class RegSetValueEx(TestCaseLocalMachine):
    def setUp(self):
        TestCaseLocalMachine.setUp(self)
        self.key = interface.RegCreateKeyEx(self.key, 'SOFTWARE')
        self.key = interface.RegCreateKeyEx(self.key , 'RegSetValueEx')

    def _test_set_get_value(self, name, data):
        kwargs = {'key': self.key,
                  'valueName': name,
                  'valueData': data}
        self.assertEquals(None, interface.RegSetValueEx(**kwargs))
        self.assertEquals(data, interface.RegQueryValueEx(key=self.key, valueName=name).to_python_object())

    def test_null_value(self):
        kwargs = {'key': self.key,
                  'valueName': '',
                  'valueData': 'hi'}
        self.assertEquals(None, interface.RegSetValueEx(**kwargs))

    def test_dword_small(self):
        self._test_set_get_value('dword', 1)

    def test_dword_max(self):
        self._test_set_get_value('dword_max', 2 ** 32 - 1)

    def test_sz(self):
        self._test_set_get_value('sz', u'hi')

    def test_multi_sz(self):
        self._test_set_get_value('multi_sz', [u'hi', u'bye'])

    def test_binary(self):
        self._test_set_get_value('binary', (5, 5, 5, 5, 5, 5, 5, 5))

    def test_base_exception(self):
        kwargs = {'key':-1, 'valueName':'m0she', 'valueData':1}
        self._test_base_exception(kwargs, errors.RegistryBaseException)

