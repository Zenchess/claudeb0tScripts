"""Custom exceptions for hackmud memory scanner"""


class ScannerError(Exception):
    """Base exception for scanner errors"""
    pass


class GameNotFoundError(ScannerError):
    """Raised when hackmud process is not found"""
    pass


class ConfigError(ScannerError):
    """Raised when configuration is invalid or missing"""
    pass


class MemoryReadError(ScannerError):
    """Raised when memory reading fails"""
    pass


class WindowNotFoundError(ScannerError):
    """Raised when requested window is not found"""
    pass


class OffsetsNotFoundError(ScannerError):
    """Raised when offsets are not available"""
    pass
