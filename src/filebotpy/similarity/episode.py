"""
SeasonEpisodeMatcher - Matches season and episode patterns in filenames.

Based on FileBot's SeasonEpisodeMatcher class.
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class EpisodeMatch:
    """A single episode match from a filename."""
    season: int
    episode: int


@dataclass
class SeasonEpisodeInfo:
    """Parsed season/episode information."""
    episodes: List[EpisodeMatch]
    absolute_episode: Optional[int] = None
    is_special: bool = False
    raw_text: Optional[str] = None


class SeasonEpisodeMatcher:
    """Matches season and episode patterns in filenames."""

    # Season/Episode patterns from FileBot
    PATTERNS = [
        # S01E01, S01E01E02, S01E01-E02
        (re.compile(
            r'[Ss](\d{1,4})[Ee](\d{1,4})'
            r'(?:[Ee](\d{1,4}))*'
            r'(?:[-~](\d{1,4}))?'
        ), 'sxe'),

        # 1x01, 01x01
        (re.compile(
            r'(\d{1,2})[xX](\d{2,4})'
            r'(?:[xX](\d{2,4}))*'
        ), 'sxe'),

        # Season 1 Episode 1
        (re.compile(
            r'[Ss]eason\s+(\d{1,4})\s*[Ee]pisode\s+(\d{1,4})'
            r'(?:\s*[,-]\s*[Ee]pisode\s+(\d{1,4}))*'
        ), 'sxe'),

        # Season 1, Episode 1 (comma separated)
        (re.compile(
            r'[Ss]eason\s+(\d{1,4})\s*,\s*[Ee]pisode\s+(\d{1,4})'
        ), 'sxe'),

        # Ep 1, EP1
        (re.compile(
            r'[Ee][Pp]\.?\s*(\d{1,4})'
        ), 'ep'),

        # #1, #01 (anime style)
        (re.compile(
            r'#(\d{1,4})'
        ), 'hash'),

        # 01, 001 (absolute episode at end or after separator)
        # Exclude year-like numbers (1900-2099)
        (re.compile(
            r'(?:^|[\s._\-\(\[])(\d{2,4})(?:v\d)?[\s._\-\)\]]'
        ), 'absolute'),

        # E101 (Episode 101, where 1 is season, 01 is episode)
        (re.compile(
            r'[Ee](\d)(\d{2,3})'
        ), 'e'),

        # 101 (3-digit episode number: season 1, episode 01)
        (re.compile(
            r'(?:^|[\s._\-\(\[])(\d)(\d{2})(?=[\s._\-\)\]]|$)'
        ), 'triple'),

        # S01 (season only)
        (re.compile(
            r'[Ss](\d{1,4})\b'
        ), 'season_only'),
    ]

    # Special episode indicators
    SPECIAL_PATTERNS = [
        re.compile(r'(?:S\d+)?[Ee]00', re.IGNORECASE),
        re.compile(r'(?:Special|OVA|OAV|SP)', re.IGNORECASE),
    ]

    @classmethod
    def match(cls, filename: str) -> Optional[SeasonEpisodeInfo]:
        """Match season/episode patterns in a filename.

        Returns SeasonEpisodeInfo if a match is found, None otherwise.
        """
        # Check for special episodes first
        is_special = any(p.search(filename) for p in cls.SPECIAL_PATTERNS)

        # Try each pattern
        for pattern, pattern_type in cls.PATTERNS:
            match = pattern.search(filename)
            if match:
                episodes = cls._extract_episodes(match, pattern_type)
                if episodes:
                    return SeasonEpisodeInfo(
                        episodes=episodes,
                        is_special=is_special,
                        raw_text=match.group(0),
                    )

        return None

    @classmethod
    def _extract_episodes(cls, match, pattern_type: str) -> List[EpisodeMatch]:
        """Extract episode matches from a regex match."""
        episodes = []

        if pattern_type == 'sxe':
            season = int(match.group(1))
            episode = int(match.group(2))
            episodes.append(EpisodeMatch(season=season, episode=episode))

            # Check for multi-episode (E01E02 or E01-E02)
            for i in range(3, len(match.groups()) + 1):
                if match.group(i):
                    episodes.append(EpisodeMatch(season=season, episode=int(match.group(i))))

        elif pattern_type == 'ep':
            episode = int(match.group(1))
            # Assume season 1 if not specified
            episodes.append(EpisodeMatch(season=1, episode=episode))

        elif pattern_type == 'hash':
            episode = int(match.group(1))
            episodes.append(EpisodeMatch(season=1, episode=episode))

        elif pattern_type == 'absolute':
            episode = int(match.group(1))
            # Exclude year-like numbers (1900-2099)
            if 1900 <= episode <= 2099:
                return []
            episodes.append(EpisodeMatch(season=1, episode=episode))

        elif pattern_type == 'e':
            season = int(match.group(1))
            episode = int(match.group(2))
            episodes.append(EpisodeMatch(season=season, episode=episode))

        elif pattern_type == 'triple':
            season = int(match.group(1))
            episode = int(match.group(2))
            episodes.append(EpisodeMatch(season=season, episode=episode))

        elif pattern_type == 'season_only':
            season = int(match.group(1))
            # Season only, no episode - return empty
            return []

        return episodes

    @classmethod
    def parse_sxe(cls, text: str) -> List[Tuple[int, int]]:
        """Parse SxE pattern and return list of (season, episode) tuples."""
        results = []
        pattern = re.compile(r'[Ss](\d{1,4})[Ee](\d{1,4})')
        for match in pattern.finditer(text):
            results.append((int(match.group(1)), int(match.group(2))))
        return results

    @classmethod
    def is_episode_filename(cls, filename: str) -> bool:
        """Check if filename contains episode information."""
        return cls.match(filename) is not None
