[![PyPI version](https://badge.fury.io/py/django-scripts-tracker.svg)](https://badge.fury.io/py/django-scripts-tracker)
[![Code Health](https://landscape.io/github/Krzysiek555/django-scripts-tracker/master/landscape.svg?style=flat)](https://landscape.io/github/Krzysiek555/django-scripts-tracker/master)
![Python versions](https://img.shields.io/pypi/pyversions/django-scripts-tracker.svg)
![Django versions](https://img.shields.io/badge/django-1.7%2C%201.8%2C%201.11-blue.svg)
![License](https://img.shields.io/pypi/l/django-scripts-tracker.svg)

Django Scripts Tracker
======================

An unofficial Django utility tool that tracks management scripts execution.

**What does it mean "to track script execution"?**

Scripts tracker watches manage.py scripts located in ``your_app/management/commands`` directory and just after you pull
some new code and apply its migrations - you will get notified about new (or modified) manage.py scripts that should
be applied for the project to work properly.

**Script dependencies**

Furthermore scripts tracker enables ensuring proper order of scripts execution through defining their 
"required preceeding scripts" (aka dependencies).

Quick feature preview
---------------------

**Step 1:** When you create a new management script, decorate `handle()` method with `@tracked_script` decorator 
and push it to repository:

```python
class Command(BaseCommand):
    help = 'Some sample script help text'

    @tracked_script
    def handle(self, *args, **options):
        # (...)
```

**Step 2:** Anyone who pulls your changes and runs migrations, will get a notification message that there is a new 
script to be applied:

    $ python manage.py migrate
    (...)
    Running migrations:
      (...)
    Checking management scripts:
      You have 1 new and 0 modified management scripts to be applied.
    New scripts (1):
      your_app/management/commands/sample_management_script.py
        Some sample script help text

Installation
------------

1. Install the app using `pip` package manager::

        pip install django-scripts-tracker

2. Add `django_scripts_tracker` to your `INSTALLED_APPS` setting:

    ```python
    # your_app/settings.py
    INSTALLED_APPS = [
        # (...)
        'django_scripts_tracker',
    ]
    ```

3. Run migrations in order to create tracker models::

        python manage.py migrate

4. Configure directories that should be scanned for management scripts:

    ```python
    # your_app/settings.py
    COMMANDS_DIRS = [
        'your_app/management/commands',
        'another_app/management/commands',
    ]
    ```

Usage
-----

### How to add a new tracked script?

1. Create a new management script under a tracked `(...)/management/commands/` directory (tracked directories are 
defined in `COMMANDS_DIRS`).

2. Decorate either `handle()` or `handle_noargs()` Command method with a `@tracked_script` decorator.

3. Make sure that the created script file is not ingored and is within a tracked directory.


### How to check if there are unapplied scripts?

Script checking process takes place every time you perform DB migrations, but you can also invoke it manually:

    python manage.py check_scripts


### How to mark scripts as "applied" ones?

Scripts are automatically marked as applied ones just after their execution.

If there are some scripts that have already been applied but the tracker lists them - it is possible to mark them
manually as applied ones.

To mark scripts as "applied" ones type in the following command:

    python manage.py check_scripts --mark-all-applied


### How to ensure proper scripts execution order?

If there are some scripts that must be executed in a specific order - one after another,
you may decorate their `handle()` or `handle_noargs()` with `@required_preceding_script`
decorator.

Following sample script would require execution of two preceding scripts:

```python
from your_app.management.commands import admin_script_1, admin_script_2
from scripts_tracker.dependency_tracker import required_preceding_script
    
class Command(BaseCommand):
    help = 'This is some help'
    
    @required_preceding_script(admin_script_1, admin_script_2)
    def handle(self, **options):
        # (...)
```

Note that:

* The `@required_preceding_script` decorator arguments must be python modules and they must be 'trackable scripts'
(not ignored and `@tracked_script` decorated)
* The dependency tracker checks if required preceding scripts were executed and if not a warning is displayed,
yet user may ignore it and script can be executed without executing preceding scripts


Configuration
-------------

There are few tracker constants that you might want to override in your project's `settings.py` file:

* `COMMANDS_DIRS` - a list of directories that will be scanned for django-admin command scripts (default: `[]`)

* `IGNORED_FILES` - a tuple of files that will be ignored during scanning directories (default: `('__init__.py',)`)

* `IGNORED_CMD_PREFIXES` - a tuple of file name prefixes to be ignored (default: `tuple()`)

* `CHECK_SCRIPT_GIT_STATUS` - a flag, when set to `True` - scripts with uncommited changes **won't** get marked as 
applied ones after their execution (default: `False`)

* `SCRIPTS_TRACKER` - a dict, with optional configurations. Currently only one key is in use: `auto_run`, which
indicates whether all unapplied scripts should be automatically run after performing migrations
(default: `{ 'auto_run': False }`)


Python and Django compatibility
-------------------------------

The app has been written to support Python 2.7.x and Python 3.x<br>
It has been successfully tested on Python 2.7.17 and 3.6.2

The app has been written to support Django 1.7+<br>
It has been successfully tested on Django 1.7.11, 1.8.18 and 1.11.11


Author
------

Krzysztof Falcman