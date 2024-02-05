# riselib

The riselib package is a collection of modules and functions which can be used in any project. The package is not intended to be run directly, but rather imported into other projects.

## Installation
There are a few different ways to install the package/ use code from it. It depends on your needs and skills/ comfort.

### Only use functions
If you just wanna use functions from the package, you can install the package using pip:
```bash
pip install git+https://gitlab.iea.org/iea/ems/rise/riselib --no-dependencies
```

This will not install the dependencies, since this should be done via conda to not mix up conda and pip. Just run the code and wait for `ModuleNotFoundError` to appear. Then install the missing package using conda. Or run:
```bash
conda install -c conda-forge pandas pyodbc sqlalchemy
```

> Note: When conda is not used, you can install all the dependencies automatically by just skipping the `--no-dependencies` flag.

### Also develop the package

If you also want to develop the package, e.g. change and add code, you can clone the repository next to your other projects.
```bash
git clone https://gitlab.iea.org/iea/ems/rise/riselib
```
Which could lead to a folder structure like this:
```
U:\code\plexos-model-setup
U:\code\riselib
```

If you now wanna use riselib inside the plexos-model-setup project, you can install the package in editable mode:
```bash
pip install -e U:\code\riselib
```

This will create a link to the riselib package in the site-packages folder of your python environment. This way, you can change the code in the riselib folder and the changes will be directly available in the plexos-model-setup project. In most IDEs, you can also directly add a second content root to your project, so that you can directly see the code in the IDE. In PyCharm, this can be done via: Settings/ Project Structure/ Add Content Root. This way you can work on both projects at the same time, keeping the git repositories and code separated.


## Usage

Just import the functions you need in your code, like you would do with any other package:

```python
from riselib import ...
```
