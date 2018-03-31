# -*- coding: utf-8 -*-
from optparse import make_option

from django.core.management import BaseCommand

from django_scripts_tracker.core_tracker import get_unapplied_scripts, mark_script_as_applied, \
    print_new_and_modified_scripts

MARK_ALL_SCRIPTS_AS_APPLIED = 'mark_all_scripts_as_applied'
SHOW_DEPENDENCIES = 'show_dependencies'


class Command(BaseCommand):
    help = 'Checks whether there are some unapplied management scripts'

    if hasattr(BaseCommand, 'option_list'):
        # Django 1.7, 1.8, 1.9
        option_list = BaseCommand.option_list + (
            make_option('--mark-all-applied',
                        action='store_true',
                        dest=MARK_ALL_SCRIPTS_AS_APPLIED,
                        default=False,
                        help='Marks all management scripts as applied'),
            make_option('--show-dependencies',
                        action='store_true',
                        dest=SHOW_DEPENDENCIES,
                        default=False,
                        help='Prints unapplied scripts and their unapplied dependencies'),
        )
    else:
        # Django 1.10 and 1.11
        def add_arguments(self, parser):
            parser.add_argument('--mark-all-applied',
                                action='store_true',
                                dest=MARK_ALL_SCRIPTS_AS_APPLIED,
                                default=False,
                                help='Marks all management scripts as applied')
            parser.add_argument('--show-dependencies',
                                action='store_true',
                                dest=SHOW_DEPENDENCIES,
                                default=False,
                                help='Prints unapplied scripts and their unapplied dependencies')

    def handle(self, *args, **options):
        if options[MARK_ALL_SCRIPTS_AS_APPLIED]:
            self.mark_all_scripts_as_applied()
        else:
            new_scripts, modified_scripts = get_unapplied_scripts()
            print_new_and_modified_scripts(new_scripts, modified_scripts, options[SHOW_DEPENDENCIES])

    @staticmethod
    def mark_all_scripts_as_applied():
        new_scripts, modified_scripts = get_unapplied_scripts()

        for script_path in new_scripts + modified_scripts:
            mark_script_as_applied(script_path)
