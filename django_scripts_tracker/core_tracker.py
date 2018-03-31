import inspect
import os
from functools import wraps

from django_scripts_tracker.dependency_resolver import build_dependencies_dict, print_dependencies, run_scripts
from django_scripts_tracker.git_plugin import has_uncommited_changes
from django_scripts_tracker.models import AppliedManagementScripts
from django_scripts_tracker.settings import COMMANDS_DIRS, TERM_COLORS, CHECK_SCRIPT_GIT_STATUS
from django_scripts_tracker.tracker_commons import is_script_ignored, is_tracked_script, filter_unapplied_scripts
from django_scripts_tracker.utils import get_hash, get_script_path, print_scripts


def mark_script_as_applied(script_path):
    hash_ = get_hash(script_path)
    AppliedManagementScripts.objects.create(file_path=script_path, file_hash=hash_)


def tracked_script(decorated_func):
    """ Decorator which logs management scripts executions """

    @wraps(decorated_func)
    def wrapper(*args, **kwargs):
        result = decorated_func(*args, **kwargs)

        script_module = inspect.getmodule(decorated_func)
        script_path = get_script_path(script_module)
        if CHECK_SCRIPT_GIT_STATUS:
            if not has_uncommited_changes(script_path):
                mark_script_as_applied(script_path)
        else:
            mark_script_as_applied(script_path)

        return result

    wrapper._is_tracked_script = True
    return wrapper


def _get_trackable_scripts(cmd_dirs):
    """ Returns a list of scripts (list of script paths) that should be tracked for modifications """
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


def get_unapplied_scripts():
    script_paths = _get_trackable_scripts(COMMANDS_DIRS)
    new_scripts, modified_scripts = filter_unapplied_scripts(script_paths)
    return (new_scripts, modified_scripts)


def print_new_and_modified_scripts(new_scripts, modified_scripts, show_dependencies=False):
    print('{LIGHT_CYAN}Checking management scripts:{NC}\n'
          '  You have {new_count} new and {mod_count} modified management scripts to be applied.'.format(
        new_count=len(new_scripts), mod_count=len(modified_scripts), **TERM_COLORS))

    if len(new_scripts):
        print('{LIGHT_CYAN}New scripts ({count}):{NC}'.format(count=len(new_scripts), **TERM_COLORS))
        print_scripts(new_scripts)

    if len(modified_scripts):
        print('{LIGHT_CYAN}Modified scripts ({count}):{NC}'.format(count=len(modified_scripts), **TERM_COLORS))
        print_scripts(modified_scripts)

    if show_dependencies and len(new_scripts + modified_scripts):
        scripts_dependencies = build_dependencies_dict(new_scripts + modified_scripts)
        print_dependencies(scripts_dependencies, prefix='  ')


def check_scripts_signal_handler(sender, **kwargs):
    from django.conf import settings

    new_scripts, modified_scripts = get_unapplied_scripts()
    print_new_and_modified_scripts(new_scripts, modified_scripts)

    if hasattr(settings, 'SCRIPTS_TRACKER') and settings.SCRIPTS_TRACKER \
            and settings.SCRIPTS_TRACKER.get('auto_run', False):
        scripts_dependencies = build_dependencies_dict(new_scripts + modified_scripts)
        run_scripts(scripts_dependencies, True)
