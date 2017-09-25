Django Scripts Tracker
======================
An unofficial Django utility tool that tracks management scripts execution.

### What does it mean _to track script execution_?
Scripts tracker watches manage.py scripts located in ``your_app/management/commands`` directory and just after you pull
some new code and apply its migrations - you will get notified about new (or modified) manage.py scripts that should
be applied for the project to work properly.

## Quick feature preview
**Step 1** - decorate your management script handle() method with ``@tracked_script`` decorator and push it to repository:

    class Command(BaseCommand):
        help = 'Populates Facility code_part_1 with appropriate data'

        @tracked_script
        def handle(self, *args, **options):
            for f in Facility.objects.all():
                f.code_part_1 = f.full_resort_code[:12]
                f.save()

**Step 2** - anyone who pulls your changes and runs migrations (``python manage.py migrate``) will get a notification
message:

    $ python manage.py migrate
    (...)
    Running migrations:
      (...)
    Checking management scripts:
      You have 1 new and 0 modified management scripts to be applied.
    New scripts (1):
      your_app/management/commands/populate_code_part_1.py
        Populates Facility code_part_1 with appropriate data

## Getting started

### Installation

1. Install the app using ``pip`` package manager:

        pip install django-scripts-tracker

2. Add ``django_scripts_tracker`` to your ``INSTALLED_APPS`` setting:

        # your_app/settings.py
        INSTALLED_APPS = [
            # (...)
            'django_scripts_tracker',
        ]

3. Run migrations in order to create tracker models:

        python manage.py migrate

4. Configure directories that should be scanned for management scripts:

        # your_app/settings.py
        COMMANDS_DIRS = [
            'your_app/management/commands',
            'another_app/management/commands',
        ]


### Usage

#### How to add a new tracked script?

1. Create a new management script under a tracked ``(...)/management/commands/`` directory
(tracked directories are defined in ``COMMANDS_DIRS``).

2. Decorate either ``handle()`` or ``handle_noargs()`` Command method with a ``@tracked_script`` decorator.

3. Make sure that the created script file is not ingored and is within a tracked directory.


#### How to check if there are unapplied scripts?

Script checking process takes place every time you perform DB migrations, but you can also invoke it manually:

    python manage.py check_scripts


#### How to mark scripts as "applied" ones?

If there are some scripts that have already been applied but the tracker lists them - it is possible to mark them
manually as applied ones.

To mark scripts as "applied" ones type in the following command:

    python manage.py check_scripts --mark-all-applied