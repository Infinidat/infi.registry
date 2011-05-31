
# -*- coding: utf-8 -*-

import logging
import unittest2
import mock
import os
from .. import interface, constants, dtypes, errors, funcs, c_api

class SameAsValue(object):
    pass

class BaseTestCase(unittest2.TestCase):
    _regtype = None

    def _get_factory(self):
        return dtypes.RegistryValueFactory().by_type(self._regtype)

    def _test_value_bidirectional(self, value, expected=SameAsValue()):
        regvalue = self._get_factory()(value)
        logging.debug(regvalue)
        byte_array = regvalue.to_byte_array()
        logging.debug([i for i in byte_array])
        actual = regvalue.from_byte_array(byte_array)
        logging.debug(repr(actual))
        logging.debug(repr(value))
        expected = value if isinstance(expected, SameAsValue) else expected
        self.assertEquals(expected, actual)

    def _test_detected_type(self, value, expected_type_error=False):
        expected = self._regtype
        if expected_type_error:
            self.assertRaises(TypeError, dtypes.RegistryValueFactory().by_value)
        else:
            actual = dtypes.RegistryValueFactory().by_value(value).registry_type
            self.assertEquals(expected, actual)

class RegSz(BaseTestCase):
    _regtype = constants.REG_SZ

    def test_empty_string(self):
        self._test_value_bidirectional('')

    def test_whitespace(self):
        self._test_value_bidirectional(' ')

    def test_abc(self):
        self._test_value_bidirectional('abc')

    def test_long_string(self):
        self._test_value_bidirectional('a' * 1024)

    def test_unicode_characters(self):
        self._test_value_bidirectional(u'\xe2\x9f\xb2')

    def test_detect_type(self):
        self._test_detected_type('fooBar')

class RegExpandSz(RegSz):
    _regtype = constants.REG_EXPAND_SZ

    def test_detect_type(self):
        self._test_detected_type('%fooBar%')

class RegLink(RegSz):
    _regtype = constants.REG_LINK

    def test_detect_type(self):
        raise unittest2.SkipTest

class RegMultiSz(BaseTestCase):
    _regtype = constants.REG_MULTI_SZ

    def test_empty_list(self):
        self._test_value_bidirectional([])

    def test_one_string(self):
        self._test_value_bidirectional(['abc', ])

    def test_one_empty_string(self):
        self._test_value_bidirectional(['', ], [])

    def test_three_strings(self):
        self._test_value_bidirectional(['a', 'b', 'c'])

    def test_long_list(self):
        self._test_value_bidirectional(['a', 'b', 'c'] * 1024)

    def test_detect_type(self):
        self._test_detected_type(['foo', 'bar'])

class RegDword(BaseTestCase):
    _regtype = constants.REG_DWORD

    def test_zero(self):
        self._test_value_bidirectional(0)

    def test_one(self):
        self._test_value_bidirectional(1)

    def test_range(self):
        for i in range (0, 64):
            self._test_value_bidirectional(i)

    def test_large_number(self):
        self._test_value_bidirectional(2 ** 32 - 1)

    def test_64bit_number(self):
        self._test_value_bidirectional(2 ** 32, 0)

    def test_detect_type(self):
        self._test_detected_type(1024)

class RegBinary(BaseTestCase):
    _regtype = constants.REG_BINARY

    def test_simple_tuple(self):
        self._test_value_bidirectional((1, 2, 3, 4,))

    def test_tuple_with_maximum_values(self):
        self._test_value_bidirectional((255,) * 200)

    def test_detect_type(self):
        self._test_detected_type((1, 2,))

    def test_detect_invalid_type(self):
        self._test_detected_type(('hi', 'bye'), True)
