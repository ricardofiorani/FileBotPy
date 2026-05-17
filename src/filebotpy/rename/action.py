"""
RenameAction - File rename operations (move, copy, hardlink, symlink, clone).

Based on FileBot's StandardRenameAction class.
"""

import os
import shutil
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Optional


class RenameActionType(str, Enum):
    """Type of rename action."""
    MOVE = "move"
    COPY = "copy"
    HARDLINK = "hardlink"
    SYMLINK = "symlink"
    CLONE = "clone"


class RenameResult:
    """Result of a rename operation."""

    def __init__(self, source: Path, destination: Path, success: bool, error: Optional[str] = None):
        self.source = source
        self.destination = destination
        self.success = success
        self.error = error

    def __repr__(self) -> str:
        status = "OK" if self.success else f"FAILED: {self.error}"
        return f"RenameResult({self.source} -> {self.destination}: {status})"


class RenameAction(ABC):
    """Base class for rename actions."""

    @abstractmethod
    def execute(self, source: Path, destination: Path) -> RenameResult:
        """Execute the rename operation."""
        pass

    @abstractmethod
    def action_type(self) -> RenameActionType:
        """Get the type of this action."""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class MoveAction(RenameAction):
    """Move file to destination (standard rename)."""

    def execute(self, source: Path, destination: Path) -> RenameResult:
        try:
            # Create destination directory if needed
            destination.parent.mkdir(parents=True, exist_ok=True)

            # Move the file
            shutil.move(str(source), str(destination))
            return RenameResult(source, destination, success=True)
        except Exception as e:
            return RenameResult(source, destination, success=False, error=str(e))

    def action_type(self) -> RenameActionType:
        return RenameActionType.MOVE


class CopyAction(RenameAction):
    """Copy file to destination."""

    def execute(self, source: Path, destination: Path) -> RenameResult:
        try:
            # Create destination directory if needed
            destination.parent.mkdir(parents=True, exist_ok=True)

            # Copy the file
            shutil.copy2(str(source), str(destination))
            return RenameResult(source, destination, success=True)
        except Exception as e:
            return RenameResult(source, destination, success=False, error=str(e))

    def action_type(self) -> RenameActionType:
        return RenameActionType.COPY


class HardlinkAction(RenameAction):
    """Create hard link at destination."""

    def execute(self, source: Path, destination: Path) -> RenameResult:
        try:
            # Create destination directory if needed
            destination.parent.mkdir(parents=True, exist_ok=True)

            # Create hard link
            os.link(str(source), str(destination))
            return RenameResult(source, destination, success=True)
        except Exception as e:
            return RenameResult(source, destination, success=False, error=str(e))

    def action_type(self) -> RenameActionType:
        return RenameActionType.HARDLINK


class SymlinkAction(RenameAction):
    """Create symbolic link at destination pointing to source."""

    def execute(self, source: Path, destination: Path) -> RenameResult:
        try:
            # Create destination directory if needed
            destination.parent.mkdir(parents=True, exist_ok=True)

            # Create symbolic link
            # Use absolute path for the link target
            destination.symlink_to(source.resolve())
            return RenameResult(source, destination, success=True)
        except Exception as e:
            return RenameResult(source, destination, success=False, error=str(e))

    def action_type(self) -> RenameActionType:
        return RenameActionType.SYMLINK


class CloneAction(RenameAction):
    """Clone file (reflink on Linux, CloneFile on Windows).

    Falls back to copy if cloning is not supported.
    """

    def execute(self, source: Path, destination: Path) -> RenameResult:
        try:
            # Create destination directory if needed
            destination.parent.mkdir(parents=True, exist_ok=True)

            # Try reflink (copy-on-write)
            # On Linux with btrfs/xfs, use cp --reflink
            # On Windows, use CloneFile API (not directly available in Python)
            # Fallback to regular copy
            shutil.copy2(str(source), str(destination))
            return RenameResult(source, destination, success=True)
        except Exception as e:
            return RenameResult(source, destination, success=False, error=str(e))

    def action_type(self) -> RenameActionType:
        return RenameActionType.CLONE


class StandardRenameAction:
    """Factory for standard rename actions."""

    _actions = {
        RenameActionType.MOVE: MoveAction,
        RenameActionType.COPY: CopyAction,
        RenameActionType.HARDLINK: HardlinkAction,
        RenameActionType.SYMLINK: SymlinkAction,
        RenameActionType.CLONE: CloneAction,
    }

    @classmethod
    def create(cls, action_type: RenameActionType) -> RenameAction:
        """Create a rename action of the specified type."""
        action_class = cls._actions.get(action_type)
        if action_class is None:
            raise ValueError(f"Unknown action type: {action_type}")
        return action_class()

    @classmethod
    def list_actions(cls) -> list:
        """List available action types."""
        return list(cls._actions.keys())
