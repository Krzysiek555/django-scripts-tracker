import os

from django.conf import settings

# ==========================================================
# Directories that will be used to search for scripts
# ==========================================================
COMMANDS_DIRS = getattr(settings, 'COMMANDS_DIRS', [])

# ==========================================================
# All files starting with these prefixes will be ignored (must be a tuple()!)
# ==========================================================
IGNORED_CMD_PREFIXES = getattr(settings, 'IGNORED_CMD_PREFIXES', tuple())

# ==========================================================
# Files to ignore (must be a tuple()!)
# ==========================================================
IGNORED_FILES = getattr(settings, 'IGNORED_FILES', ('__init__.py',))

# ==========================================================
# When set to True - scripts with uncommited changes
# WON'T get marked as applied ones after their execution
# ==========================================================
CHECK_SCRIPT_GIT_STATUS = False

# ==========================================================
# Terminal colors
# ==========================================================
_LINUX_TERM_COLORS = {
    'GREEN': '\033[0;32m',
    'LIGHT_CYAN': '\033[1;36m',
    'NC': '\033[0m'
}

_NO_TERM_COLORS = {k: '' for k, v in _LINUX_TERM_COLORS.items()}  # empty color codes

TERM_COLORS = _LINUX_TERM_COLORS if os.name == 'posix' else _NO_TERM_COLORS
