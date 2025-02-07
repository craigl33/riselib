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

### 1. Simple Installation (Functions Only)

If you just want to use the package functions, install via pip:
```bash
pip install git+https://gitlab.iea.org/iea/ems/rise/riselib --no-dependencies
```
