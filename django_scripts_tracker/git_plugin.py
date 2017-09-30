import subprocess


def has_uncommited_changes(script_path):
    try:
        status = subprocess.check_output('git status {} --porcelain'.format(script_path), shell=True).strip()
    except subprocess.CalledProcessError:
        status = None

    return bool(status)