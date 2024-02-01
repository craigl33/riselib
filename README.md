# riselib

The riselib package is a collection of modules and functions which can be used in any project. The package is not intended to be run directly, but rather imported into other projects.

## Installation

### conda environment
The package can be installed using pip straight from the github repository. But the dependencies should be installed manually using conda, to not mix up conda and pip.

Install dependencies:
```bash
conda install -c conda-forge pandas pyodbc sqlalchemy
```

Install riselib:
```bash
pip install git+https://gitlab.iea.org/iea/ems/rise/riselib --no-dependencies
```

If you install the packages after installing `riselib`, you might have to reinstall it.

### virtualenv (pip only)
When conda is not used, you can install all the dependencies automatically by just skipping the `--no-dependencies` flag.
