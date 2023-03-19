'''This module provides the ansinject config functionality.'''
# rptodo/config.py
from __future__ import annotations

import configparser
import os
import subprocess
from inspect import get_annotations
from io import TextIOWrapper
from pathlib import Path
from typing import ItemsView
from typing import Literal
from typing import Mapping
from typing import TypeAlias
from typing import TypedDict
from typing import Union
from typing import cast

import typer
from rich.console import Console
from rich.status import Status
from rich.table import Table

from ansinject import DEPENDENCY_ERROR
from ansinject import FILE_ERROR
from ansinject import __app_name__

CONFIG_DIR_PATH = Path(typer.get_app_dir(__app_name__))
CONFIG_FILE_PATH = CONFIG_DIR_PATH / 'config.ini'
console = Console()

ToolsKeys: TypeAlias = Literal[
    'adb',
    'zipalign',
    'apktool',
    'jarsigner',
    'keytool',
]


class Tools(TypedDict, total=False):
    '''The tools dictionary.'''

    adb: Path
    zipalign: Path
    apktool: Path
    jarsigner: Path
    keytool: Path


GeneralKeys: TypeAlias = Literal['apk', 'android_home']


class General(TypedDict, total=False):
    '''The general dictionary.'''

    apk: Path
    android_home: Path


ConfigKeys: TypeAlias = Literal['general', 'tools']

ConfigView: TypeAlias = ItemsView[str, Union[Tools, General]]


class Config(TypedDict):
    '''The configuration dictionary.'''

    general: General
    tools: Tools


config: Config = {
    'general': {},
    'tools': {},
}


def _get_dependency_path_using_which(dependency: str) -> Path | None:
    try:
        cmd_str = subprocess.run(
            ['which', dependency],
            check=True,
            text=True,
            capture_output=True,
        )
        stdout = cmd_str.stdout[:-1]
        return Path(stdout)
    except subprocess.CalledProcessError:
        return None


def _get_dependency_path_using_find(dependency: str) -> Path | None:
    try:
        cmd_str = subprocess.run(
            ['find', config['general']['android_home'], '-name', dependency],
            check=True,
            text=True,
            capture_output=True,
        )
        stdout = cmd_str.stdout[:-1].split('\n', 1)[0]

        return Path(stdout)
    except subprocess.CalledProcessError:
        return None


def _find_dependency(dependency: str) -> Path:
    '''Find the dependency.'''

    if path := _get_dependency_path_using_which(dependency):
        return path

    if path := _get_dependency_path_using_find(dependency):
        return path

    console.print(f'Could not find [b]{dependency}[/b]')
    raise typer.Exit(DEPENDENCY_ERROR)


def _init_initial_config() -> None:
    '''Initialize the initial configuration.'''

    if (android_home := os.environ.get('ANDROID_HOME')) is None:
        console.print('b]ANDROID_HOME[/b] environment variable not set')
        raise typer.Exit(DEPENDENCY_ERROR)

    config['general']['android_home'] = Path(android_home)


def _init_dependency_config() -> None:
    '''Initialize the dependency configuration.'''

    for key in get_annotations(Tools):
        config['tools'][key] = _find_dependency(key)  # type: ignore


def _read_config_file(file: TextIOWrapper):
    '''Read the config file.'''

    file.seek(0)
    config_parser = configparser.ConfigParser()
    config_parser.read_file(file)
    return config_parser


def _write_config_file(
    config_parser: configparser.ConfigParser,
    file: TextIOWrapper,
):
    '''Write the config file.'''
    config_parser.write(file)


def _config_commit(file: TextIOWrapper) -> None:
    '''Commit the configuration to the config file.'''

    config_parser = configparser.ConfigParser()

    for section, section_dict in config.items():
        config_parser[section] = cast(Mapping[str, str], section_dict)
    _write_config_file(config_parser, file)


def _config_load(config_parser: configparser.ConfigParser) -> None:
    '''Load the configuration from the config file.'''

    for section in config.keys():
        try:
            config[section] = config_parser[section]  # type: ignore
        except KeyError:
            pass


def config_reset() -> None:
    '''Reset the configuration.'''

    CONFIG_FILE_PATH.unlink(missing_ok=True)


def _print_config(config: Config) -> None:
    '''Print the configuration.'''

    for key, value in cast(ConfigView, config.items()):
        table = Table(title=key)
        table.add_column('key', justify='right', style='cyan', no_wrap=True)
        table.add_column('value', style='magenta')
        for key, v in value.items():
            table.add_row(key, str(v))
        console.print(table)


def config_show() -> None:
    '''Show the configuration.'''

    try:
        with CONFIG_FILE_PATH.open('r') as file:
            config_parser = _read_config_file(file)
    except FileNotFoundError:
        console.print(
            'Configuration file not found. Please run [b]ansinject config init[/b]',
        )
        raise typer.Exit(FILE_ERROR)

    _config_load(config_parser)
    _print_config(config)


def init_app() -> None:
    '''Initialize the application.'''

    with Status('Initializing the application...', spinner='aesthetic'):
        with CONFIG_FILE_PATH.open('a+') as file:
            config_parser = _read_config_file(file)
            try:
                config_parser.get('general', 'android_home')
            except (configparser.NoSectionError, configparser.NoOptionError):
                _init_initial_config()
                _init_dependency_config()
                _config_commit(file)
                return

            _config_load(config_parser)
