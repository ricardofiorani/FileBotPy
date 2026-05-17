"""
ClutterFileFilter - Filters out clutter files that should not be processed.

Based on FileBot's ClutterFileFilter and patterns from ReleaseInfo.properties.
"""

import re
from pathlib import Path
from typing import List, Set


class ClutterFileFilter:
    """Filters out files and folders that should be excluded from processing."""

    # Clutter file patterns from ReleaseInfo.properties
    CLUTTER_FILE_PATTERN = re.compile(
        r'[\-](?:behindthescenes|deleted|featurette|interview|scene|short|trailer|other)[.][^.]+$',
        re.IGNORECASE
    )

    CLUTTER_FOLDER_PATTERN = re.compile(
        r'^(?:Extras|Trailers|Featurettes|Interviews|Scenes|Shorts|'
        r'Behind\.the\.Scenes|Deleted\.Scenes)$',
        re.IGNORECASE
    )

    CLUTTER_EXCLUDES_PATTERN = re.compile(
        r'[!\-\(\[]](?:Sample|Trailer)|'
        r'(?:Sample|Trailer)[\-\)\]]|'
        r'(?:^|[.\-])(?:(?-i:s|t)|sample|trailer|deleted|featurette|'
        r'interview|scene|other|behindthescene)$|'
        r'(?:NCED|NCOP|(?-i:OP|ED)\d{0,2}(?!\w))|'
        r'(?:Extras|Trailers|Featurettes|Interviews|Scenes)$|'
        r'Behind\.the\.Scenes|Deleted\.and\.Extended\.Scenes|'
        r'Deleted\.Scenes',
        re.IGNORECASE
    )

    # Clutter file types to exclude
    CLUTTER_TYPES_PATTERN = re.compile(
        r'[.](?:jpg|jpeg|png|gif|ico|nfo|info|xml|htm|html|log|m3u|'
        r'cue|ffp|srt|sub|idx|smi|sup|md5|sfv|txt|rtf|url|website|'
        r'db|dna|log|tgmd|json|data|ignore|srv|srr|nzb|vbs|ini|vsmeta|'
        r'DS_Store)$',
        re.IGNORECASE
    )

    # Disk folder patterns (BDMV, VIDEO_TS, etc.)
    DISK_FOLDER_PATTERN = re.compile(
        r'^(?:BDMV|AVCHD|HVDVD_TS|VIDEO_TS|AUDIO_TS|VCD|'
        r'MovieObject\.bdmv|VIDEO_TS\.VOB|VTS_[0-9]+_[0-9]+\.VOB)$',
        re.IGNORECASE
    )

    # System files to exclude
    SYSTEM_FILES_PATTERN = re.compile(
        r'^[@.][a-z]+|#recycle|bin|initrd|opt|sbin|var|lib|proc|sys|'
        r'etc|lost\.found|root|tmp|mnt|run|usr|System\.Volume\.Information$',
        re.IGNORECASE
    )

    def is_clutter_file(self, path: Path) -> bool:
        """Check if a file should be excluded as clutter."""
        name = path.name

        # Check clutter file pattern
        if self.CLUTTER_FILE_PATTERN.search(name):
            return True

        # Check clutter excludes pattern
        if self.CLUTTER_EXCLUDES_PATTERN.search(name):
            return True

        # Check clutter file types (non-media files)
        if self.CLUTTER_TYPES_PATTERN.search(name):
            return True

        # Check system files
        if self.SYSTEM_FILES_PATTERN.search(name):
            return True

        return False

    def is_clutter_folder(self, path: Path) -> bool:
        """Check if a folder should be excluded as clutter."""
        name = path.name

        # Check clutter folder pattern
        if self.CLUTTER_FOLDER_PATTERN.search(name):
            return True

        # Check disk folder pattern
        if self.DISK_FOLDER_PATTERN.search(name):
            return True

        # Check system folders
        if self.SYSTEM_FILES_PATTERN.search(name):
            return True

        return False

    def is_media_file(self, path: Path) -> bool:
        """Check if a file is a media file (not clutter)."""
        if path.is_file() and not self.is_clutter_file(path):
            return path.suffix.lower() in {
                '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm',
                '.m4v', '.mpg', '.mpeg', '.m2ts', '.ts', '.vob', '.iso',
                '.ogv', '.3gp', '.3g2', '.f4v', '.divx', '.xvid',
            }
        return False

    def filter_files(self, paths: List[Path]) -> List[Path]:
        """Filter out clutter files and folders from a list of paths."""
        result = []
        for path in paths:
            if path.is_dir():
                if not self.is_clutter_folder(path):
                    result.append(path)
            elif path.is_file():
                if not self.is_clutter_file(path):
                    result.append(path)
        return result

    def collect_media_files(self, directory: Path) -> List[Path]:
        """Collect all media files from a directory, excluding clutter."""
        media_files = []
        if not directory.is_dir():
            return media_files

        for item in directory.iterdir():
            if item.is_file() and self.is_media_file(item):
                media_files.append(item)
            elif item.is_dir() and not self.is_clutter_folder(item):
                # Recursively collect from subdirectories
                media_files.extend(self.collect_media_files(item))

        return sorted(media_files)
