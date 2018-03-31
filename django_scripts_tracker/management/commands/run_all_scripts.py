# -*- coding: utf-8 -*-
from optparse import make_option

from django.core.management import BaseCommand

from django_scripts_tracker.core_tracker import get_unapplied_scripts
from django_scripts_tracker.dependency_resolver import run_scripts, build_dependencies_dict

VERBOSE = 'verbose'


class Command(BaseCommand):
    help = 'Runs all unapplied management scripts'

    if hasattr(BaseCommand, 'option_list'):
        # Django 1.7, 1.8, 1.9
        option_list = BaseCommand.option_list + (
            make_option('--verbose',
                        action='store_true',
                        dest=VERBOSE,
                        default=False,
                        help='Prints scripts that are being executed'),
        )
    else:
        # Django 1.10 and 1.11
        def add_arguments(self, parser):
            parser.add_argument('--verbose',
                                action='store_true',
                                dest=VERBOSE,
                                default=False,
                                help='Prints scripts that are being executed')

    def handle(self, *args, **options):
        new_scripts, modified_scripts = get_unapplied_scripts()
        scripts_dependencies = build_dependencies_dict(new_scripts + modified_scripts)

        run_scripts(scripts_dependencies, options[VERBOSE])
