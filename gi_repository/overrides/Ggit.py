# -*- Mode: Python; py-indent-offset: 4 -*-
# vim: tabstop=4 shiftwidth=4 expandtab
#
# Copyright (C) 2012 - Jesse van den Kieboom
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

from gi.repository import Gio
from ..overrides import override
from ..module import get_introspection_module


Ggit = get_introspection_module('Ggit')
__all__ = []


def _wrap_iter_size(self):
    for i in range(0, self.size()):
        yield self.get(i)

def _wrap_iter_get(self):
    while self.next():
        yield self.get()

def _wrap_iter_get_by_index(self):
    for i in range(0, self.size()):
        yield self.get_by_index(i)

def _wrap_iter_next(self):
    while True:
        value = self.next()
        if value is None:
            break

        yield value

def _wrap_initable_init(self, *args, **kwargs):
    super(self.__class__, self).__init__(*args, **kwargs)
    Gio.Initable.init(self, None)

def _override_dyn(base, **kwargs):
    name = base.__name__

    try:
        cls = globals()[name]

    except KeyError:
        cls = override(type(name, (base,), {}))
        globals()[name] = cls
        __all__.append(name)

    for method, wrapper in kwargs.items():
        setattr(cls, method, wrapper)


for c in dir(Ggit):
    try:
        o = getattr(Ggit, c)

    except AttributeError:
        continue

    if not hasattr(o, '__gtype__'):
        continue

    # Add __str__ mapping using to_string
    if hasattr(o, 'to_string'):
        _override_dyn(o, __str__=o.to_string)

    # Add iterator pattern
    # GgitCommitParents, GgitIndexEntriesResolveUndo, GgitTree
    if hasattr(o, 'get') and hasattr(o, 'size'):
        _override_dyn(o, __iter__=_wrap_iter_size)

    # GgitBranchEnumerator
    elif hasattr(o, 'get') and hasattr(o, 'next'):
        _override_dyn(o, __iter__=_wrap_iter_get)

    # GgitIndexEntries
    elif hasattr(o, 'get_by_index') and hasattr(o, 'size'):
        _override_dyn(o, __iter__=_wrap_iter_get_by_index)

    # GgitRevisionWalker
    elif hasattr(o, 'next'):
        _override_dyn(o, __iter__=_wrap_iter_next)

    # GgitIndex, GgitRepository, GgitRevisionWalker, ...
    if o.__gtype__.is_a(Gio.Initable):
        _override_dyn(o, __init__=_wrap_initable_init)

# vi:ex:ts=4:et
