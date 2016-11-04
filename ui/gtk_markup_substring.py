#!/usr/bin/env python
#
# Lara Maia <dev@lara.click> 2015 ~ 2016
#
# The Steam Tools is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# The Steam Tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk


def set_from_css(widget, styles, params):
    context = widget.get_style_context()

    markup = []
    for style, param in zip(styles, params):
        context.save()
        context.add_class(style)
        foreground = context.get_color(Gtk.StateFlags.NORMAL)

        foreground_hex = '#'
        for color in foreground.to_string()[4:-1].split(','):
            foreground_hex += '{:02x}'.format(int(color))

        markup.append('<span color="{}">{} </span>'.format(foreground_hex, param))

        context.restore()

    widget.set_markup(''.join(markup))
