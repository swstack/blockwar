import pkg_resources
import os

THIS_DIR = os.path.abspath(os.path.dirname(__file__))

try:
    from blockwar.__genversion__ import __version__
    running_in_egg = True
except ImportError:
    running_in_egg = False


#-------------------------------------------------------------------------------
# Paths
#-------------------------------------------------------------------------------
def project_root():
    if running_in_egg:
        return os.path.abspath(os.path.join(THIS_DIR, "..", ".."))
    else:
        return os.path.abspath(os.path.join(THIS_DIR, "..", "..", ".."))


def env():
    if running_in_egg:
        return os.path.join(os.path.expanduser("~"), ".env")
    else:
        return os.path.join(project_root(), ".env")


def resources():
    return os.path.abspath(os.path.join(THIS_DIR, '..', 'resources'))


def log_file():
    return os.path.join(env(), 'log.txt')


def settings_path():
    return os.path.join(env(), "settings.json")


def project_tmp():
    return os.path.join(env(), "tmp")


def build_dir():
    return os.path.join(project_root(), 'build', 'blockwar')


#-------------------------------------------------------------------------------
# Helpers
#-------------------------------------------------------------------------------
def init_dirs(path):
    """Helper function to recursively make the directories in `path` if they don't exist

    :param path: Any filesystem path (directories or files)
    """
    if not os.path.exists(path):  # path doesn't exist, safe to proceed
        # make sure the path doesn't look file-like
        end_of_path = os.path.split(path)[-1]
        if ("." in end_of_path) and (not end_of_path.startswith(".")):
            dirs, filename = os.path.split(path)
            if not os.path.exists(dirs):
                os.makedirs(dirs)
        else:
            os.makedirs(path)
