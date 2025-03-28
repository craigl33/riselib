"""Generel utility functions which could be used anywhere."""

import os
from riselib.utils.logger import Logger

log = Logger(__name__)

def catch_errors(func: callable) -> callable:
    """Catch errors decorator.

    Decorator to catch errors in functions and log them instead of crashing the program. This decorator can only be
    used on functions that have a configuration object as the first argument. This is because the decorator needs to
    access the configuration object (e.g. create output and create plot functions) to check if error catching is
    enabled in the configuration file.
    """

    def _catch_errors_wrapper(*args: list, **kwargs: dict) -> callable:
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
