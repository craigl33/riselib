"""This module, 'utils.py', contains a collection of functions that are used in the other modules of the solution_file_processing package.
"""

import os

from .logger import Logger

log = Logger(__name__)
print = log.info


def catch_errors(func):
    """Decorator to catch errors in functions and log them instead of crashing the program. This decorator can only be
    used on functions that have a configuration object as the first argument. This is because the decorator needs to
    access the configuration object (e.g. create output and create plot functions) to check if error catching is
    enabled in the configuration file.
    """

    def _catch_errors_wrapper(*args, **kwargs):
        # Extract the configuration object "c" from the arguments
        c = args[0] if args else kwargs.get('c')

        if c.cfg['run']['catch_errors']:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log.exception(f'{e.__class__.__name__} in {func.__name__}:')

        else:
            return func(*args, **kwargs)

    return _catch_errors_wrapper


def get_files(root_folder, file_type, id_text, subfolder='', return_type=0):
    """Basic function to walk through folder and return all files of a certain type containing specific text in its
    name. Can return either a list of full paths or two lists odf directories and filenames separately depending on
    the argument return type =0/1
    """
    searched_files = []
    searched_file_paths = []
    searched_files_fullpath = []

    folder = os.path.join(root_folder, subfolder)

    for dirpath, subdirs, files in os.walk(folder):
        for file in files:
            if (file.endswith(file_type)) & (id_text in file):
                searched_files_fullpath.append(os.path.join(os.path.normpath(dirpath), file))
                searched_files.append(file)
                searched_file_paths.append(os.path.normpath(dirpath))

    if return_type == 0:
        return searched_files_fullpath
    else:
        return searched_file_paths, searched_files
