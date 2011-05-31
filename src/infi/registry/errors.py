
import os
from . import constants

if os.name == 'nt':
    from __builtin__ import WindowsError
else:
    WindowsError = OSError

class RegistryBaseException(Exception):
    pass

class InvalidHandleException(RegistryBaseException):
    pass

class CloseKeyFailed(RegistryBaseException):
    pass

class RemoteRegistryConnectionFailed(RegistryBaseException):
    pass

class CreateKeyFailed(RegistryBaseException):
    pass

class InvalidParameterException(RegistryBaseException):
    pass

class AccessDeniedException(RegistryBaseException):
    pass

class ConnectRegistryFailed(RegistryBaseException):
    pass

class DeleteKeyFailed(RegistryBaseException):
    pass

class DeleteValueFailed(RegistryBaseException):
    pass

class FlushKeyError(RegistryBaseException):
    pass

class FunctionNotSupported(RegistryBaseException):
    pass

class OpenKeyFailed(RegistryBaseException):
    pass

class QueryInfoKeyFailed(RegistryBaseException):
    pass

def is_invalid_handle(exception):
    return exception.winerror == constants.ERROR_INVALID_HANDLE

def is_connection_failed(exception):
    return exception.winerror in [constants.ERROR_BAD_NETPATH, constants.RPC_S_INVALID_NET_ADDR]

def is_access_defined(exception):
    return exception.winerror == constants.ERROR_ACCESS_DENIED

def is_invalid_parameter(exception):
    return exception.winerror == constants.ERROR_INVALID_PARAMETER

def is_subkey_not_found(exception):
    return exception.winerror == constants.ERROR_FILE_NOT_FOUND

def is_no_more_items(exception):
    return exception.winerror == constants.ERROR_NO_MORE_ITEMS

def catch_and_raise_general_errors(exception):
    if is_invalid_handle(exception):
        raise InvalidHandleException(exception)
    if is_connection_failed(exception):
        raise RemoteRegistryConnectionFailed(exception)
    if is_access_defined(exception):
        raise AccessDeniedException(exception)
    if is_invalid_parameter(exception):
        raise InvalidParameterException(exception)
    if is_subkey_not_found(exception):
        raise KeyError
    if is_no_more_items(exception):
        raise IndexError
