import inspect
import os
from functools import wraps
from types import ModuleType

from django_scripts_tracker.settings import TERM_COLORS
from django_scripts_tracker.tracker_commons import is_script_ignored, is_tracked_script, filter_unapplied_scripts
from django_scripts_tracker.utils import print_scripts, get_script_path


class UserAbortingExecution(Exception):
    pass


def required_preceding_script(*modules):
    """ Decorator which checks if specified dependency scripts have been applied earlier """

    if any(not isinstance(m, ModuleType) for m in modules):
        raise TypeError('Arguments must be modules')

    script_paths = [get_script_path(m) for m in modules]

    for script_path in script_paths:
        if is_script_ignored(os.path.split(script_path)[1]) or not is_tracked_script(script_path):
            raise UserWarning(
                'The required preceding script: {} is either ignored or not tracked and therefore will never get marked as applied one upon execution.'.format(
                    script_path))

    def decorator(decorated_func):
        @wraps(decorated_func)
        def wrapper(*args, **kwargs):
            unapplied_preceding_scripts, modified_preceding_scripts = filter_unapplied_scripts(script_paths)

            if unapplied_preceding_scripts or modified_preceding_scripts:
                _print_warning(unapplied_preceding_scripts, modified_preceding_scripts)
                script_module = inspect.getmodule(decorated_func)
                script_path = get_script_path(script_module)
                if _ask_for_abort(script_path):
                    raise UserAbortingExecution(
                        '\n{GREEN}Script execution aborted by the user{NC}'.format(**TERM_COLORS))

            result = decorated_func(*args, **kwargs)
            return result

        wrapper._required_scripts = script_paths
        return wrapper

    return decorator


def _print_warning(unapplied_preceding_scripts, modified_preceding_scripts):
    print('{LIGHT_CYAN}Warning:{NC}'.format(**TERM_COLORS))
    if unapplied_preceding_scripts:
        print('  You have {} management scripts that should be applied before applying this script.'.format(
            len(unapplied_preceding_scripts)))
    if modified_preceding_scripts:
        print('  {} required management scripts were modified since their last execution.'.format(
            len(modified_preceding_scripts)))

    if unapplied_preceding_scripts:
        print('{LIGHT_CYAN}Unapplied scripts ({count}):{NC}'.format(count=len(unapplied_preceding_scripts),
                                                                    **TERM_COLORS))
        print_scripts(unapplied_preceding_scripts)
    if modified_preceding_scripts:
        print(
            '{LIGHT_CYAN}Modified scripts ({count}):{NC}'.format(count=len(modified_preceding_scripts), **TERM_COLORS))
        print_scripts(modified_preceding_scripts)


try:
    input = raw_input
except NameError:
    pass


def _ask_for_abort(current_script):
    print('It is adviced to abort the execution of this script and apply its required preceding scripts first.')

    res = input('Do you want to abort the execution of {}? [Y/N]\n'.format(current_script)).lower()
    while res not in ['y', 'n', 'yes', 'no']:
        res = input('Do you want to abort the execution of {}? [Y/N]\n'.format(current_script)).lower()

    if res in ['y', 'yes']:
        return True

    return False
