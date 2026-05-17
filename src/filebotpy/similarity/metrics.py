"""
SimilarityMetric - Base class and implementations for similarity metrics.

Based on FileBot's SimilarityMetric interface and various metric implementations.
"""

import re
from abc import ABC, abstractmethod
from typing import Any


class SimilarityMetric(ABC):
    """Base class for similarity metrics."""

    @abstractmethod
    def compare(self, a: Any, b: Any) -> float:
        """Compare two items and return similarity score (0.0 to 1.0)."""
        pass


class StringSimilarityMetric(SimilarityMetric):
    """String similarity using Levenshtein distance ratio."""

    def compare(self, a: str, b: str) -> float:
        if not a or not b:
            return 0.0

        a_lower = a.lower()
        b_lower = b.lower()

        if a_lower == b_lower:
            return 1.0

        # Calculate Levenshtein distance
        distance = self._levenshtein_distance(a_lower, b_lower)
        max_len = max(len(a_lower), len(b_lower))

        return 1.0 - (distance / max_len)

    @staticmethod
    def _levenshtein_distance(s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return SimilarityMetric._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]


class NormalizedStringMetric(SimilarityMetric):
    """String similarity with normalization."""

    def compare(self, a: str, b: str) -> float:
        if not a or not b:
            return 0.0

        norm_a = self._normalize(a)
        norm_b = self._normalize(b)

        if norm_a == norm_b:
            return 1.0

        # Token-based similarity
        tokens_a = set(norm_a.split())
        tokens_b = set(norm_b.split())

        if not tokens_a or not tokens_b:
            return 0.0

        intersection = tokens_a & tokens_b
        union = tokens_a | tokens_b

        return len(intersection) / len(union) if union else 0.0

    @staticmethod
    def _normalize(s: str) -> str:
        """Normalize string for comparison."""
        s = s.lower()
        s = re.sub(r'[^\w\s]', '', s)
        s = re.sub(r'\s+', ' ', s).strip()
        return s


class MetricCascade(SimilarityMetric):
    """Cascade of metrics - returns first non-zero result."""

    def __init__(self, *metrics: SimilarityMetric):
        self.metrics = metrics

    def compare(self, a: Any, b: Any) -> float:
        for metric in self.metrics:
            score = metric.compare(a, b)
            if score > 0:
                return score
        return 0.0


class MetricAvg(SimilarityMetric):
    """Average of multiple metrics."""

    def __init__(self, *metrics: SimilarityMetric):
        self.metrics = metrics

    def compare(self, a: Any, b: Any) -> float:
        if not self.metrics:
            return 0.0

        scores = [m.compare(a, b) for m in self.metrics]
        return sum(scores) / len(scores)


class MetricMin(SimilarityMetric):
    """Minimum of multiple metrics."""

    def __init__(self, *metrics: SimilarityMetric):
        self.metrics = metrics

    def compare(self, a: Any, b: Any) -> float:
        if not self.metrics:
            return 0.0

        scores = [m.compare(a, b) for m in self.metrics]
        return min(scores)
