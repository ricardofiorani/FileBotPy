"""
AutoDetection - Detects media type from filename/path.

Based on FileBot's AutoDetection class and patterns.
"""

import re
from enum import Enum
from pathlib import Path
from typing import Optional

from filebotpy.media.release_info import ReleaseInfo, ReleaseInfoParser


class MediaType(str, Enum):
    """Media type enumeration."""
    TV = "tv"
    MOVIE = "movie"
    ANIME = "anime"
    MUSIC = "music"
    UNKNOWN = "unknown"


class AutoDetection:
    """Automatically detects media type from filename."""

    # TV show patterns
    TV_PATTERNS = [
        # S01E01, s01e01, S01E01E02
        re.compile(r'[Ss](\d{1,4})[Ee](\d{1,4})(?:[Ee](\d{1,4}))*', re.IGNORECASE),
        # 1x01, 01x01
        re.compile(r'(\d{1,4})[xX](\d{1,4})(?:[xX](\d{1,4}))*', re.IGNORECASE),
        # Season 1 Episode 1
        re.compile(r'[Ss]eason\s+(\d{1,4})\s*[Ee]pisode\s+(\d{1,4})', re.IGNORECASE),
        # Season 1
        re.compile(r'[Ss]eason\s+(\d{1,4})', re.IGNORECASE),
        # E01, e01 (episode only, need series folder context)
        re.compile(r'[Ee](\d{1,4})(?:\s*[-]\s*E(\d{1,4}))*', re.IGNORECASE),
        # Absolute episode numbers (anime style)
        re.compile(r'(?:^|[\s._\-\(\[])(\d{2,3})(?:v\d)?[\s._\-\)\]]', re.IGNORECASE),
    ]

    # Anime patterns (more specific than TV)
    ANIME_PATTERNS = [
        # [SubGroup] Series Name - 01 [1080p]
        re.compile(r'^\[.+\].+\s[-]\s\d{1,4}', re.IGNORECASE),
        # Series Name - 01 (absolute episode with dash)
        re.compile(r'.+\s[-]\s(\d{1,4})\s', re.IGNORECASE),
        # Ep 01, EP01
        re.compile(r'[Ee][Pp]\s*(\d{1,4})', re.IGNORECASE),
        # #01, #1
        re.compile(r'#(\d{1,4})', re.IGNORECASE),
        # Common anime indicators
        re.compile(r'\b(?:NCOP|NCED|OP|ED)\d{0,2}\b', re.IGNORECASE),
    ]

    # Movie patterns
    MOVIE_PATTERNS = [
        # Title (Year)
        re.compile(r'.+\((?:19|20)\d{2}\)'),
        # Title.Year
        re.compile(r'.+[\._](?:19|20)\d{2}[\._]'),
    ]

    # Music patterns
    MUSIC_PATTERNS = [
        # Artist - Album (Year)
        re.compile(r'.+\s[-]\s.+\s\((?:19|20)\d{2}\)'),
        # Track number patterns
        re.compile(r'\d{2,3}\s[-]\s.+'),
    ]

    # Clutter patterns from ReleaseInfo.properties
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

    # Video file extensions
    VIDEO_EXTENSIONS = {
        '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm',
        '.m4v', '.mpg', '.mpeg', '.m2ts', '.ts', '.vob', '.iso',
        '.ogv', '.3gp', '.3g2', '.f4v', '.divx', '.xvid',
    }

    # Audio file extensions
    AUDIO_EXTENSIONS = {
        '.mp3', '.flac', '.aac', '.ogg', '.wma', '.m4a',
        '.alac', '.wav', '.aiff', '.ape', '.opus',
    }

    # Subtitle extensions
    SUBTITLE_EXTENSIONS = {
        '.srt', '.ass', '.ssa', '.vtt', '.sub', '.idx', '.smi', '.sup',
    }

    @classmethod
    def is_video_file(cls, path: Path) -> bool:
        """Check if path is a video file."""
        return path.suffix.lower() in cls.VIDEO_EXTENSIONS

    @classmethod
    def is_audio_file(cls, path: Path) -> bool:
        """Check if path is an audio file."""
        return path.suffix.lower() in cls.AUDIO_EXTENSIONS

    @classmethod
    def is_subtitle_file(cls, path: Path) -> bool:
        """Check if path is a subtitle file."""
        return path.suffix.lower() in cls.SUBTITLE_EXTENSIONS

    @classmethod
    def is_clutter(cls, path: Path) -> bool:
        """Check if file/folder should be excluded as clutter."""
        name = path.name

        # Check clutter folder pattern
        if path.is_dir() and cls.CLUTTER_FOLDER_PATTERN.search(name):
            return True

        # Check clutter file pattern
        if path.is_file():
            if cls.CLUTTER_FILE_PATTERN.search(name):
                return True
            if cls.CLUTTER_EXCLUDES_PATTERN.search(name):
                return True

        return False

    @classmethod
    def detect(cls, path: Path) -> MediaType:
        """Detect media type from file path."""
        if not isinstance(path, Path):
            path = Path(path)

        # Check if it's a media file
        if cls.is_audio_file(path):
            return cls._detect_music(path)

        is_video = cls.is_video_file(path)
        is_subtitle = cls.is_subtitle_file(path)

        if not is_video and not is_subtitle:
            return MediaType.UNKNOWN

        # Check if it's clutter
        if cls.is_clutter(path):
            return MediaType.UNKNOWN

        filename = path.stem
        name = filename

        # Check anime patterns first (more specific)
        if cls._is_anime(name):
            return MediaType.ANIME

        # Check TV patterns
        if cls._is_tv(name):
            return MediaType.TV

        # Check movie patterns
        if cls._is_movie(name):
            return MediaType.MOVIE

        # Check parent folder for context
        parent = path.parent.name
        if cls._is_tv(parent):
            return MediaType.TV

        return MediaType.UNKNOWN

    @classmethod
    def _is_anime(cls, name: str) -> bool:
        """Check if filename matches anime patterns."""
        for pattern in cls.ANIME_PATTERNS:
            if pattern.search(name):
                return True
        return False

    @classmethod
    def _is_tv(cls, name: str) -> bool:
        """Check if filename matches TV show patterns."""
        # Look for S01E01 pattern
        sxe_match = re.search(r'[Ss](\d{1,4})[Ee](\d{1,4})', name)
        if sxe_match:
            return True

        # Look for 1x01 pattern (but not just numbers)
        x_match = re.search(r'(\d{1,2})[xX](\d{2,4})', name)
        if x_match:
            return True

        # Look for Season/Episode words
        if re.search(r'[Ss]eason\s+\d', name, re.IGNORECASE):
            return True

        # Look for Ep. 01 or Episode 01 pattern
        if re.search(r'[Ee][Pp]\.?\s*\d+', name):
            return True
        if re.search(r'[Ee]pisode\s+\d+', name, re.IGNORECASE):
            return True

        return False

    @classmethod
    def _is_movie(cls, name: str) -> bool:
        """Check if filename matches movie patterns."""
        # Look for (Year) pattern
        if re.search(r'\((?:19|20)\d{2}\)', name):
            return True

        # Look for .Year. pattern
        if re.search(r'[\._](?:19|20)\d{2}[\._]', name):
            return True

        return False

    @classmethod
    def _detect_music(cls, path: Path) -> MediaType:
        """Detect if audio file is music."""
        # For now, assume all audio files are music
        # Could be enhanced with ID3 tag reading
        return MediaType.MUSIC

    @classmethod
    def parse_release_info(cls, path: Path) -> ReleaseInfo:
        """Parse release info from file path."""
        if not isinstance(path, Path):
            path = Path(path)
        return ReleaseInfoParser.parse(path.name)
