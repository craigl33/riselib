# riselib

The riselib package is a collection of modules and functions which can be used in any project. The package is not intended to be run directly, but rather imported into other projects.

## Installation
The package can be installed using pip straight from the github repository. 

```bash
pip install git+https://github.com/rise-iea/riselib --no-dependencies
```

When conda is used, the dependencies should not be installed automatically (which means via pip) but rather manually using conda. Otherwise, they could be installed twice, which leads to problems. 
When pip only is used, skip the `--no-dependencies` flag, and all are installed automatically.
