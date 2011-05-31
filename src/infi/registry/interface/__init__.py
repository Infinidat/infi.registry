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
        return _RegCloseKey(key)
    except WindowsError, exception:
        if _is_invalid_handle(exception):
            raise InvalidHandleException
        logging.exception(exception)
        raise CloseKeyFailed

def _RegConnectRegistryW(*args, **kwargs):
    _prototype = WINFUNCTYPE(LONG, LPCWSTR, HKEY, POINTER(HKEY))
    _parameters = (1, 'computerName'), (1, 'key'), (2, 'result')
    _function = _prototype(("RegConnectRegistryW", windll.advapi32), _parameters)
    _function.errcheck = _raise_exception_if_necessary
    return _function(*args, **kwargs)

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
        return _RegConnectRegistryW(machineName, key)
    except WindowsError, exception:
        if _is_connection_failed(exception):
            raise RemoteRegistryConnectionFailed(exception.winerror, exception.strerror)
        if _is_access_defined(exception):
            raise AccessDeniedException
        raise ConnectRegistryFailed

def RegCopyTree(keySrc, subKey, keyDest):
    # TODO Implement RegCopyTree
    raise NotImplementedError # pragma: no cover

def _RegCreateKeyExW(*args, **kwargs):
    _prototype = WINFUNCTYPE(LONG, HKEY, LPCWSTR, DWORD, LPCWSTR, DWORD, DWORD,
                             POINTER(SECURITY_ATTRIBUTES), POINTER(HKEY), POINTER(DWORD))
    _parameters = (1, 'key'), (1, 'subKey'), (1, 'reserved'), (1, 'classType'), (1, 'options'), \
                    (1, 'samDesired'), (1, 'securityAttributes'), (2, 'result'), (2, 'disposition')
    _function = _prototype(("RegCreateKeyExW", windll.advapi32), _parameters)
    _function.errcheck = _raise_exception_if_necessary
    return _function(*args, **kwargs)

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
        return _RegCreateKeyExW(key, subKey, 0, None, 0, samDesired, None)[0]
    except WindowsError, exception:
        if _is_invalid_handle(exception):
            raise InvalidHandleException
        if _is_access_defined(exception):
            raise AccessDeniedException
        logging.exception(exception)
        raise CreateKeyFailed(exception.winerror, exception.strerror)

def RegCreateKeyTransacted():
    raise NotImplementedError # pragma: no cover

def _RegDeleteKeyW(*args, **kwargs):
    _prototype = WINFUNCTYPE(LONG, HKEY, LPCWSTR)
    _parameters = (1, 'key'), (1, 'subKey'),
    _function = _prototype(("RegDeleteKeyW", windll.advapi32), _parameters)
    _function.errcheck = _raise_exception_if_necessary
    return _function(*args, **kwargs)

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
    If subKey is None, the function raises a TypeError
    if subKey does not exist, a KeyError exception is raised
    If subKey contains subKey, an AccessDeniedException will be raised
    In case of bad permissions, an AccessDeniedException will be raised
    """
    try:
        result = c_api.RegDeleteKeyW(key, subKey)
    except errors.WindowsError, exception:
        errors.catch_and_raise_general_errors(exception)
        logging.exception(exception)
        raise DeleteKeyFailed(exception.winerror, exception.strerror)

def RegDeleteKeyEx(key, subKey, samDesired=constants.KEY_ALL_ACCESS):
    # This is supported only Windows 64bit
    # TODO Implement RegDeleteKeyEx
    raise NotImplementedError #pragma: no cover

def RegDeleteKeyTransacted():
    # TODO Implement RegDeleteKeyTransacted
    raise NotImplementedError #pragma: no cover

def RegDeleteKeyValue(key, subKey=None, valueName=None):
    # TODO Implement RegDeleteKeyValue
    raise NotImplementedError #pragma: no cover

def _RegDeleteValueW(*args, **kwargs):
    _prototype = WINFUNCTYPE(LONG, HKEY, LPCWSTR)
    _parameters = (1, 'key'), (1, "valueName"),
    _function = _prototype(("RegDeleteValueW", windll.advapi32), _parameters)
    _function.errcheck = _raise_exception_if_necessary
    return _function(*args, **kwargs)

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
        raise DeleteValueFailed(exception.winerror, exception.strerror)

def RegDisablePredefinedCahce():
    raise NotImplementedError #pragma: no cover

def RegDisablePredefinedCacheex():
    raise NotImplementedError #pragma: no cover

def RegDisableReflectionKey():
    raise NotImplementedError #pragma: no cover

def RegEnableReflectionKey():
    raise NotImplementedError #pragma: no cover

def _RegEnumKeyExW(*args, **kwargs):
    _prototype = WINFUNCTYPE(LONG, HKEY, DWORD, wintypes.LPWSTR, POINTER(DWORD), POINTER(DWORD),
                             LPWSTR, POINTER(DWORD), POINTER(FILETIME))
    _parameters = (1, 'key'), (1, "index"), \
                  (2, 'name', create_unicode_buffer(constants.MAX_KEYNAME_LENGTH)), \
                  (3, 'nameSize', DWORD(constants.MAX_KEYNAME_LENGTH)), \
                  (0, 'reserved', None), \
                  (3, 'classType', create_unicode_buffer(constants.MAX_KEYNAME_LENGTH)), \
                  (3, 'classTypeSize', DWORD(constants.MAX_KEYNAME_LENGTH)), \
                  (2, 'lastWriteTime', FILETIME()),
    _function = _prototype(("RegEnumKeyExW", windll.advapi32), _parameters)
    _function.errcheck = _raise_exception_if_necessary
    return _function(*args, **kwargs)

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
        (name, nameSize, classType, classTypeSize, lastWriteTime) = _RegEnumKeyExW(key=key, index=index)
        return name.value
    except WindowsError, exception:
        if _is_invalid_handle(exception):
            raise InvalidHandleException
        if _is_access_defined(exception):
            raise AccessDeniedException
        if _is_no_more_items(exception):
            raise IndexError
        logging.exception(exception)
        raise RegistryBaseException(exception.winerror, exception.strerror)

def _RegEnumValueW(*args, **kwargs):
    _prototype = WINFUNCTYPE(LONG, HKEY, DWORD, LPWSTR, POINTER(DWORD), POINTER(DWORD),
                             POINTER(DWORD), POINTER(BYTE), POINTER(DWORD))
    _parameters = (1, 'key'), (1, "index"), \
                  (2, 'valueName', create_unicode_buffer(constants.MAX_VALUENAME_LENGTH)), \
                  (3, 'valueNameSize', DWORD(constants.MAX_VALUENAME_LENGTH)), \
                  (0, 'reserved', None), \
                  (2, 'valueType', DWORD()), \
                  (3, 'valueData', (BYTE * 0).from_address(0)), \
                  (3, 'valueDataSize', DWORD(0)),
    _function = _prototype(("RegEnumValueW", windll.advapi32), _parameters)
    _function.errcheck = _raise_exception_if_necessary
    return _function(*args, **kwargs)

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
        raise RegistryBaseException(exception.winerror, exception.strerror)

def _RegFlushKey(*args, **kwargs):
    _prototype = WINFUNCTYPE(LONG, HKEY)
    _parameters = (1, 'key'),
    _function = _prototype(("RegFlushKey", windll.advapi32), _parameters)
    _function.errcheck = _raise_exception_if_necessary
    return _function(*args, **kwargs)

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
        raise FlushKeyError

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
        return _RegOpenKeyExW(key, subKey, 0, samDesired)
    except WindowsError, exception:
        if _is_invalid_handle(exception):
            raise InvalidHandleException
        if _is_access_defined(exception):
            raise AccessDeniedException
        if _is_subkey_not_found(exception):
            raise KeyError
        logging.exception(exception)
        raise OpenKeyFailed(exception.winerror, exception.strerror)
    raise NotImplementedError

def _RegQueryInfoKeyW(*args, **kwargs):
    _prototype = WINFUNCTYPE(LONG, HKEY, LPWSTR, POINTER(DWORD), POINTER(DWORD),
                             POINTER(DWORD), POINTER(DWORD), POINTER(DWORD),
                             POINTER(DWORD), POINTER(DWORD), POINTER(DWORD),
                             POINTER(DWORD), POINTER(FILETIME))
    _parameters = (1, 'key'), \
                  (2, 'classType', create_unicode_buffer(constants.MAX_KEYNAME_LENGTH)), \
                  (3, 'classTypeLength', DWORD(constants.MAX_KEYNAME_LENGTH)), \
                  (0, 'reserved', None), (2, 'subKeys'), (2, 'maxSubKeyLength'), \
                  (2, 'maxClassTypeLength'), (2, 'values'), (2, 'maxValueNameLength'), \
                  (2, 'maxValueLength',), (2, 'securityDescriptor'), \
                  (2, 'lastWriteTime')
    _function = _prototype(("RegQueryInfoKeyW", windll.advapi32), _parameters)
    _function.errcheck = _raise_exception_if_necessary
    return _function(*args, **kwargs)

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
        result = _RegQueryInfoKeyW(key)
        return result[2:8]
    except WindowsError, exception:
        if _is_invalid_handle(exception):
            raise InvalidHandleException
        if _is_access_defined(exception):
            raise AccessDeniedException
        logging.exception(exception)
        raise QueryInfoKeyFailed(exception.winerror, exception.strerror)
    raise NotImplementedError

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
