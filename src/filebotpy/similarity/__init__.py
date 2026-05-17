"""Similarity matching module."""

from filebotpy.similarity.episode import SeasonEpisodeMatcher
from filebotpy.similarity.series import SeriesNameMatcher
from filebotpy.similarity.movie import MovieMatcher
from filebotpy.similarity.metrics import SimilarityMetric

__all__ = [
    "SeasonEpisodeMatcher",
    "SeriesNameMatcher",
    "MovieMatcher",
    "SimilarityMetric",
]
