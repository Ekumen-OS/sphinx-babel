# Getting started with `sphinx-babel`

`sphinx-babel` is a [`poetry`](https://python-poetry.org) Python package with [`tox`](https://tox.wiki) driven testing. The regular workflow applies.

## Clone `sphinx-babel` repository

```sh
git clone https://github.com/Ekumen-OS/sphinx-babel.git
```

## Bootstrap development virtualenv

```sh
cd sphinx-babel
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

## Run tests with `tox`

```sh
tox
```

## Install package with `poetry`

```sh
poetry install .
```
