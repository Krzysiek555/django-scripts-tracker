import imp
import os

from django_scripts_tracker.models import AppliedManagementScripts
from django_scripts_tracker.settings import IGNORED_FILES, IGNORED_CMD_PREFIXES
from django_scripts_tracker.utils import get_hash


def filter_unapplied_scripts(file_paths):
    """ Returns scripts that have been added or modified """
    new_scripts = []
    modified_scripts = []
    for file_path in file_paths:
        hash_ = get_hash(file_path)
        if AppliedManagementScripts.objects.filter(file_hash=hash_).exists():
            continue  # script was applied and was not modified
        elif AppliedManagementScripts.objects.filter(file_path=file_path).exists():
            modified_scripts.append(file_path)  # script was applied but has been modified since then
        else:
            new_scripts.append(file_path)  # script was not applied
    return new_scripts, modified_scripts


def is_script_ignored(file_name):
    return not file_name.endswith('.py') \
           or file_name.lower() in IGNORED_FILES \
           or file_name.lower().startswith(IGNORED_CMD_PREFIXES)


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
