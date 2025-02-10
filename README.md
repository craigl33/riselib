# riselib

The riselib package is a collection of utility modules and functions for data analysis, logging, and plotting. It provides reusable components that can be integrated into any Python project.

## Features

- **Advanced Logging**: Custom logger with:
  - Multiple output handlers (console, file, email)
  - Configurable log levels 
  - Time tracking
  - Easy enabling/disabling of logging
  - SMTP support for email notifications

- **Plotting Utilities**:
  - IEA style formatting for matplotlib plots
  - Custom grid and axis formatting
  - Geographic coordinate handling

- **Error Handling**:
  - Decorator-based error catching
  - Configurable error handling behavior
## Installation

There are several ways to install and use the package depending on your needs:

### 1. Simple Installation (functions only)

If you just want to use the package functions, install via pip using SSH:
```bash
pip install git+ssh://git@gitlab.iea.org/iea/ems/rise/riselib --no-dependencies
```

Or if using HTTPS:
```bash
pip install git+https://gitlab.iea.org/iea/ems/rise/riselib --no-dependencies
```

### 2. Install for development

If you also want to develop the package, e.g. change and add code, you can clone the repository next to your other projects.
```bash
git clone https://gitlab.iea.org/iea/ems/rise/riselib
```
Which could lead to a folder structure like this, for e.g.:
```
git_folder\plexos-model-setup
git_folder\riselib
etc
```

If you now want use riselib inside the plexos-model-setup project or any other, you can install the package in editable mode:
```bash
pip install -e ..\riselib --no-dependencies
pip install -r ..\riselib\requirements.txt
```

This will create a link to the riselib package in the site-packages folder of your python environment. This way, you can change the code in the riselib folder and the changes will be directly available in the plexos-model-setup project. In most IDEs, you can also directly add a second content root to your project, so that you can directly see the code in the IDE. In PyCharm, this can be done via: Settings/ Project Structure/ Add Content Root. This way you can work on both projects at the same time, keeping the git repositories and code separated.


## Usage

Just import the functions you need in your code, like you would do with any other package:

```python
from riselib import ...
```
```
