"""
Data models for web services.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional


@dataclass
class Episode:
    """TV Episode information."""
    id: Optional[int] = None
    series_id: Optional[int] = None
    season: Optional[int] = None
    episode: Optional[int] = None
    absolute_number: Optional[int] = None
    title: Optional[str] = None
    overview: Optional[str] = None
    first_aired: Optional[date] = None
    runtime: Optional[int] = None
    director: Optional[str] = None
    writers: List[str] = field(default_factory=list)
    guest_stars: List[str] = field(default_factory=list)
    rating: Optional[float] = None
    votes: Optional[int] = None
    thumbnail: Optional[str] = None

    @property
    def sxe(self) -> str:
        """Get SxxEyy formatted string."""
        if self.season is not None and self.episode is not None:
            return f"S{self.season:02d}E{self.episode:02d}"
        return ""

    @property
    def air_date_str(self) -> Optional[str]:
        """Get air date as string."""
        if self.first_aired:
            return self.first_aired.isoformat()
        return None


@dataclass
class Series:
    """TV Series information."""
    id: Optional[int] = None
    name: Optional[str] = None
    overview: Optional[str] = None
    first_aired: Optional[date] = None
    network: Optional[str] = None
    status: Optional[str] = None
    runtime: Optional[int] = None
    genre: List[str] = field(default_factory=list)
    rating: Optional[float] = None
    votes: Optional[int] = None
    language: Optional[str] = None
    country: Optional[str] = None
    poster: Optional[str] = None
    fanart: Optional[str] = None
    episodes: List[Episode] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)

    @property
    def year(self) -> Optional[int]:
        """Get year from first_aired."""
        if self.first_aired:
            return self.first_aired.year
        return None


@dataclass
class Movie:
    """Movie information."""
    id: Optional[int] = None
    title: Optional[str] = None
    overview: Optional[str] = None
    release_date: Optional[date] = None
    runtime: Optional[int] = None
    genre: List[str] = field(default_factory=list)
    director: Optional[str] = None
    cast: List[str] = field(default_factory=list)
    rating: Optional[float] = None
    votes: Optional[int] = None
    language: Optional[str] = None
    country: Optional[str] = None
    poster: Optional[str] = None
    backdrop: Optional[str] = None
    collection: Optional[str] = None
    budget: Optional[int] = None
    revenue: Optional[int] = None
    tagline: Optional[str] = None
    aliases: List[str] = field(default_factory=list)

    @property
    def year(self) -> Optional[int]:
        """Get year from release_date."""
        if self.release_date:
            return self.release_date.year
        return None
