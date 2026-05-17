"""
SeriesNameMatcher - Matches series names from filenames.

Based on FileBot's SeriesNameMatcher class.
"""

import re
from typing import List, Optional, Tuple


class SeriesNameMatcher:
    """Matches and extracts series names from filenames."""

    # Patterns to remove from series names
    CLEANUP_PATTERNS = [
        # Remove year in parentheses
        re.compile(r'\s*\(\d{4}\)\s*'),
        # Remove resolution
        re.compile(r'\s*(?:720|1080|2160|480|576)[pi]+\s*', re.IGNORECASE),
        # Remove codec
        re.compile(r'\s*(?:x264|x265|h264|h265|HEVC|AVC)\s*', re.IGNORECASE),
        # Remove source
        re.compile(r'\s*(?:WEB[-.]?DL|WEBRip|BluRay|HDTV|DVDRip)\s*', re.IGNORECASE),
        # Remove group tags
        re.compile(r'\s*\[[^\]]*\]\s*'),
        re.compile(r'\s*\([^\)]*\)\s*$'),
        # Remove trailing separators
        re.compile(r'[\s._\-]+$'),
        # Remove leading separators
        re.compile(r'^[\s._\-]+'),
    ]

    # Common words to ignore in matching
    IGNORE_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
        'for', 'of', 'with', 'by', 'from',
    }

    @classmethod
    def extract_series_name(cls, filename: str) -> Optional[str]:
        """Extract series name from filename.

        This is a simplified extraction - full matching requires
        episode pattern matching first to know where the name ends.
        """
        # Remove extension
        name = filename.rsplit('.', 1)[0] if '.' in filename else filename

        # Try to find where the series name ends (before SxE or year)
        # Look for S01E01 pattern
        sxe_match = re.search(r'[Ss]\d{1,4}[Ee]\d{1,4}', name)
        if sxe_match:
            name = name[:sxe_match.start()]

        # Look for (Year) pattern
        year_match = re.search(r'\(\d{4}\)', name)
        if year_match:
            name = name[:year_match.start()]

        # Look for .Year. pattern (movies without parentheses)
        year_dot_match = re.search(r'[\._](\d{4})[\._]', name)
        if year_dot_match:
            name = name[:year_dot_match.start()]

        # Look for 1x01 pattern
        x_match = re.search(r'\d{1,2}[xX]\d{2,4}', name)
        if x_match:
            name = name[:x_match.start()]

        # Look for Ep. 01 pattern
        ep_match = re.search(r'[Ee][Pp]\.?\s*\d+', name)
        if ep_match:
            name = name[:ep_match.start()]

        # Look for Episode 01 pattern
        episode_match = re.search(r'[Ee]pisode\s*\d+', name)
        if episode_match:
            name = name[:episode_match.start()]

        # Clean up the name
        name = cls._clean_name(name)

        return name if name else None

    @classmethod
    def _clean_name(cls, name: str) -> str:
        """Clean up a series name."""
        # Apply cleanup patterns
        for pattern in cls.CLEANUP_PATTERNS:
            name = pattern.sub(' ', name)

        # Normalize whitespace
        name = ' '.join(name.split())

        # Remove trailing/leading dots
        name = name.strip('. ')

        return name

    @classmethod
    def normalize_name(cls, name: str) -> str:
        """Normalize a series name for comparison."""
        # Clean the name first
        name = cls._clean_name(name)

        # Lowercase
        name = name.lower()

        # Remove special characters
        name = re.sub(r'[^\w\s]', '', name)

        # Normalize whitespace
        name = ' '.join(name.split())

        return name

    @classmethod
    def similarity(cls, name1: str, name2: str) -> float:
        """Calculate similarity between two series names.

        Returns a value between 0.0 and 1.0.
        """
        norm1 = cls.normalize_name(name1)
        norm2 = cls.normalize_name(name2)

        if norm1 == norm2:
            return 1.0

        # Tokenize
        tokens1 = set(norm1.split())
        tokens2 = set(norm2.split())

        # Remove ignore words
        tokens1 -= cls.IGNORE_WORDS
        tokens2 -= cls.IGNORE_WORDS

        if not tokens1 or not tokens2:
            return 0.0

        # Calculate Jaccard similarity
        intersection = tokens1 & tokens2
        union = tokens1 | tokens2

        if not union:
            return 0.0

        return len(intersection) / len(union)

    @classmethod
    def match(cls, filename: str, series_names: List[str], threshold: float = 0.7) -> Optional[Tuple[str, float]]:
        """Match filename against a list of series names.

        Returns (matched_name, similarity_score) or None if no match.
        """
        filename_name = cls.extract_series_name(filename)
        if not filename_name:
            return None

        best_match = None
        best_score = 0.0

        for series_name in series_names:
            score = cls.similarity(filename_name, series_name)
            if score > best_score:
                best_score = score
                best_match = series_name

        if best_score >= threshold:
            return (best_match, best_score)

        return None
