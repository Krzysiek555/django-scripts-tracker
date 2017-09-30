import hashlib
import imp
import os

from django_scripts_tracker.settings import TERM_COLORS


def print_scripts(script_paths):
    """ Prints out the list of scripts with their descriptions """
    for script_path in script_paths:
        help = _get_script_help(script_path)
        print(u'  {GREEN}{path}{NC}\n'
              u'    {descr}'.format(path=script_path, descr=help, **TERM_COLORS))


def _get_script_help(script_path):
    (path, name) = os.path.split(script_path)
    (name, ext) = os.path.splitext(name)
    fm = imp.find_module(name, [path])
    try:
        module_ = imp.load_module(name, *fm)  # load the script module to gather the help content
        return module_.Command.help
    finally:
        fm[0].close()


def get_script_path(script_module):
    """ Changes: management.commands.test into: management/commands/test.py """
    return os.path.join(*script_module.__name__.split('.')) + '.py'


def get_hash(file_name, mode='md5'):
    CHUNK_SIZE = 8192
    h = hashlib.new(mode)

    with open(file_name, 'rb') as file:
        block = file.read(CHUNK_SIZE)
        while block:
            h.update(block)
            block = file.read(CHUNK_SIZE)

    return h.hexdigest()
