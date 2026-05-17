"""Web service clients module."""

from filebotpy.web.tvdb import TheTVDBClient
from filebotpy.web.tmdb import TMDbClient
from filebotpy.web.models import Episode, Series, Movie

__all__ = [
    "TheTVDBClient",
    "TMDbClient",
    "Episode",
    "Series",
    "Movie",
]
