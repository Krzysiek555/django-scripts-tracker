import hashlib
import imp
import inspect
import os
from functools import wraps

from models import AppliedManagementScripts
from settings import COMMANDS_DIRS, IGNORED_CMD_PREFIXES, IGNORED_FILES, TERM_COLORS


def check_scripts_signal_handler(sender, **kwargs):
    new_scripts, modified_scripts = get_unapplied_scripts()
    print_new_and_modified_scripts(new_scripts, modified_scripts)


def get_unapplied_scripts():
    script_paths = _get_trackable_scripts(COMMANDS_DIRS, IGNORED_CMD_PREFIXES, IGNORED_FILES)
    new_scripts, modified_scripts = _filter_unapplied_scripts(script_paths)
    return (new_scripts, modified_scripts)


def print_new_and_modified_scripts(new_scripts, modified_scripts):
    def print_scripts(script_paths):
        """ Prints out the list of scripts with their descriptions """
        for script_path in script_paths:
            help = _get_script_help(script_path)
            print u'  {GREEN}{path}{NC}\n' \
                  u'    {descr}'.format(path=script_path, descr=help, **TERM_COLORS)

    print '{LIGHT_CYAN}Checking management scripts:{NC}\n' \
          '  You have {new_count} new and {mod_count} modified management scripts to be applied.'.format(
        new_count=len(new_scripts), mod_count=len(modified_scripts), **TERM_COLORS)

    if len(new_scripts):
        print '{LIGHT_CYAN}New scripts ({count}):{NC}'.format(count=len(new_scripts), **TERM_COLORS)
        print_scripts(new_scripts)

    if len(modified_scripts):
        print '{LIGHT_CYAN}Modified scripts ({count}):{NC}'.format(count=len(modified_scripts), **TERM_COLORS)
        print_scripts(modified_scripts)


def _get_trackable_scripts(cmd_dirs, ignored_cmd_prefixes, ignored_files):
    """ Returns a list of scripts (list of script paths) that should be tracked for modifications """

    def is_script_ignored(file_name):
        return not file_name.endswith('.py') \
               or file_name.lower() in ignored_files \
               or file_name.lower().startswith(ignored_cmd_prefixes)

    def is_tracked_script(script_path):
        """ Checks whether any of scripts handle methods was decorated with @tracked_script """
        (path, name) = os.path.split(script_path)
        (name, ext) = os.path.splitext(name)
        fm = imp.find_module(name, [path])
        try:
            module_ = imp.load_module(name, *fm)
            return hasattr(module_.Command.handle, '_is_tracked_script') \
                   or hasattr(module_.Command, 'handle_noargs') and hasattr(module_.Command.handle_noargs,
                                                                            '_is_tracked_script')
        finally:
            fm[0].close()

    script_paths = []
    for cmd_dir in cmd_dirs:
        for entry in os.listdir(cmd_dir):
            if not is_script_ignored(entry):
                # script file is not ignored -> check if @tracked_script decorator is present
                cmd_dir = os.path.join(*cmd_dir.split('/'))  # convert system dependant slashes
                script_path = os.path.join(cmd_dir, entry)
                if is_tracked_script(script_path):
                    script_paths.append(script_path)
    return script_paths


def _filter_unapplied_scripts(file_paths):
    """ Returns scripts that have been added or modified """
    new_scripts = []
    modified_scripts = []
    for file_path in file_paths:
        hash = get_hash(file_path)
        if AppliedManagementScripts.objects.filter(file_hash=hash).exists():
            continue  # script was applied and was not modified
        elif AppliedManagementScripts.objects.filter(file_path=file_path).exists():
            modified_scripts.append(file_path)  # script was applied but has been modified since then
        else:
            new_scripts.append(file_path)  # script was not applied
    return new_scripts, modified_scripts


def mark_script_as_applied(script_path):
    hash_ = get_hash(script_path)
    AppliedManagementScripts.objects.create(file_path=script_path, file_hash=hash_)


def _get_script_help(script_path):
    (path, name) = os.path.split(script_path)
    (name, ext) = os.path.splitext(name)
    fm = imp.find_module(name, [path])
    try:
        module_ = imp.load_module(name, *fm)  # load the script module to gather the help content
        return module_.Command.help
    finally:
        fm[0].close()


def get_hash(file_name, mode='md5'):
    CHUNK_SIZE = 8192
    h = hashlib.new(mode)

    with open(file_name, 'rb') as file:
        block = file.read(CHUNK_SIZE)
        while block:
            h.update(block)
            block = file.read(CHUNK_SIZE)

    return h.hexdigest()


def tracked_script(decorated_func):
    """ Decorator which logs management scripts executions """

    def resolve_script_path_from_function(func):
        module = inspect.getmodule(func)
        # changes: management.commands.test into: management/commands/test.py
        script_path = os.path.join(*module.__name__.split('.')) + '.py'
        return script_path

    @wraps(decorated_func)
    def wrapper(*args, **kwargs):
        result = decorated_func(*args, **kwargs)
        script_path = resolve_script_path_from_function(decorated_func)
        mark_script_as_applied(script_path)
        return result

    wrapper._is_tracked_script = True
    return wrapper
