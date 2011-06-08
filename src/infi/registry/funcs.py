
import logging
from . import constants
from .dtypes import LONG, BYTE, LPCWSTR

def raise_exception_if_necessary(result, func, args):
    from ctypes import WinError
    if result != constants.ERROR_SUCCESS:
        raise WinError(result)
    return args

def _build_args_for_winfunctype(return_value, parameters):
    args = (return_value,)
    for parameter_tuple in parameters:
        args += (parameter_tuple[0],)
    return args

def _build_paramflags_for_prototype(parameters):
    paramflags = tuple()
    for parameter_tuple in parameters:
        paramflags += (parameter_tuple[1:],)
    return paramflags

def wrap_advapi32_function(name, return_value=LONG, parameters=()):
    """ this function wraps functions from advapi32.dll
    name            function name
    return_value    ctypes type
    parameters      tuple of the following form:
                    (ctypes_type, in/out, name, default_value)
    """
    from ctypes import windll, WINFUNCTYPE

    args = _build_args_for_winfunctype(return_value, parameters)
    _prototype = WINFUNCTYPE(*args)
    _paramflags = _build_paramflags_for_prototype(parameters)
    _function = _prototype((name, windll.advapi32), _paramflags)
    _function.errcheck = raise_exception_if_necessary
    return _function

def item_to_unicode(item):
    try:
        return unicode(item)
    except:
        raise TypeError("item cannot be formatted in unicode")
