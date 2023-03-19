"""This module provides the andinject CLI."""
# ansinject/cli.py
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional

import typer

from ansinject import __app_name__
from ansinject import __version__
from ansinject import ansinject
from ansinject import config

app = typer.Typer()


class ConfigChoice(Enum):
    init = 'init'
    reset = 'reset'
    show = 'show'


@app.command(name='config')
def conf(
    config_choice: ConfigChoice = typer.Argument(
        'show',
        help='The config choice.',
    ),
) -> int:
    """Configure the application."""
    match config_choice:
        case ConfigChoice.init:
            config.config_reset()
            config.init_app()
        case ConfigChoice.reset:
            config.config_reset()
        case ConfigChoice.show:
            config.config_show()

    return 0


@app.command()
def inject(
    input_apk: Path = typer.Argument(
        ...,
        help='The input APK to inject.',
        exists=True,
        readable=True,
        resolve_path=True,
    ),
    output_apk: Path = typer.Argument(
        ...,
        help='The output APK.',
        exists=False,
        writable=True,
        resolve_path=True,
    ),
    temp_dir: Path = typer.Option(
        None,
        '--temp-dir',
        '-t',
        help='The temporary directory. If spesified middlewares will be kept in this directory. If not specified, the system temporary directory will be used and they will be deleted at the end of process.',
        exists=False,
        writable=True,
        resolve_path=True,
    ),
) -> None:
    """Inject an APK."""
    config.init_app()
    ansinject.inject_apk(
        input_apk=input_apk,
        output_apk=output_apk,
        temp_dir=temp_dir,
    )


def _version_callback(value: bool) -> None:
    if value:
        print(f'{__app_name__} v{__version__}')
        raise typer.Exit()


@app.callback(
    no_args_is_help=True,
)
def main(
    version: Optional[bool] = typer.Option(
        None,
        '--version',
        '-v',
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """A tool to inject an APK."""
