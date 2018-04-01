import imp
import os
import subprocess

from django_scripts_tracker.settings import TERM_COLORS
from django_scripts_tracker.tracker_commons import filter_unapplied_scripts


def get_required_preceding_scripts(script_path):
    """ Gets required preceding scripts paths from a @required_preceding_script decorated script """
    (path, name) = os.path.split(script_path)
    (name, ext) = os.path.splitext(name)
    fm = imp.find_module(name, [path])
    try:
        module_ = imp.load_module(name, *fm)
        if hasattr(module_.Command, 'handle') and hasattr(module_.Command.handle, '_required_scripts'):
            return module_.Command.handle._required_scripts
        elif hasattr(module_.Command, 'handle_noargs') and hasattr(module_.Command.handle_noargs, '_required_scripts'):
            return module_.Command.handle_noargs._required_scripts
        else:
            return []
    finally:
        fm[0].close()


def build_dependencies_dict(script_paths):
    """ Builds a dict of scripts and their dependencies """
    scripts_dependencies = dict()
    for script_path in script_paths:
        required_scripts = get_required_preceding_scripts(script_path)
        new_scripts, modified_scripts = filter_unapplied_scripts(required_scripts)
        scripts_dependencies[script_path] = set(new_scripts + modified_scripts)

    return scripts_dependencies


def run_scripts(script_dependencies, print_executed_scripts=False):
    """ Runs all unapplied scripts resolving their dependencies """
    if len(script_dependencies) == 0:
        return

    for script_path, dependencies in script_dependencies.items():
        if len(dependencies) == 0:
            if print_executed_scripts:
                print('{LIGHT_CYAN}Running:{NC} {script}'.format(script=script_path, **TERM_COLORS))
            script_name = os.path.splitext(os.path.basename(script_path))[0]
            subprocess.call('python manage.py {}'.format(script_name), shell=True)
            new_dependencies_dict = _remove_script_from_dependencies(script_path, script_dependencies)
            return run_scripts(new_dependencies_dict, print_executed_scripts)

    raise Exception('Could not resolve dependencies')


def _remove_script_from_dependencies(executed_script, script_dependencies):
    """ Builds new dependencies dict skipping the executed script """
    new_dependencies = dict()
    for script_path, dependencies in script_dependencies.items():
        if script_path != executed_script:
            new_dependencies[script_path] = [d for d in dependencies if d != executed_script]
    return new_dependencies


def print_dependencies(scripts_dependencies, prefix=''):
    """ Prints script dependencies as a tree """

    def _recursive_traverse(scripts, depth_prefix=None):
        if not depth_prefix:
            depth_prefix = u''

        for index, script in enumerate(scripts, start=1):
            if index != len(scripts):
                line = u'\u251C\u2500'
            else:
                line = u'\u2514\u2500'  # last item

            if len(scripts_dependencies[script]) == 0:
                line += u'\u2500'
            else:
                line += u'\u252C'  # has child dependencies

            line += u'\u2500 ' + script
            print(prefix + depth_prefix + line)

            if index == len(scripts):
                depth_prefix += u'  '
            else:
                depth_prefix += u'\u2502 '

            _recursive_traverse(scripts_dependencies[script], depth_prefix)
            depth_prefix = depth_prefix[:-2]

    print('{LIGHT_CYAN}Script dependencies:{NC}'.format(**TERM_COLORS))
    _recursive_traverse(scripts_dependencies.keys())
