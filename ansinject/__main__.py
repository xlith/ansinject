"""ansinject entry point script."""
# rptodo/__main__.py
from __future__ import annotations

from ansinject import __app_name__
from ansinject import cli


def main() -> None:
    cli.app(prog_name=__app_name__)


if __name__ == '__main__':
    main()
