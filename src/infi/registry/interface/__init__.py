__import__("pkg_resources").declare_namespace(__name__)

import logging
from .. import constants, c_api, errors, dtypes

def RegCloseKey(key):
    """ Closes a handle to the specified registry key
    
    Parameters
    key    A handle to the open key to be closed
    
    Return Value
    If the function succeeds, the return value is None.
    Else, a CloseKeyFailed exception is raised, unless:
    The handle is invalid, and an InvalidHandleException is raised
    
    Notes
    Closing a closed handle doesn't raise an exception
    """
    try:
        return c_api.RegCloseKey(key)
    except errors.WindowsError, exception:
        errors.catch_and_raise_general_errors(exception)
        logging.exception(exception)
        raise errors.CloseKeyFailed

def RegConnectRegistry(machineName, key):
    """ Establishes a connection to a predefined registry handle on another computer.
    
    Parameters
    machineName    The name of the remote computer, of the form \\computername. If None, the local computer is used.
    key            The predefined registry handle. On a remote computer, only HKEY_LOCAL_MACHINE and HKEY_USERS are allowed. 
    
    Return Value 
    If the function succeeds, it returns a key handle identifying the predefined handle on the remote computer.
    If the fuction fails, a ConnectRegistryFailed exception is raised, unless:
    If the predefined key is not allowed, an ValueError exception is raised.
    If the connection to the remote computer has failed, a RemoteRegistryConnectionFailed exception is raised, unless:
    If the connection failed, an AccessDeniedException will be raised
    
    Notes
    This function does not support the additional predefined handles added in Windows Vista
    """
    ALLOWED_KEYS_REMOTE = [constants.HKEY_LOCAL_MACHINE, constants.HKEY_USERS]
    ALLOWED_KEYS_LOCAL = ALLOWED_KEYS_REMOTE + [constants.HKEY_CURRENT_USER, constants.HKEY_CLASSES_ROOT,
                                                constants.HKEY_CURRENT_CONFIG]
    if machineName is None and key not in ALLOWED_KEYS_LOCAL:
        raise ValueError
    if machineName is not None and key not in ALLOWED_KEYS_REMOTE:
        raise ValueError

    try:
        return c_api.RegConnectRegistryW(machineName, key)
    except errors.WindowsError, exception:
        errors.catch_and_raise_general_errors(exception)
        logging.exception(exception)
        raise errors.ConnectRegistryFailed

def RegCopyTree():
    # TODO Implement RegCopyTree
    raise NotImplementedError # pragma: no cover

def RegCreateKeyEx(key, subKey, samDesired=constants.KEY_ALL_ACCESS):
    """ Creates the specified key, or opens the key if it already exists.
    
    Parameters
    key        An already open key. The calling process must have KEY_CREATE_SUB_KEY access to the key.
    subKey     The name of a key that this method opens or creates.
               This key must be a subkey of the key identified by the key parameter
    
    Return Value
    The return value is the handle of the opened key.
    If the function fails, a CreateKeyFailed exception is raised, unless:
    In case of bad permissions, an AccessDeniedException is raised
    If the key is not open, an InvalidHandleException is raised
    
    Notes
    This function does not support the transaction, options and securityAttributes arguments.
    """
    try:
        return c_api.RegCreateKeyExW(key, subKey, 0, None, 0, samDesired, None)[0]
    except errors.WindowsError, exception:
        errors.catch_and_raise_general_errors(exception)
        logging.exception(exception)
        raise errors.CreateKeyFailed(exception.winerror, exception.strerror)

def RegCreateKeyTransacted():
    raise NotImplementedError # pragma: no cover

def RegDeleteKey(key, subKey):
    """ Deletes the specified key.  The calling process must have KEY_DELETE access rights.
    This method can not delete keys with subkeys.
    
    Parameters
    key     An already open key.
    subKey  The name of the key to delete, in string format 
            This key must be a subkey of the key identifier by the key parameter.
            This value must not be None, and the key cannot have subkeys.
    
    Return Value
    If the function succeeds, it returns None
    If the function fails, it raises a DeleteKeyFailed exception, unless:
    If the key is not open, an InvalidHandleException is raised
    If subKey is None, the function raises a InvalidParameterException
    if subKey does not exist, a KeyError exception is raised
    If subKey contains subKey, an AccessDeniedException will be raised
    In case of bad permissions, an AccessDeniedException will be raised
    """
    try:
        result = c_api.RegDeleteKeyW(key, subKey)
    except errors.WindowsError, exception:
        errors.catch_and_raise_general_errors(exception)
        logging.exception(exception)
        raise errors.DeleteKeyFailed(exception.winerror, exception.strerror)

def RegDeleteKeyEx():
    # This is supported only Windows 64bit
    # TODO Implement RegDeleteKeyEx
    raise NotImplementedError #pragma: no cover

def RegDeleteKeyTransacted():
    # TODO Implement RegDeleteKeyTransacted
    raise NotImplementedError #pragma: no cover

def RegDeleteKeyValue():
    # TODO Implement RegDeleteKeyValue
    raise NotImplementedError #pragma: no cover

def RegDeleteValue(key, valueName=None):
    """ Removes the specified value from the specified registry key .
    
    Parameters
    key         A handle to an open registry key. The Key must have been opened with the KEY_SET_VALUE access right.
    valueName   The registry value to be removed from the key. If None, the default value is cleared
    
    Return Value
    If the function succeeds, the return value is None
    If the function fails, a DeleteKeyValueFailed exception is raised, unless:
    If the key is not open, an InvalidHandleException is raised
    if valueName does not exist, a KeyError exception is raised
    If access is denied, an AccesDeniedException isRaised
    """
    try:
        result = c_api.RegDeleteValueW(key, valueName)
    except errors.WindowsError, exception:
        errors.catch_and_raise_general_errors(exception)
        logging.exception(exception)
        raise errors.DeleteValueFailed(exception.winerror, exception.strerror)

def RegDisablePredefinedCahce():
    raise NotImplementedError #pragma: no cover

def RegDisablePredefinedCacheex():
    raise NotImplementedError #pragma: no cover

def RegDisableReflectionKey():
    raise NotImplementedError #pragma: no cover

def RegEnableReflectionKey():
    raise NotImplementedError #pragma: no cover

def RegEnumKeyEx(key, index):
    """ Enumerates the subkeys of the specified open registry key. 
    The function retrieves information about one subkey each time it is called.

    Parameters
    key         A handle to an open registry key. 
                The key must have been opened with the KEY_ENUMERATE_SUB_KEYS access right
    index       The index of the subkey to retrieve. This parameter should be zero for the first call to the 
                RegEnumKeyEx function and then incremented for subsequent calls.
                Because subkeys are not ordered, any new subkey will have an arbitrary index. 
                This means that the function may return subkeys in any order.
    
    Return Value
    If the function succeeds, the return value is the name of the subkey.
    If the function fails, a RegistryBaseException is raised, unless:
    If the key is not open, an InvalidHandleException is raised
    If access is denied, an AccesDeniedException isRaised
    If the index is too large, an IndexError exception is raised
    """
    try:
        (name, nameSize, classType, classTypeSize, lastWriteTime) = c_api.RegEnumKeyExW(key=key, index=index)
        return name.value
    except errors.WindowsError, exception:
        errors.catch_and_raise_general_errors(exception)
        logging.exception(exception)
        raise errors.RegistryBaseException(exception.winerror, exception.strerror)

def RegEnumValue(key, index):
    """ Enumerates the values for the specified open registry key. 
    The function copies one indexed value name and data block for the key each time it is called.


    Parameters
    key         A handle to an open registry key. 
                The key must have been opened with the KEY_QUERY_VALUE access right
    index       The index of the subkey to retrieve. This parameter should be zero for the first call to the 
                RegEnumKeyEx function and then incremented for subsequent calls.
                Because subkeys are not ordered, any new subkey will have an arbitrary index. 
                This means that the function may return subkeys in any order.
    
    Return Value
    If the function succeeds, the return a tuple of the value's name and RegistryValue object data.
    If the function fails, a RegistryBaseException exception is raised, unless:
    If the key is not open, an InvalidHandleException is raised
    If access is denied, an AccesDeniedException isRaised
    If the index is too large, an IndexError exception is raised
    """
    try:
        (name, nameSize, dataType, data, dataLength) = c_api.RegEnumValueW(key=key, index=index)
        data = (dtypes.BYTE * dataLength.value)()
        (name, nameSize, dataType, data, dataLength) = c_api.RegEnumValueW(key=key, index=index,
                                                                    data=data, dataLength=dataLength)
        return name.value, dtypes.RegistryValueFactory().by_type(dataType)(data)
    except errors.WindowsError, exception:
        errors.catch_and_raise_general_errors(exception)
        logging.exception(exception)
        raise errors.RegistryBaseException(exception.winerror, exception.strerror)

def RegFlushKey(key):
    """ Writes all the attributes of the specified open registry key into the registry
    
    Parameters
    key    A handle to the open key to be closed
    
    Return Value
    If the function succeeds, the return value is None.
    Else, a FlushKeyError exception is raised, unless:
    The handle is invalid, and an InvalidHandleException is raised
    """
    try:
        return c_api.RegFlushKey(key)
    except errors.WindowsError, exception:
        errors.catch_and_raise_general_errors(exception)
        logging.exception(exception)
        raise errors.FlushKeyError

def RegGetKeySecurity():
    raise NotImplementedError #pragma: no cover

def RegLoadKey():
    # TODO Implement RegLoadKey
    raise NotImplementedError #pragma: no cover

def RegOpenKeyEx(key, subKey=None, samDesired=constants.KEY_ALL_ACCESS):
    """ Opens the specifics registry key.
    
    Parameters
    key            A handle to an open registry key.
    subKey        The name of the registry subkey to be opened. It is optional.
    samDesired    A mask that specifics the desired access rights to the key to be opened.
    
    Return Value
    If the function succeeds, it returns a handle to the opened key
    If the function fails, it raises an OpenKeyFailed exception, unless:
    In case of bad permissions, an AccessDeniedException is raised
    If the key is not open, an InvalidHandleException is raised
    If the subKey does not exist, a KeyError exception is raised
    
    Notes
    This function does not support the transaction, options and securityAttributes arguments.
    """
    try:
        return c_api.RegOpenKeyExW(key, subKey, 0, samDesired)
    except errors.WindowsError, exception:
        errors.catch_and_raise_general_errors(exception)
        logging.exception(exception)
        raise errors.OpenKeyFailed(exception.winerror, exception.strerror)

def RegQueryInfoKey(key):
    """Retreived information about the specified registry key
    
    Parameters
    key        A handle to an open registry key.
               The key must have been opened with the KEY_QUERY_VALUE access right.
    
    
    Return Value
    If the function succeeds, it returns a tuple of the following form:
        (subKeys, maxSubKeyLength, maxClassTypeLength, values, maxValueNameLength,
         maxValueLength)
    If the function fails, it raises a QueryInfoKeyFailed exception, unless:
    In case of bad permissions, an AccessDeniedException is raised
    If the key is not open, an InvalidHandleException is raised
    """
    try:
        result = c_api.RegQueryInfoKeyW(key)
        return result[2:8]
    except errors.WindowsError, exception:
        errors.catch_and_raise_general_errors(exception)
        logging.exception(exception)
        raise errors.QueryInfoKeyFailed(exception.winerror, exception.strerror)

def RegQueryValueEx(key, valueName=None):
    """ Retrieves the type and data for the specified registry value.

    Parameters
    key         A handle to an open registry key. 
                The key must have been opened with the KEY_QUERY_VALUE access right
    valueName   The name of the registry value. it is optional.
    
    Return Value
    If the function succeeds, the return a tuple of the value's name and RegistryValue object data.
    If the function fails, a RegistryBaseException exception is raised, unless:
    If the key is not open, an InvalidHandleException is raised
    If access is denied, an AccesDeniedException isRaised
    If the value does not exist, the function raises KeyError
    """
    try:
        (dataType, data, dataLength) = c_api.RegQueryValueExW(key=key, name=valueName)
        data = (dtypes.BYTE * dataLength.value)()
        (dataType, data, dataLength) = c_api.RegQueryValueExW(key=key, name=valueName,
                                                            data=data, dataLength=dataLength)
        return dtypes.RegistryValueFactory().by_type(dataType)(data)
    except errors.WindowsError, exception:
        errors.catch_and_raise_general_errors(exception)
        logging.exception(exception)
        raise errors.RegistryBaseException(exception.winerror, exception.strerror)

def RegReplaceKey():
    # TODO Implement RegReplaceKey
    raise NotImplementedError #pragma: no cover

def RegRestoreKey():
    # TODO Implement RegRestoreKey
    raise NotImplementedError #pragma: no cover

def RegSaveKey():
    # TODO Implement RegSaveKey
    raise NotImplementedError #pragma: no cover

def RegSaveKeyEx():
    # TODO Implement RegSaveKeyEx
    raise NotImplementedError #pragma: no cover

def RegSetKeyValue():
    raise NotImplementedError #pragma: no cover

def RegSetValueEx(key, valueName, valueData):
    """ Sets the data and type of a specified value under a registry key
    
    Parameters
    key             A handle to an open registry key. 
                    The key must have been opened with the KEY_SET_VALUE access right.
    valueName       The name of the value to be set.
                    If it is None or an empty string, the function sets the type and data
                    for the key's unnamed or default value. 
    valueDataType   the type of data.
    
    Return Value
    If the function succeeds, it returns None.
    If the function fails, a RegistryBaseException exception is raised, unless:
    If the key is not open, an InvalidHandleException is raised
    If access is denied, an AccesDeniedException isRaised
    If the value does not exist, the function returns None
    """
    from ctypes import sizeof
    try:
        regvalue = dtypes.RegistryValueFactory().by_value(valueData)
        data, dataType = regvalue.to_byte_array(), regvalue.registry_type
        result = c_api.RegSetValueExW(key=key, name=valueName, dataType=dataType,
                                      data=data, dataLength=sizeof(data))
    except errors.WindowsError, exception:
        errors.catch_and_raise_general_errors(exception)
        logging.exception(exception)
        raise errors.RegistryBaseException(exception.winerror, exception.strerror)

def RegUnLoadKey():
    # TODO Implement RegSaveKeyEx
    raise NotImplementedError #pragma: no cover

def RegSetKeySecurity():
    # TODO Implement RegSetKeySecurity
    raise NotImplementedError #pragma: no cover

def RegQueryReflectionKey():
    # TODO Implement RegQueryReflectionKey
    raise NotImplementedError #pragma: no cover

def RegOpenKeyTransacted():
    #TODO Implement RegOpenKeyTransacted
    raise NotImplementedError #pragma: no cover


# TODO add performance/memory-leaks tests
