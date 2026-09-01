# Cronem

Cronem is an unofficial CLI for UofSC Columbia students who want to add dining-hall foods to Cronometer.

## Requirements

- Python 3.10 or newer
- A Cronometer account
- A [Kernel](https://www.kernel.sh/) API key

## Install

```console
git clone https://github.com/Tfrailey11/Cronem
cd Cronem
python -m pip install .
```

For development:

```console
python -m pip install -e '.[dev]'
pytest
```

## Use

Run `Cronem login` once. The Kernel key and username are written to a private configuration file; the Cronometer password is stored in the operating system keyring.

```console
Cronem halls
Cronem menu --hall garnet-station --meal lunch
Cronem add
Cronem add --dry-run
Cronem doctor
```

`Cronem add` supports numbered food selection, lets you override the inferred meal, previews the selection, and asks for confirmation before opening a browser session.

## Data and privacy

Generated database files and local experiments under `DataBase/` are ignored by Git and are not part of the installed application. Never commit API keys or account credentials.

This is an unofficial personal-use tool. Users are responsible for complying with Cronometer's terms of service. This project is not affiliated with Cronometer.
