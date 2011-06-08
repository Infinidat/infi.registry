
import logging
import unittest2
import mock
from bunch import Bunch

import random
import string

from . import LocalComputer
from .dtypes.key import KeyStore, RegistryHive
from infi.registry.dtypes.key import ValueStore
from infi.registry.dtypes.value import RegistryValueFactory, RegistryValue
from infi.registry import constants, errors, dtypes

class MockedInterface(object):
    def __init__(self, func_name):
        self.func_name = func_name
        self.patcher = mock.patch('infi.registry.interface.%s' % self.func_name)
        self.mock = None

    def start(self):
        self.mock = self.patcher.start()

    def stop(self):
        self.patcher.stop()

class TestCase(unittest2.TestCase):
    def setUp(self):
        self._computer = self._get_computer()

    def tearDown(self):
        pass

    def _get_computer(self):
        raise NotImplementedError

class LocalMachineTestCase(TestCase):
    def _get_computer(self, sam=constants.KEY_READ):
        return LocalComputer(sam=sam)

    def test_hives_exists(self):
        self.assertIsInstance(self._computer.local_machine, RegistryHive)
        self.assertIsInstance(self._computer.current_user, RegistryHive)
        self.assertIsInstance(self._computer.classes_root, RegistryHive)
        self.assertIsInstance(self._computer.current_config, RegistryHive)
        self.assertIsInstance(self._computer.users, RegistryHive)

    def test_getitem_for_existing_keys_under_local_machine(self):
        reg = self._computer.local_machine
        self.assertIsInstance(reg, KeyStore)
        self.assertIsInstance(reg[r'SOFTWARE\Microsoft'], KeyStore)
        self.assertIsInstance(reg[r'SOFTWARE\Microsoft\Windows'], KeyStore)
        self.assertIsInstance(reg[ur'SOFTWARE\Microsoft\Windows NT'], KeyStore)

    def _walk_on_key(self, key, level=0):
        logging.debug('%s%s' % ('.' * level, key._relapath,))
        try:
            for subkey in key.itervalues():
                try:
                    self._walk_on_key(subkey, level + 1)
                except (errors.AccessDeniedException, KeyError):
                    pass
        except errors.AccessDeniedException:
            pass
        try:
            for value in key.values_store.itervalues():
                pass
        except errors.AccessDeniedException:
            pass

    def test_walk_1(self):
        hive = self._get_computer(constants.KEY_READ).local_machine
        self._walk_on_key(hive[r'SOFTWARE'])

    def test_walk_2(self):
        hive = self._get_computer(constants.KEY_READ).local_machine
        self._walk_on_key(hive[r'SYSTEM\CurrentControlSet\Services'])

    def test_iteritems(self):
        key = self._computer.local_machine[r'SOFTWARE\Microsoft\Windows NT\CurrentVersion']
        for item in key.iteritems():
            self.assertIsInstance(item[1], KeyStore)
            self.assertEqual(type(item[0]), unicode)
            self.assertGreater(len(item[0]), 0)
        for item in key.values_store.iteritems():
            self.assertIsInstance(item[1], RegistryValue)
            self.assertEqual(type(item[0]), unicode)
            self.assertGreater(len(item[0]), 0)

    def test_items(self):
        key = self._computer.local_machine[r'SOFTWARE\Microsoft\Windows NT\CurrentVersion']
        self.assertEqual(len(key.items()), len([item for item in key.iteritems()]))
        self.assertIsInstance(key.items()[0], tuple)
        self.assertEqual(len(key.values_store.items()), len([item for item in key.values_store.iteritems()]))
        self.assertIsInstance(key.values_store.items()[0], tuple)

    def test_iterkeys(self):
        key = self._computer.local_machine[r'SOFTWARE\Microsoft\Windows NT\CurrentVersion']
        for item in key.iterkeys():
            self.assertEqual(type(item), unicode)
            self.assertGreater(len(item), 0)
        for item in key.iterkeys():
            self.assertEqual(type(item), unicode)
            self.assertGreater(len(item), 0)

    def test_keys(self):
        key = self._computer.local_machine[r'SOFTWARE\Microsoft\Windows NT\CurrentVersion']
        self.assertEqual(len(key.keys()), len([item for item in key.iterkeys()]))
        self.assertIsInstance(key.keys()[0], unicode)
        self.assertEqual(len(key.values_store.keys()), len([item for item in key.values_store.iterkeys()]))
        self.assertIsInstance(key.values_store.keys()[0], unicode)

    def test_itervalues(self):
        key = self._computer.local_machine[r'SOFTWARE\Microsoft\Windows NT\CurrentVersion']
        for item in key.itervalues():
            self.assertIsInstance(item, KeyStore)
        for item in key.values_store.itervalues():
            self.assertIsInstance(item, RegistryValue)

    def test_values(self):
        key = self._computer.local_machine[r'SOFTWARE\Microsoft\Windows NT\CurrentVersion']
        self.assertEqual(len(key.values()), len([item for item in key.itervalues()]))
        self.assertIsInstance(key.values()[0], KeyStore)
        self.assertEqual(len(key.values_store.values()), len([item for item in key.values_store.itervalues()]))
        self.assertIsInstance(key.values_store.values()[0], RegistryValue)

    def _get_random_string(self):
        length = random.randint(1, 100)
        return ''.join(random.choice(string.ascii_letters + string.digits) for x in range(length))

    def test_a_workout(self):
        software = self._get_computer(constants.KEY_ALL_ACCESS).local_machine['SOFTWARE']
        hive_name = self._get_random_string()
        self.assertNotIn(hive_name, software)
        software[hive_name] = None
        self.assertIn(hive_name, software)
        key = software[hive_name]
        self.assertIsInstance(key, KeyStore)
        self.assertEqual(0, len(key.keys()))
        self.assertEqual(0, len(key.values_store.keys()))
        for k, v in ((self._get_random_string(), 1),
                     (self._get_random_string(), self._get_random_string()),
                     (self._get_random_string(), [self._get_random_string(), self._get_random_string()])):
            self.assertNotIn(k, key.values_store)
            key.values_store[k] = dtypes.RegistryValueFactory().by_value(v)
            self.assertIn(k, key.values_store)
            self.assertTrue(key.values_store.has_key(k))
            self.assertEqual(v, key.values_store[k].to_python_object())
        v = key.values_store.pop(k)
        self.assertIsInstance(v, RegistryValue)
        key.values_store.clear()
        self.assertEqual(0, len(key.keys()))
        self.assertEqual(0, len(key.values_store.keys()))
        key.change_permissions(constants.KEY_ALL_ACCESS)
        del(software[hive_name])
        self.assertNotIn(hive_name, software)

    def test_clear_key_with_subkeys(self):
        # TODO implement this important test
        raise unittest2.SkipTest

class MockLocalMachineTestCase(LocalMachineTestCase):
    def setUp(self):
        self._set_mocks_dictionary()
        self._start_all_mocks()
        LocalMachineTestCase.setUp(self)

    def _set_mocks_dictionary(self):
        self._mocks = Bunch()
        self._mocks.connect_registry = MockedInterface('RegConnectRegistry')
        self._mocks.open_key = MockedInterface('RegOpenKeyEx')
        self._mocks.query_value = MockedInterface('RegQueryValueEx')
        self._mocks.close_key = MockedInterface('RegCloseKey')
        self._mocks.query_info_key = MockedInterface('RegQueryInfoKey')
        self._mocks.enum_key = MockedInterface('RegEnumKeyEx')
        self._mocks.enum_value = MockedInterface('RegEnumValue')

    def _start_all_mocks(self):
        for mock in self._mocks.itervalues():
            mock.start()

    def tearDown(self):
        LocalMachineTestCase.tearDown(self)

    def _stop_all_mocks(self):
        for mock in self._mocks.itervalues():
            mock.stop()

    def _assert_calls_to_mock_name(self, mock_name, number):
        self.assertTrue(self._mocks[mock_name].mock.called)
        self.assertEqual(number, self._mocks[mock_name].mock.call_count)

    def _assert_calls_to_connect_registry(self, number):
        self._assert_calls_to_mock_name('connect_registry', number)

    def _assert_calls_to_open_key(self, number):
        self._assert_calls_to_mock_name('open_key', number)

    def test_hives_exists(self):
        LocalMachineTestCase.test_hives_exists(self)
        self._assert_calls_to_connect_registry(5)
        self._assert_calls_to_open_key(5)

    def test_getitem_for_existing_keys_under_local_machine(self):
        self._mocks.query_value.mock.side_effect = KeyError()
        LocalMachineTestCase.test_getitem_for_existing_keys_under_local_machine(self)
        self._assert_calls_to_connect_registry(1)
        self._assert_calls_to_open_key(4)

    def test_walk_1(self):
        raise unittest2.SkipTest

    def test_walk_2(self):
        raise unittest2.SkipTest

    def test_walk_3(self):
        raise unittest2.SkipTest

    def test_a_workout(self):
        raise unittest2.SkipTest

    def _prepare_mocks_for_iteration_tests(self):
        self._mocks.query_info_key.mock.return_value = [10, 0, 0, 10]
        key = self._computer.local_machine['SOFTWARE']
        value = RegistryValueFactory().by_value(u'someValue')
        self._mocks.enum_key.mock.return_value = u'someKey'
        self._mocks.enum_value.mock.return_value = u'someName', value

    def test_iteritems(self):
        self._prepare_mocks_for_iteration_tests()
        LocalMachineTestCase.test_iteritems(self)

    def test_items(self):
        self._prepare_mocks_for_iteration_tests()
        LocalMachineTestCase.test_items(self)

    def test_iterkeys(self):
        self._prepare_mocks_for_iteration_tests()
        LocalMachineTestCase.test_iterkeys(self)

    def test_keys(self):
        self._prepare_mocks_for_iteration_tests()
        LocalMachineTestCase.test_keys(self)

    def test_itervalues(self):
        self._prepare_mocks_for_iteration_tests()
        LocalMachineTestCase.test_itervalues(self)

    def test_values(self):
        self._prepare_mocks_for_iteration_tests()
        LocalMachineTestCase.test_values(self)

    # TODO add tests that check the dict-wrap
