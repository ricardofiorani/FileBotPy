"""
ConflictResolver - Handles file naming conflicts during rename operations.

Based on FileBot's StandardConflictAction class.
"""

import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


class ConflictAction(str, Enum):
    """How to handle naming conflicts."""
    AUTO_RENAME = "auto"      # Append (1), (2), etc.
    OVERWRITE = "overwrite"   # Overwrite existing file
    SKIP = "skip"            # Skip the file
    FAIL = "fail"            # Raise error


@dataclass
class ConflictInfo:
    """Information about a naming conflict."""
    source: Path
    destination: Path
    existing: Path
    action: ConflictAction = ConflictAction.AUTO_RENAME


class ConflictResolver:
    """Resolves naming conflicts during rename operations."""

    # Pattern for auto-renamed files: filename (1).ext
    AUTO_RENAME_PATTERN = re.compile(r'^(.+?)(?:\s*\((\d+)\))?(\.[^.]+)?$')

    def __init__(self, action: ConflictAction = ConflictAction.AUTO_RENAME):
        """Initialize with default conflict action."""
        self.default_action = action

    def resolve(self, source: Path, destination: Path) -> Path:
        """Resolve potential conflict and return the final destination path.

        If there's no conflict, returns the original destination.
        If there's a conflict, applies the configured action.
        """
        if not destination.exists():
            return destination

        if self.default_action == ConflictAction.AUTO_RENAME:
            return self._auto_rename(destination)
        elif self.default_action == ConflictAction.OVERWRITE:
            return destination
        elif self.default_action == ConflictAction.SKIP:
            return None
        elif self.default_action == ConflictAction.FAIL:
            raise FileExistsError(
                f"Destination already exists: {destination}. "
                f"Conflict action is set to fail."
            )

        return destination

    def _auto_rename(self, path: Path) -> Path:
        """Generate a new path by appending (1), (2), etc."""
        if not path.exists():
            return path

        # Parse the filename
        stem = path.stem
        suffix = path.suffix
        parent = path.parent

        # Check if already has auto-rename suffix
        match = self.AUTO_RENAME_PATTERN.match(stem)
        if match:
            base_name = match.group(1)
            current_num = int(match.group(2) or 0)
            file_suffix = match.group(3) or ''
        else:
            base_name = stem
            current_num = 0
            file_suffix = suffix

        # Find next available number
        counter = current_num + 1
        while True:
            new_name = f"{base_name} ({counter}){file_suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1

            # Safety limit
            if counter > 1000:
                raise RuntimeError(
                    f"Could not find available filename for {path}"
                )

    def check_conflict(self, source: Path, destination: Path) -> Optional[ConflictInfo]:
        """Check if there's a conflict and return ConflictInfo if so."""
        if destination.exists():
            return ConflictInfo(
                source=source,
                destination=destination,
                existing=destination,
                action=self.default_action,
            )
        return None

    def get_final_path(self, source: Path, destination: Path) -> Path:
        """Get the final destination path after conflict resolution."""
        conflict = self.check_conflict(source, destination)
        if conflict is None:
            return destination

        return self.resolve(source, destination)
