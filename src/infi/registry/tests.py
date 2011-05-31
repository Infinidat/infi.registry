
# -*- coding: utf-8 -*-

import unittest2
import mock
from . import interface, constants

class BaseTestCase(unittest2.TestCase):
    def setUo(self):
        pass

    def tearDown(self):
        pass

class RegCloseKey(BaseTestCase):
    def test_invalid_key_1(self):
        kwargs = {'key': 0}
        self.assertRaises(interface.InvalidHandleException, interface.RegCloseKey, **kwargs)

    def test_invalid_key_2(self):
        kwargs = {'key': 4}
        self.assertRaises(interface.InvalidHandleException, interface.RegCloseKey, **kwargs)

    def test_valid_close(self):
        open_key = self._get_open_key()
        self.assertEqual(None, interface.RegCloseKey(open_key))

    def _get_open_key(self):
        return interface.RegCreateKey(interface.RegConnectRegistry(None, constants.HKEY_LOCAL_MACHINE),
                                      'SOFTWARE')

    def test_double_close(self):
        open_key = self._get_open_key()
        self.assertEqual(None, interface.RegCloseKey(open_key))
        self.assertEqual(None, interface.RegCloseKey(open_key))

class RegConnectRegistry(BaseTestCase):

    @mock.patch("win32api.RegConnectRegistry")
    def test_invalid_local_key(self, mocked_function):
        kwargs = {'computerName': None,
                  'key': 0}
        self.assertRaises(interface.InvalidKeyException, interface.RegConnectRegistry, **kwargs)

    @mock.patch("win32api.RegConnectRegistry")
    def test_invalid_remote_key(self, mocked_function):
        kwargs = {'computerName': 'remoteComputer',
                  'key': constants.HKEY_CURRENT_USER}
        self.assertRaises(interface.InvalidKeyException, interface.RegConnectRegistry, **kwargs)

    @mock.patch("win32api.RegConnectRegistry")
    def test_valid_remote_keys(self, mocked_function):
        mocked_function.return_value = None
        kwargs = {'computerName': 'remoteComputer'}
        for key in [constants.HKEY_LOCAL_MACHINE, constants.HKEY_USERS]:
            kwargs['key'] = key
            self.assertEqual(None, interface.RegConnectRegistry(**kwargs))
        self.assertEqual(2, mocked_function.call_count)

    @mock.patch("win32api.RegConnectRegistry")
    def test_valid_local_keys(self, mocked_function):
        mocked_function.return_value = None
        kwargs = {'computerName': None}
        for key in [constants.HKEY_LOCAL_MACHINE, constants.HKEY_USERS, constants.HKEY_CURRENT_CONFIG,
                    constants.HKEY_CURRENT_USER, constants.HKEY_CLASSES_ROOT]:
            kwargs['key'] = key
            self.assertEqual(None, interface.RegConnectRegistry(**kwargs))
        self.assertEqual(5, mocked_function.call_count)

    def test_connect_to_local_machine(self):
        key = interface.RegConnectRegistry(None, constants.HKEY_LOCAL_MACHINE)
        self.assertGreater(key.handle, 0)

    def test_connect_to_remote_machine(self):
        import socket
        key = interface.RegConnectRegistry(r'\\%s' % socket.gethostname(), constants.HKEY_LOCAL_MACHINE)
        self.assertGreater(key.handle, 0)

    def test_connect_to_invalid_remote(self):
        kwargs = {'computerName': r'\\0.0.0.0',
                  'key': constants.HKEY_LOCAL_MACHINE}
        self.assertRaises(interface.RemoteRegistryConnectionFailed, interface.RegConnectRegistry, **kwargs)

    def test_connect_to_unauthorized_remote(self):
        kwargs = {'computerName': r'\\127.0.0.2',
                  'key': constants.HKEY_LOCAL_MACHINE}
        self.assertRaises(interface.RemoteRegistryConnectionFailed, interface.RegConnectRegistry, **kwargs)

class RegCreateKey(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        self.key = interface.RegConnectRegistry(None, constants.HKEY_LOCAL_MACHINE)

    def tearDown(self):
        interface.RegCloseKey(self.key)

    def test_create_existing_subkey(self):
        self.assertGreater(interface.RegCreateKey(self.key, 'SOFTWARE').handle, 0)

    def test_non_existing_subkey(self):
        # TODO Implement test
        raise unittest2.SkipTest

    def test_access_denied(self):
        # TODO Impelment test
        raise unittest2.SkipTest

    def test_closed_key(self):
        self.tearDown()
        kwargs = {'key': self.key,
                  'subKey': 'SOFTWARE'}
        self.assertRaises(interface.CreateKeyFailed, interface.RegCreateKey, **kwargs)

    def test_unicode_subkey_1(self):
        self.assertGreater(interface.RegCreateKey(self.key, u'SOFTWARE').handle, 0)

    def test_deep_subkey(self):
        self.assertGreater(interface.RegCreateKey(self.key, r'SOFTWARE\Microsoft').handle, 0)

class RegCreateKeyEx(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        self.key = interface.RegConnectRegistry(None, constants.HKEY_LOCAL_MACHINE)

    def tearDown(self):
        interface.RegCloseKey(self.key)

    def test_unicode_subkey_2(self):
        self.assertGreater(interface.RegCreateKey(self.key, u'SOFTWARE\\\xe2\x9f\xb2').handle, 0)
