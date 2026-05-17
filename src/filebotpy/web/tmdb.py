"""
TMDbClient - Client for The Movie Database API.

Based on FileBot's TMDbMovieClient class.
"""

import re
from datetime import datetime, date
from typing import List, Optional

from filebotpy.web.models import Movie


class TMDbClient:
    """Client for The Movie Database (TMDb) API.

    Requires an API key from https://www.themoviedb.org/settings/api
    """

    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/"

    def __init__(self, api_key: str, language: str = "en-US"):
        """Initialize with API key."""
        self.api_key = api_key
        self.language = language
        self._session = None

    def _get_session(self):
        """Get requests session with API key."""
        if self._session is None:
            import requests
            self._session = requests.Session()
            self._session.params.update({"api_key": self.api_key})
        return self._session

    def search_movie(self, query: str, year: Optional[int] = None) -> List[Movie]:
        """Search for movies by title."""
        session = self._get_session()
        url = f"{self.BASE_URL}/search/movie"
        params = {"query": query, "language": self.language}
        if year:
            params["year"] = year

        response = session.get(url, params=params)
        response.raise_for_status()

        data = response.json().get("results", [])
        results = []

        for item in data:
            movie = Movie(
                id=item.get("id"),
                title=item.get("title"),
                overview=item.get("overview"),
                release_date=self._parse_date(item.get("release_date")),
                runtime=None,  # Not available in search results
                genre=[],  # Not available in search results
                rating=item.get("vote_average"),
                votes=item.get("vote_count"),
                poster=item.get("poster_path"),
                backdrop=item.get("backdrop_path"),
            )
            results.append(movie)

        return results

    def get_movie(self, movie_id: int) -> Optional[Movie]:
        """Get movie details by ID."""
        session = self._get_session()
        url = f"{self.BASE_URL}/movie/{movie_id}"
        params = {"language": self.language, "append_to_response": "credits"}

        response = session.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        return self._parse_movie(data)

    def find_by_external_id(self, external_id: str, source: str = "imdb_id") -> Optional[Movie]:
        """Find movie by external ID (IMDb, etc.)."""
        session = self._get_session()
        url = f"{self.BASE_URL}/find/{external_id}"
        params = {"external_source": source, "language": self.language}

        response = session.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        results = data.get("movie_results", [])

        if results:
            return self._parse_movie(results[0])
        return None

    def lookup_by_filename(self, filename: str) -> Optional[Movie]:
        """Look up movie by filename."""
        # Extract movie name and year from filename
        name, year = self._extract_movie_info(filename)
        if not name:
            return None

        results = self.search_movie(name, year)
        if results:
            return results[0]
        return None

    def _extract_movie_info(self, filename: str) -> tuple:
        """Extract movie name and year from filename."""
        # Remove extension
        name = filename.rsplit('.', 1)[0] if '.' in filename else filename

        # Try to find year
        year_match = re.search(r'[\(\.\s](\d{4})[\)\.\s]', name)
        year = int(year_match.group(1)) if year_match else None

        # Remove year from name
        if year_match:
            name = name[:year_match.start()] + name[year_match.end():]

        # Clean up name
        name = re.sub(r'\s*(?:720|1080|2160|480|576)[pi]+', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*(?:x264|x265|h264|h265|HEVC)', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*(?:WEB[-.]?DL|WEBRip|BluRay|HDTV)', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*\[[^\]]*\]', '', name)
        name = re.sub(r'[\._]', ' ', name)

        # Clean up
        name = name.strip(' -')
        name = ' '.join(name.split())

        return name if name else None, year

    def _parse_movie(self, data: dict) -> Movie:
        """Parse movie data from API response."""
        return Movie(
            id=data.get("id"),
            title=data.get("title"),
            overview=data.get("overview"),
            release_date=self._parse_date(data.get("release_date")),
            runtime=data.get("runtime"),
            genre=[g.get("name") for g in data.get("genres", [])] if data.get("genres") else [],
            director=self._get_director(data.get("credits", {})),
            cast=self._get_cast(data.get("credits", {})),
            rating=data.get("vote_average"),
            votes=data.get("vote_count"),
            language=data.get("original_language"),
            poster=data.get("poster_path"),
            backdrop=data.get("backdrop_path"),
            collection=data.get("belongs_to_collection", {}).get("name") if data.get("belongs_to_collection") else None,
            budget=data.get("budget"),
            revenue=data.get("revenue"),
            tagline=data.get("tagline"),
        )

    @staticmethod
    def _get_director(credits: dict) -> Optional[str]:
        """Get director from credits."""
        crew = credits.get("crew", [])
        for person in crew:
            if person.get("job") == "Director":
                return person.get("name")
        return None

    @staticmethod
    def _get_cast(credits: dict) -> List[str]:
        """Get cast from credits."""
        cast_list = []
        for person in credits.get("cast", [])[:10]:  # Top 10 cast members
            cast_list.append(person.get("name"))
        return cast_list

    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[date]:
        """Parse date string from API."""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None

    def get_image_url(self, path: Optional[str], size: str = "original") -> Optional[str]:
        """Get full image URL from path."""
        if not path:
            return None
        return f"{self.IMAGE_BASE_URL}{size}{path}"
