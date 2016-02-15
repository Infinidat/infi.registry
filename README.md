Overview
========
Python bindings to the Windows registry
Usage
-----

The first thing you do is open the registry for the local computer:

```python
>>> from infi.registry import LocalComputer
>>> local_computer = LocalComputer()
```

You can browse different registry hives:

```python
>>> local_machine = local_computer.local_machine
>>> current_usrr = local_computer.current_user
```

You can travel the hive in two ways:

```python
>>> # direct
>>> key = local_machine[r'Software\Microsoft\Windows NT\\CurrentVersion']
>>> # indirect
>>> key = local_machine['Software']['Microsoft']['Windows NT']['CurrentVersion']
```

Accessing a non-existing key raises KeyError.

The registry values are stored in a dictionary:

```python
>>> key.values_store.keys()[:2]
[u'CurrentVersion',
 u'CurrentBuild']
```

Updating a value is easy:
```pyhton
>>> from infi.registry import RegistryValueFactory
>>> factory = RegistryValueFactory()
>>> new_value = factory.by_value('this is a string')
>>> key.values_store['name'] = new_value
```

The by_value method guesses the registry value type but the type of the instance.
You can define the value type on our own by using factory.by_type method.

Checking out the code
=====================

To check out the code for development purposes, clone the git repository and run the following commands:

    easy_install -U infi.projector
    projector devenv build

Python 3
========
Python 3 support is experimental and untested at this stage.
