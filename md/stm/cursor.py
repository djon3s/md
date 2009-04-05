from __future__ import absolute_import
from collections import MutableSequence, MutableSet, MutableMapping
from .interfaces import Cursor
from .transaction import allocate, readable, writable

__all__ = ('cursor', 'tdict', 'tlist', 'tset')


### Simple Cursor

class cursor(Cursor):
    __slots__ = ()
    StateType = dict

    def __new__(cls, *args, **kwargs):
	return allocated(cls, cls.StateType())

    def __getattr__(self, key):
	try:
	    return readable(self)[key]
	except KeyError:
	    raise AttributeError, key

    def __setattr__(self, key, value):
	try:
	    writable(self)[key] = value
	except KeyError:
	    raise AttributeError, key

    def __delattr__(self, key):
	try:
	    del writable(self)[key]
	except KeyError:
	    raise AttributeError, key

    def __reduce__(self):
	return (allocated, (type(self), self.__getstate__()))

    def __getstate__(self):
	return readable(self)

    def __sizeof__(self):
	return object.__sizeof__(self) + readable(self).__sizeof__()


### Pickling

def allocated(cls, state):
    if not isinstance(state, cls.StateType):
	state = cls.StateType(state)
    return allocate(object.__new__(cls), state)


### Collections

class _collection(cursor):

    def __contains__(self, item):
	return item in readable(self)

    def __iter__(self):
	return iter(readable(self))

    def __repr__(self):
	return repr(readable(self))

    def __lt__(self, other):
	return readable(self).__lt__(self.__cast(other))

    def __le__(self, other):
	return readable(self).__le__(self.__cast(other))

    def __eq__(self, other):
	return readable(self).__eq__(self.__cast(other))

    def __ne__(self, other):
	return readable(self).__ne__(self.__cast(other))

    def __gt__(self, other):
	return readable(self).__gt__(self.__cast(other))

    def __ge__(self, other):
	return readable(self).__ge__(self.__cast(other))

    def __cmp__(self, other):
	return readable(self).__cmp__(self.__cast(other))

    __hash__ = None

    def __len__(self):
	return readable(self).__len__()

    def __getitem__(self, i):
	return readable(self).__getitem__(i)

    def __setitem__(self, i, item):
	return writable(self).__setitem__(i, item)

    def __delitem__(self, i):
	return writable(self).__delitem__(self, i)

class tlist(_collection, MutableSequence):
    StateType = list

    def __init__(self, seq=()):
	self.extend(seq)

    def __getslice__(self, i, j):
	return allocated(type(self), readable(self).__getslice__(i, j))

    def __setslice__(self, i, j, other):
	return writable(self).__setslice__(i, j, self.__coerce(other))

    def __delslice__(self, i, j):
	return writable(self).__delslice__(i, j)

    def __add__(self, other):
	return allocated(
	    type(self), readable(self).__add__(self.__coerce(other))
	)

    def __radd__(self, other):
	return allocated(
	    type(self), readable(self).__radd__(self.__coerce(other))
	)

    def __iadd__(self, other):
	return writable(self).__iadd__(self.__coerce(other))

    def __mul__(self, n):
	return allocated(type(self), readable(self).__mul__(n))

    __rmul__ = __mul__

    def __imul__(self, n):
	return writable(self).__imul__(n)

    def __cast(self, other):
	return readable(self) if isinstance(other, tlist) else other

    def __coerce(self, other):
	if isinstance(other, tlist):
	    return readable(other)
	elif isinstance(other, self.StateType):
	    return other
	else:
	    return self.StateType(other)

    def append(self, item):
	return writable(self).append(item)

    def insert(self, i, item):
	return writable(self).insert(i, item)

    def pop(self, i=-1):
	return writable(self).pop(i)

    def remove(self, item):
	return writable(self).remove(item)

    def count(self, item):
	return readable(self).count(item)

    def index(item, *args):
	return readable(self).index(item, *args)

    def reverse(self):
	return writable(self).reverse()

    def sort(self, *args, **kwargs):
	return writable(self).sort(*args, **kwargs)

    def extend(self, other):
	return writable(self).extend(self.__cast(other))

class tdict(_collection, MutableMapping):

    ## Almost exactly the implementation of UserDict

    def __init__(self, dict=None, **kwargs):
	if dict is not None:
	    self.update(dict)
	if kwargs:
	    self.update(kwargs)

    def __getitem__(self):
	data = readable(self)
	if key in data:
	    return data[key]
	if hasattr(type(self), '__missing__'):
	    return self.__missing__(key)
	raise KeyError(key)

    def __cast(self, other):
	return readable(other) if isinstance(other, tdict) else other

    def clear(self):
	return writable(self).clear()

    def copy(self):
	import copy
	return allocate(copy.copy(self), copy.copy(readable(self)))

    @classmethod
    def fromkeys(cls, iterable, value=None):
	return allocated(cls, ((k, value) for k in iterable))

    def get(self, key, default=None):
	if key not in self:
	    return default
	return self[key]

    def has_key(self, key):
	return key in readable(self)

    def items(self):
	return readable(self).items()

    def iteritems():
	return readable(self).iteritems()

    def iterkeys():
	return readable(self).iterkeys()

    def itervalues(self):
	return readable(self).itervalues()

    def keys(self):
	return readable(self).keys()

    def pop(self, key, *args):
	return writable(self).pop(key, *args)

    def popitem(self):
	return writable(self).popitem()

    def setdefault(self, key, default=None):
	if key not in self:
	    self[key] = default
	return self[key]

    def update(self, dict=None, **kwargs):
	if not (dict or kwargs):
	    return
	data = writable(self)
	if dict: data.update(dict)
	if kwargs: data.update(dict)

    def values(self):
	return readable(self).values()

class tset(_collection, MutableSet):
    StateType = set

    def __init__(self, seq=None):
	if seq is not None:
	    self.update(seq)

    def __and__(self, other):
	return readable(self) & self.__coerce(other)

    def __iand__(self, other):
	return writable(self).__iand__(self.__coerce(other))

    def __ior__(self, other):
	return writable(self).__ior__(self.__coerce(other))

    def __isub__(self, other):
	return writable(self).__isub__(self.__coerce(other))

    def __ixor__(self, other):
	return writable(self).__ixor(self.__coerce(other))

    def __rand__(self, other):
	return readable(self).__rand__(self.__coerce(other))

    def __ror__(self, other):
	return readable(self).__ror__(self.__coerce(other))

    def __rsub__(self, other):
	return readable(self).__rsub__(self.__coerce(other))

    def __rxor__(self, other):
	return readable(self).__rxor__(self.__coerce(other))

    def __sub__(self, other):
	return readable(self) - self.__coerce(other)

    def __xor__(self, other):
	return readable(self) ^ self.__coerce(other)

    def __cast(self, other):
	return readable(self) if isinstance(other, tlist) else other

    def __coerce(self, other):
	if isinstance(other, tlist):
	    return readable(other)
	elif isinstance(other, self.StateType):
	    return other
	else:
	    return self.StateType(other)

    def add(self, *args):
	return writable(self).add(*args)

    def clear(self):
	return writable(self).clear()

    def copy(self):
	import copy
	return allocate(copy.copy(self), copy.copy(readable(self)))

    def difference(self, *args):
	return readable(self).difference(*args)

    def difference_update(self, *args):
	return writable(self).difference_update(*args)

    def discard(self, *args):
	return writable(self).discard(*args)

    def intersection(self, *args):
	return readable(self).intersection(*args)

    def intersection_update(self, *args):
	return writable(self).intersection_update(*args)

    def isdisjoint(self, *args):
	return readable(self).isdisjoint(*args)

    def issubset(self, *args):
	return readable(self).issubset(*args)

    def issuperset(self, *args):
	return readable(self).issuperset(*args)

    def pop(self, *args):
	return writable(self).pop(*args)

    def remove(self, *args):
	return writable(self).remove(*args)

    def symmetric_difference(self, *args):
	return readable(self).symmetric_difference(*args)

    def symmetric_difference_update(self, *args):
	return writable(self).symmetric_difference_update(*args)

    def union(self, *args):
	return readable(self).union(*args)

    def update(self, *args):
	return writable(self).update(*args)

