# example_device

Concrete server and feature implementation for an example device.

## Development Environment Setup

- Install Git
- Install Python
- `python -m venv venv`
- `source venv/bin/activate`
- `pip install --upgrade pip`
- `pip install . --group dev`
- `pre-commit install`

**Recommended**

The project is set up for the following tools to help with good development practices. These are usually something you can set up in your IDE, and VSCode/VSCodium has extensions for them:

- Black and isort for Python formatting
- Flake8 for Python linting
- Docstrfmt for reStructuredText formatting
- Mypy for type checking (please use type hints)

## Project Automation

### Tox

This project is set up with project automation through [tox](https://tox.wiki/en/latest/). Unit tests can be run by simply invoking:

```bash
tox
```

or other actions can be run with:

```bash
tox run -e <action>
```

Multiple actions can be run in sequence with commas:

```bash
tox run -e clean,build
```

A list of available actions can be found by running `tox list` after [Development Environment Setup](#development-environment-setup).

### Pre-Commit

To help with code checking, this project is set up with [pre-commit](https://pre-commit.com/). Once installed for the repo (`pre-commit install` in [Development Environment Setup](#development-environment-setup)), a series of tests and checks will be automatically run through git pre-commit hooks before the commit is allowed to go through. Some issues are fixed automatically, some require manual intervention. Once everything has been fixed, commit the new changes and try again until all of the checks are passing!
