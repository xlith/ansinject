from __future__ import annotations

import os
import re
import shutil
import subprocess
from contextlib import nullcontext
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import ContextManager

import typer
from rich import print
from rich.prompt import Confirm
from rich.status import Status

from ansinject import APK_BUILD_ERROR
from ansinject import APK_DECODE_ERROR
from ansinject import DIR_ERROR
from ansinject.config import config


def _check_temp_dir(temp_dir: Path):
    """Check the temp directory."""

    with os.scandir(temp_dir) as it:
        if any(it):
            if Confirm.ask(
                prompt=f'[bold red]Temp directory: {temp_dir} is not empty. Clear it?[/bold red]',
            ):
                shutil.rmtree(temp_dir)
                os.mkdir(temp_dir)
                print(':white_check_mark: Clear temp directory')
            else:
                print(':x: Temp directory is not empty')
                raise typer.Exit(DIR_ERROR)
        else:
            print(':white_check_mark: Temp directory is empty')


def inject_apk(input_apk: Path, output_apk: Path, temp_dir: Path):
    """Inject an APK."""

    context: TemporaryDirectory | ContextManager[None]

    if not temp_dir:
        context = TemporaryDirectory()
        temp_dir = Path(context.name)
    else:
        context = nullcontext()

    with context:
        _check_temp_dir(temp_dir)
        decode_apk(input_apk=input_apk, output_dir=temp_dir / 'decoded-apk')
        inject_config_file(temp_dir / 'decoded-apk')
        print(':white_check_mark: Inject network_security_config.xml')
        build_apk(
            input_dir=temp_dir / 'decoded-apk',
            output_apk=temp_dir / 'unsigned.apk',
        )
        generate_keystore(keystore_path=temp_dir / 'key.keystore')
        sign_apk(
            input_apk=temp_dir / 'unsigned.apk',
            output_apk=temp_dir / 'signed-unaligned.apk',
            keystore_path=temp_dir / 'key.keystore',
        )
        align_apk(
            input_apk=temp_dir / 'signed-unaligned.apk',
            output_apk=output_apk,
        )


def decode_apk(input_apk: Path, output_dir: Path):
    """Decode an APK."""

    with Status('Decoding APK', spinner='aesthetic'):
        try:
            subprocess.run(
                [
                    config['tools']['apktool'],
                    'd',
                    input_apk,
                    '-o',
                    output_dir,
                ],
                check=True,
                text=True,
                capture_output=True,
            )
            print(':white_check_mark: Decode APK')
        except subprocess.CalledProcessError as error:
            print('Error decoding APK')
            print(error.stderr)
            typer.Exit(APK_DECODE_ERROR)


def inject_config_file(apk_dir: Path):
    shutil.copyfile(
        Path('ansinject', 'network_security_config.xml'),
        apk_dir / 'res' / 'xml' / 'network_security_config.xml',
    )


def build_apk(input_dir: Path, output_apk: Path):
    """Build an APK."""

    with Status('Building APK', spinner='aesthetic') as status:
        output = subprocess.run(
            [
                config['tools']['apktool'],
                '--use-aapt2',
                'b',
                input_dir,
                '-o',
                output_apk,
            ],
            text=True,
            capture_output=True,
        )
        if output.returncode != 0:
            status.console.print('Expected error')
            matches = re.findall(
                r'W:\s((?:/\S+)+\.xml).+error:\sresource\s(.+)\sis\sprivate',
                output.stderr,
            )

            for file_location, resource in matches:
                print(f'Fixing {file_location} resource {resource}')
                with open(file_location, 'r+t') as file:
                    text: str = file.read()
                    modified_text: str = text.replace(resource, f'*{resource}')
                    file.seek(0)
                    file.truncate()
                    file.write(modified_text)
        try:
            subprocess.run(
                [
                    config['tools']['apktool'],
                    '--use-aapt2',
                    'b',
                    input_dir,
                    '-o',
                    output_apk,
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            print(':white_check_mark: Build APK')
        except subprocess.CalledProcessError as error:
            print('Error building APK')
            print(error.stderr)
            typer.Exit(APK_BUILD_ERROR)


def generate_keystore(keystore_path: Path):
    """Generate a keystore."""
    with Status('Generating keystore', spinner='aesthetic'):
        subprocess.run(
            [
                config['tools']['keytool'],
                '-genkey',
                '-v',
                '-keystore',
                keystore_path,
                '-alias',
                'sign',
                '-keyalg',
                'RSA',
                '-keysize',
                '2048',
                '-validity',
                '10000',
                '-storepass',
                'password',
                '-dname',
                'CN=, O=, C=',
            ],
            text=True,
            check=True,
            capture_output=True,
        )
        print(':white_check_mark: Generate keystore')


def sign_apk(input_apk: Path, output_apk: Path, keystore_path: Path):
    """Sign an APK."""
    with Status('Signing the APK', spinner='aesthetic'):
        subprocess.run(
            [
                config['tools']['jarsigner'],
                '-verbose',
                '-sigalg',
                'SHA1withRSA',
                '-digestalg',
                'SHA1',
                '-keystore',
                keystore_path,
                '-storepass',
                'password',
                '-signedjar',
                output_apk,
                input_apk,
                'sign',
            ],
            text=True,
            check=True,
            capture_output=True,
        )
        print(':white_check_mark: Sign APK')


def align_apk(input_apk: Path, output_apk: Path):
    """Align an APK."""
    with Status('Aligning the APK', spinner='aesthetic'):
        subprocess.run(
            [
                config['tools']['zipalign'],
                '-p',
                '-f',
                '-v',
                '4',
                input_apk,
                output_apk,
            ],
            text=True,
            check=True,
            capture_output=True,
        )
        print(':white_check_mark: Align APK')
