from gi.repository import GObject
import inspect

from ..overrides import override
from ..importer import modules

Gedit = modules['Gedit']._introspection_module
__all__ = []

class MessageBus(Gedit.MessageBus):
    def create(self, object_path, method, **kwargs):
        tp = self.lookup(object_path, method)

        if not tp.is_a(Gedit.Message.__gtype__):
            return None

        kwargs['object-path'] = object_path
        kwargs['method'] = method

        return GObject.new(tp, **kwargs)

    def send_sync(self, object_path, method, **kwargs):
        msg = self.create(object_path, method, **kwargs)
        self.send_message_sync(msg)

        return msg

    def send(self, object_path, method, **kwargs):
        msg = self.create(object_path, method, **kwargs)
        self.send_message(msg)

        return msg

MessageBus = override(MessageBus)
__all__.append('MessageBus')

class Message(Gedit.Message):
    def __getattribute__(self, name):
        try:
            return Gedit.Message.__getattribute__(self, name)
        except:
            return getattr(self.props, name)

Message = override(Message)
__all__.append('Message')


def get_trace_info(num_back_frames=0):
    frame = inspect.currentframe().f_back
    try:
        for i in range(num_back_frames):
            frame = frame.f_back

        filename = frame.f_code.co_filename

        # http://code.activestate.com/recipes/145297-grabbing-the-current-line-number-easily/
        lineno = frame.f_lineno

        func_name = frame.f_code.co_name
        try:
            # http://stackoverflow.com/questions/2203424/python-how-to-retrieve-class-information-from-a-frame-object
            cls_name = frame.f_locals["self"].__class__.__name__
        except:
            pass
        else:
            func_name = "%s.%s" % (cls_name, func_name)

        return (filename, lineno, func_name)
    finally:
        frame = None

orig_debug_plugin_message_func = Gedit.debug_plugin_message

@override(Gedit.debug_plugin_message)
def debug_plugin_message(format, *format_args):
    filename, lineno, func_name = get_trace_info(2)
    orig_debug_plugin_message_func(filename, lineno, func_name, format % format_args)
__all__.append(debug_plugin_message)

# vi:ex:ts=4:et
