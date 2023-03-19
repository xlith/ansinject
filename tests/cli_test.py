# tests/cli_ansinject.py
from __future__ import annotations

from typer.testing import CliRunner

from ansinject import __app_name__
from ansinject import __version__
from ansinject import cli

runner = CliRunner()


def test_version():
    result = runner.invoke(cli.app, ['--version'])
    assert result.exit_code == 0
    assert f'{__app_name__} v{__version__}\n' in result.stdout
