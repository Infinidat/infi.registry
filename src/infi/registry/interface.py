

# Windows API for the Registry

import logging
from . import constants

class RegistryBaseException(Exception):
    pass

class InvalidHandleException(RegistryBaseException):
    pass

class InvalidKeyException(RegistryBaseException):
    pass

class RemoteRegistryConnectionFailed(RegistryBaseException):
    pass

class CreateKeyFailed(RegistryBaseException):
    pass

class InvalidParameterException(RegistryBaseException):
    pass

def RegCloseKey(key):
    """ Closes a previously opened registry key.
    
    Parameters
    key    the key to be closed
    
    Return Value
    If the function succeeds, the return value is None.
    Else, an InvalidHandleException is raised
    """
    import win32api, pywintypes
    try:
        return win32api.RegCloseKey(key)
    except pywintypes.error, exception:
        raise InvalidHandleException(exception.winerror, exception.strerror)

def RegConnectRegistry(computerName, key):
    """ Establishes a connection to a predefined registry handle on another computer.
    
    Parameters
    computerName    The name of the computer, of the form \\computername. If None, the local computer is used.
    key             The predefined handle. On a remote computer, only HKEY_LOCAL_MACHINE and HKEY_USERS are allowed. 
    
    Return Value 
    Establishes a connection to a predefined registry handle on another computer.
    If the key is not allowed, an InvalidKeyException is raised.
    If the connection to the remote computer has failed, a RemoteRegistryConnectionFailed exception is raised
    
    Notes
    This function does not support the additional predefined handles added in Windows Vista
    """
    import win32api, pywintypes
    ALLOWED_KEYS_REMOTE = [constants.HKEY_LOCAL_MACHINE, constants.HKEY_USERS]
    ALLOWED_KEYS_LOCAL = ALLOWED_KEYS_REMOTE + [constants.HKEY_CURRENT_USER, constants.HKEY_CLASSES_ROOT,
                                                constants.HKEY_CURRENT_CONFIG]
    if computerName is None and key not in ALLOWED_KEYS_LOCAL:
        raise InvalidKeyException
    if computerName is not None and key not in ALLOWED_KEYS_REMOTE:
        raise InvalidKeyException
    try:
        return win32api.RegConnectRegistry(computerName, key)
    except pywintypes.error, exception:
        logging.exception(exception)
        if exception.winerror in [constants.ERROR_BAD_NETPATH, constants.RPC_S_INVALID_NET_ADDR,
                                  constants.ERROR_ACCESS_DENIED]:
            # TODO are there are other errors numbers that should be caught here?
            raise RemoteRegistryConnectionFailed(exception.winerror, exception.strerror)
        raise InvalidHandleException(exception.winerror, exception.strerror)

def RegCopyTree(keySrc, subKey, keyDest):
    """ Copies an entire registry key to another location

    Parameters
    keySrc    Registry key to be copied
    subKey    a unicode string to be copied, can be None
    keyDest   The distination key
    
    Return Value
    This function is not implemented
    """
    # TODO Implement RegCopyTree
    raise NotImplementedError

def RegCreateKey(key, subKey):
    """ Creates the specified key, or opens the key if it already exists.
    
    Parameters
    key        An already open key. The calling process must have KEY_CREATE_SUB_KEY access to the key.
    subKey     The name of a key that this method opens or creates.
               This key must be a subkey of the key identified by the key parameter
    
    Return Value
    The return value is the handle of the opened key.
    If the function fails, a CreateKeyFailed exception is raised.
    """
    import win32api, pywintypes
    try:
        return win32api.RegCreateKey(key, subKey)
    except pywintypes.error, exception:
        logging.exception(exception)
        raise CreateKeyFailed(exception.winerror, exception.strerror)

def RegCreateKeyEx(key, subKey, samDesired=constants.KEY_ALL_ACCESS):
    """ Extended version of RegCreateKey
    
    Parameters
    key            An already open key. The calling process must ahve KEY_CREATE_SUB_KEY access to the key.
    subKey         Unicode name of subkey to open or create.
    samDesired     combination of constants.KEY_* constants.    
    Return Value
    
    Notes
    This function does not support the transaction, options and securityAttributes arguments.
    """

    import win32api, pywintypes
    try:
        return win32api.RegCreateKeyEx(key, subKey, samDesired, None, 0, None, None)
    except pywintypes.error, exception:
        logging.exception(exception)
        raise CreateKeyFailed(exception.winerror, exception.strerror)
