"""
FileBotPy - A Python implementation of FileBot's renaming feature.

Reverse engineered from FileBot 5.2.1 to provide media detection,
matching, and renaming with Jellyfin-compatible naming formats.
"""

__version__ = "0.1.0"

from filebotpy.media.detector import AutoDetection
from filebotpy.media.release_info import ReleaseInfo
from filebotpy.similarity.episode import SeasonEpisodeMatcher
from filebotpy.similarity.series import SeriesNameMatcher
from filebotpy.naming.engine import ExpressionFormat
from filebotpy.naming.templates import NamingTemplates
from filebotpy.rename.action import RenameAction, MoveAction, CopyAction, HardlinkAction, SymlinkAction
from filebotpy.rename.conflict import ConflictAction, ConflictResolver
from filebotpy.gui import launch_gui

__all__ = [
    "AutoDetection",
    "ReleaseInfo",
    "SeasonEpisodeMatcher",
    "SeriesNameMatcher",
    "ExpressionFormat",
    "NamingTemplates",
    "RenameAction",
    "MoveAction",
    "CopyAction",
    "HardlinkAction",
    "SymlinkAction",
    "ConflictAction",
    "ConflictResolver",
]
