from __future__ import annotations


class FormatError(Exception):
    """Base class for format-related errors"""


class FormatUnknown(FormatError):
    """Raised when a format identifier is unknown"""
