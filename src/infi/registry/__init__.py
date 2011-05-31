from infi.registry.dtypes.value import RegistryValueFactory
__import__("pkg_resources").declare_namespace(__name__)

from dtypes.key import RegistryComputer, LocalComputer, KeyStore
from dtypes.value import RegistryValue, RegistryValueFactory
import constants
import errors

__all__ = ('RegistryComputer', 'LocalComputer', 'KeyStore',
           'RegistryValue', 'RegistryValueFactory', 'constants', 'errors')

__doc__ = """ A dict-like interface to the Windows Registry.

BY EXAMPLE
==========

First, lets open the registry. You can either browse the registry of the local computer:
>>> local_computer = LocalComputer()

You can also connect to a remote computer by:
>>> remote_computer = RegistryComputer(r'\\remotecomputer', sam=KEY_READ)
Through the LocalComputer instance, you can dive into the pre-defined registry hives, for example:
>>> local_computer.local_machine

Once inside a hive, browsing the subkeys is pretty easy. For example, you can either do
>>> sub_key = local_computer.local_machine['SOFTWARE']['Microsoft']['Windows NT']

or go straight:
>>> sub_key = local_computer.local_machine[r'SOFTWARE\Microsoft\Windows NT']

Both str and unicode formats are allowed.
other methods and generators you're used to from the dict obect are supported here.

Creating new keys is done like this:
>>> sub_key = local_computer.local_machine[r'SOFTWARE\Microsoft\Windows NT'][NewKey] = None # value can by anything

Registry keys are represented by the KeyStore class.
Access to registyr values is done through the ValueStore class, which is kind of a dict, just like the KeyStore class.
You can get it from the 'values_store' property of an KeyStore instance:
>>> same_value = sub_key.values_store['someValue']

The Windows registyr supports some basic data structures as value types, which this module translates to Python objects:
Registry Type       Python object            Disambiguity
REG_SZ              unicode
REG_EXPAND_SZ       unicode                  value.count('%') > 1
REG_MULTI_SZ        list(unicode, ...)
REG_BINARY          tuple(int, ...)
REG_DWORD           int                      value < 2**32
REG_QWORD           int

If you notice, there is some disambiguity here.
For example, unicode can be saved as REG_SZ and REG_EXAND_SZ.
This may be a problem when writing registry values, and we'll soon see how this modules handles this.

Registry values are wrapped by the RegistryValue class. Accessing the true pythonic value of is simple:
>>> print same_value.to_python_ojbect()

Writing values into the value store is done through the RegistryValueFactory class, which features:
* automatic resolution of registry type disambiguity, based on the actual value.
* manual override, if you still need it

Let's write some values for demonstration:
>>> sub_key.values_store['thisIsAString'] = RegistryValueFactory().by_value('helloWorld')
>>> sub_key.values_store['thisIsADword'] = RegistryValueFactory().by_value(3)

If you wish to manually define the type, you can:
>>> from constants import *
>>> sub_key.values_store['expandString'] = RegistryValueFactory().by_type(REG_EXPAND_SZ).('helloWorld')
>>> sub_key.values_store['thisIsQword'] = RegistryValueFactory().by_type(REG_QWORD)(3)

That's the basics.

EXCEPTIONS
Besides the obvious KeyError/ValueError/TypeError exceptions usually thrown by dict objects,
the module may throw registry-specific exceptions.
The base class for such exceptions is errors.RegistryBaseException

Most of the registry-specific exception are well handles by this module,
unless something goes wrong (if so, report to us).

The one you should consider handling is AccessDeniedException, which means you're using insufficient credentials.
Consider the case in which you're browsing the registry with full access, and you're getting to a key that you can
only read, and not write. In this case, you should switch to read-only permissions.
Consider another case in which you're in read-only access, but need to modify the registry key, so you'll need to
change permissions again.

In both of these scenarios, you should catch the AccessDenied exception, and either do:
* Instanciate the LocalComputer or RegistryComputer classes, with the new permissions and access the registry key again.
* call the change_permissions method.
"""
