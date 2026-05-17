"""
MovieMatcher - Matches movie names from filenames.

Based on FileBot's movie matching logic.
"""

import re
from typing import List, Optional, Tuple


class MovieMatcher:
    """Matches movie names from filenames."""

    # Movie name patterns
    MOVIE_YEAR_PATTERN = re.compile(
        r'^(.+?)[.\s\-\(\[]+(?P<year>(?:19|20)\d{2})[.\s\-\)\]]'
    )

    # Alternative year pattern
    ALT_YEAR_PATTERN = re.compile(
        r'^(.+?)[.\s]+(?P<year>(?:19|20)\d{2})[.\s]'
    )

    @classmethod
    def extract_movie_info(cls, filename: str) -> Optional[Tuple[str, int]]:
        """Extract movie name and year from filename.

        Returns (name, year) tuple or None if not a movie.
        """
        # Remove extension
        name = filename.rsplit('.', 1)[0] if '.' in filename else filename

        # Try to match name (year) pattern
        match = cls.MOVIE_YEAR_PATTERN.search(name)
        if match:
            movie_name = match.group(1).strip('. -')
            year = int(match.group('year'))
            return (cls._clean_name(movie_name), year)

        # Try alternative pattern
        match = cls.ALT_YEAR_PATTERN.search(name)
        if match:
            movie_name = match.group(1).strip('. -')
            year = int(match.group('year'))
            return (cls._clean_name(movie_name), year)

        return None

    @classmethod
    def _clean_name(cls, name: str) -> str:
        """Clean up a movie name."""
        # Remove common patterns
        name = re.sub(r'\s*(?:720|1080|2160|480|576)[pi]+\s*', ' ', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*(?:x264|x265|h264|h265|HEVC)\s*', ' ', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*(?:WEB[-.]?DL|WEBRip|BluRay|HDTV)\s*', ' ', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*\[[^\]]*\]\s*', ' ', name)

        # Normalize whitespace
        name = ' '.join(name.split())

        return name.strip()

    @classmethod
    def normalize_name(cls, name: str) -> str:
        """Normalize a movie name for comparison."""
        name = cls._clean_name(name).lower()
        name = re.sub(r'[^\w\s]', '', name)
        name = ' '.join(name.split())
        return name

    @classmethod
    def similarity(cls, name1: str, name2: str) -> float:
        """Calculate similarity between two movie names."""
        norm1 = cls.normalize_name(name1)
        norm2 = cls.normalize_name(name2)

        if norm1 == norm2:
            return 1.0

        # Tokenize and calculate Jaccard similarity
        tokens1 = set(norm1.split())
        tokens2 = set(norm2.split())

        if not tokens1 or not tokens2:
            return 0.0

        intersection = tokens1 & tokens2
        union = tokens1 | tokens2

        return len(intersection) / len(union) if union else 0.0

    @classmethod
    def match(cls, filename: str, movie_names: List[Tuple[str, int]], threshold: float = 0.7) -> Optional[Tuple[str, int, float]]:
        """Match filename against a list of movie names with years.

        Returns (movie_name, year, similarity_score) or None.
        """
        file_info = cls.extract_movie_info(filename)
        if not file_info:
            return None

        file_name, file_year = file_info
        best_match = None
        best_score = 0.0

        for movie_name, movie_year in movie_names:
            # Year must match or be close
            if abs(movie_year - file_year) > 2:
                continue

            score = cls.similarity(file_name, movie_name)
            if score > best_score:
                best_score = score
                best_match = (movie_name, movie_year)

        if best_match and best_score >= threshold:
            return (best_match[0], best_match[1], best_score)

        return None
