"""Validates file operations for safety"""

from pathlib import Path
from typing import Tuple, Set


class FileValidator:
    """Validates file operations to prevent unauthorized access"""

    def __init__(self, allowed_base_path: str = "/home/jacob/hackmud",
                 protected_files: list = None,
                 protected_dirs: list = None,
                 max_file_size: int = 10_485_760):  # 10MB default

        self.allowed_base_path = Path(allowed_base_path).resolve()
        self.max_file_size = max_file_size

        self.protected_files: Set[str] = set()
        if protected_files:
            self.protected_files = {str(Path(f).name) for f in protected_files}
        else:
            self.protected_files = {
                '.env',
                'scanner_config.json',
                'mono_addresses.json',
                'chat_token.json'
            }

        self.protected_dirs: Set[str] = set()
        if protected_dirs:
            # Convert to string paths
            self.protected_dirs = {str(Path(d)) for d in protected_dirs}
        else:
            self.protected_dirs = {
                'discord_venv',
                'hackmud-bot/venv',
                'playwright_venv',
                'hackmud_activity_venv',
                '.git'
            }

    def is_safe_path(self, file_path: str) -> Tuple[bool, str]:
        """
        Check if a file path is safe to access.

        Returns:
            (is_safe, reason) tuple
        """
        try:
            # Resolve to absolute path
            path = Path(file_path).resolve()

            # Must be within allowed base path
            try:
                path.relative_to(self.allowed_base_path)
            except ValueError:
                return False, f"Path outside allowed base: {self.allowed_base_path}"

            # Check against protected files
            if path.name in self.protected_files:
                return False, f"Protected file: {path.name}"

            # Check against protected directories
            for protected_dir in self.protected_dirs:
                protected_path = self.allowed_base_path / protected_dir
                try:
                    path.relative_to(protected_path)
                    return False, f"Protected directory: {protected_dir}"
                except ValueError:
                    # Not in this protected directory, continue
                    pass

            return True, ""

        except Exception as e:
            return False, f"Error validating path: {e}"

    def validate_read(self, file_path: str) -> Tuple[bool, str]:
        """Validate file read operation"""
        safe, reason = self.is_safe_path(file_path)
        if not safe:
            return False, reason

        # Additional check: file must exist
        try:
            path = Path(file_path).resolve()
            if not path.exists():
                return False, "File does not exist"
        except Exception as e:
            return False, f"Error checking file: {e}"

        return True, ""

    def validate_write(self, file_path: str, content: str = "") -> Tuple[bool, str, bool]:
        """
        Validate file write operation.

        Returns:
            (allowed, reason, requires_approval) tuple
        """
        # Check path safety
        safe, reason = self.is_safe_path(file_path)
        if not safe:
            return False, reason, False

        # Check file size
        if content and len(content) > self.max_file_size:
            return False, f"File too large (max {self.max_file_size} bytes)", False

        # Writing to existing files requires approval
        try:
            path = Path(file_path).resolve()
            if path.exists():
                return False, "File already exists (requires approval)", True
        except Exception as e:
            return False, f"Error checking file: {e}", False

        # New files require approval as safety precaution
        return False, "File write requires approval", True

    def validate_delete(self, file_path: str) -> Tuple[bool, str]:
        """Validate file delete operation"""
        safe, reason = self.is_safe_path(file_path)
        if not safe:
            return False, reason

        # All deletes are blocked (require explicit approval)
        return False, "File deletion not allowed"

    def validate_create_dir(self, dir_path: str) -> Tuple[bool, str]:
        """Validate directory creation"""
        try:
            path = Path(dir_path).resolve()

            # Must be within allowed base path
            try:
                path.relative_to(self.allowed_base_path)
            except ValueError:
                return False, f"Directory outside allowed base: {self.allowed_base_path}"

            # Check against protected directories
            for protected_dir in self.protected_dirs:
                protected_path = self.allowed_base_path / protected_dir
                if path == protected_path or protected_path in path.parents:
                    return False, f"Cannot create in protected directory: {protected_dir}"

            return True, ""

        except Exception as e:
            return False, f"Error validating directory: {e}"

    def is_protected_file(self, file_path: str) -> bool:
        """Check if a file is in the protected list"""
        try:
            path = Path(file_path).resolve()
            return path.name in self.protected_files
        except:
            return False

    def is_protected_directory(self, dir_path: str) -> bool:
        """Check if a directory is in the protected list"""
        try:
            path = Path(dir_path).resolve()
            for protected_dir in self.protected_dirs:
                protected_path = self.allowed_base_path / protected_dir
                # Check if path is within protected directory
                path.relative_to(protected_path)
                return True
        except ValueError:
            pass
        except:
            pass
        return False
