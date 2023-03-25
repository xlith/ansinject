"""
Top level module for ansinject.
"""
# ansinject/__init__.py
from __future__ import annotations

__app_name__ = 'ansinject'
__version__ = '0.2.0'

(
    SUCCESS,
    DIR_ERROR,
    FILE_ERROR,
    DEPENDENCY_ERROR,
    APK_DECODE_ERROR,
    APK_BUILD_ERROR,
) = range(6)

ERRORS = {
    DIR_ERROR: 'directory error',
    FILE_ERROR: 'file error',
    DEPENDENCY_ERROR: 'dependency error',
    APK_DECODE_ERROR: 'APK decode error',
    APK_BUILD_ERROR: 'APK build error',
}
