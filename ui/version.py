import os
import sys
import importlib.machinery

__VERSION_MAJOR__ = '2'
__VERSION_MINOR__ = '0'
__VERSION_REVISION__ = '2'
__VERSION_EXTRA__ = 'GIT'

try:
    if hasattr(sys, "frozen") or not os.name == 'nt':
        __version_module_path__ = os.path.join(os.getcwd(), 'version.pyc')
        __version_class__ = importlib.machinery.SourcelessFileLoader('version', __version_module_path__)
        __version_module__ = __version_class__.load_module()

        for var in dir(__version_module__):
            locals()[var] = eval('__version_module__.' + var)
except FileNotFoundError:
    pass

__VERSION__ = '{}.{}.{} {}'.format(__VERSION_MAJOR__,
                                   __VERSION_MINOR__,
                                   __VERSION_REVISION__,
                                   __VERSION_EXTRA__)
