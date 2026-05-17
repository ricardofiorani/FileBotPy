"""
TheTVDBClient - Client for TheTVDB API v4.

Based on FileBot's TheTVDBClientV4 class.
"""

import re
from datetime import datetime, date
from typing import List, Optional

from filebotpy.web.models import Episode, Series


class TheTVDBClient:
    """Client for TheTVDB API v4.

    Requires an API key from https://thetvdb.com/api-information
    """

    BASE_URL = "https://api4.thetvdb.com/v4"

    def __init__(self, api_key: str):
        """Initialize with API key."""
        self.api_key = api_key
        self._token: Optional[str] = None
        self._session = None

    def _get_session(self):
        """Get requests session with authentication."""
        if self._session is None:
            import requests
            self._session = requests.Session()
            self._authenticate()
        return self._session

    def _authenticate(self):
        """Authenticate with TheTVDB API."""
        import requests
        url = f"{self.BASE_URL}/login"
        response = requests.post(url, json={"apikey": self.api_key})
        response.raise_for_status()
        data = response.json()
        self._token = data.get("data", {}).get("token")
        self._session.headers.update({"Authorization": f"Bearer {self._token}"})

    def search_series(self, name: str, language: str = "en") -> List[Series]:
        """Search for series by name."""
        session = self._get_session()
        url = f"{self.BASE_URL}/search"
        params = {"query": name, "type": "series"}
        response = session.get(url, params=params)
        response.raise_for_status()

        data = response.json().get("data", [])
        results = []

        for item in data:
            series = Series(
                id=item.get("tvdb_id"),
                name=item.get("name"),
                overview=item.get("overview"),
                first_aired=self._parse_date(item.get("first_air_time")),
                network=item.get("network"),
                status=item.get("status"),
                genre=item.get("genres", []),
                language=language,
                poster=item.get("image_url"),
                aliases=item.get("aliases", []),
            )
            results.append(series)

        return results

    def get_series(self, series_id: int, language: str = "en") -> Optional[Series]:
        """Get series details by ID."""
        session = self._get_session()
        url = f"{self.BASE_URL}/series/{series_id}/extended"
        params = {"meta": "translations"}
        response = session.get(url, params=params)
        response.raise_for_status()

        data = response.json().get("data", {})
        return self._parse_series(data, language)

    def get_series_episodes(self, series_id: int, season: int = 0, language: str = "en") -> List[Episode]:
        """Get episodes for a series/season."""
        session = self._get_session()
        url = f"{self.BASE_URL}/series/{series_id}/episodes/default"
        params = {"season": season, "seasonType": "official"}
        response = session.get(url, params=params)
        response.raise_for_status()

        data = response.json().get("data", [])
        episodes = []

        for item in data:
            episode = self._parse_episode(item)
            episodes.append(episode)

        return episodes

    def get_episode(self, episode_id: int, language: str = "en") -> Optional[Episode]:
        """Get episode details by ID."""
        session = self._get_session()
        url = f"{self.BASE_URL}/episodes/{episode_id}/extended"
        response = session.get(url)
        response.raise_for_status()

        data = response.json().get("data", {})
        return self._parse_episode(data)

    def lookup_by_filename(self, filename: str, language: str = "en") -> Optional[Series]:
        """Look up series by filename (extracts name and searches)."""
        # Extract series name from filename
        name = self._extract_series_name(filename)
        if not name:
            return None

        results = self.search_series(name, language)
        if results:
            return results[0]
        return None

    def _extract_series_name(self, filename: str) -> Optional[str]:
        """Extract series name from filename."""
        # Remove extension
        name = filename.rsplit('.', 1)[0] if '.' in filename else filename

        # Remove SxE pattern and everything after
        name = re.sub(r'[Ss]\d{1,4}[Ee]\d{1,4}.*$', '', name)

        # Remove (Year) pattern
        name = re.sub(r'\(\d{4}\)', '', name)

        # Remove resolution, codec, etc.
        name = re.sub(r'\s*(?:720|1080|2160|480|576)[pi]+', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*(?:x264|x265|h264|h265|HEVC)', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*(?:WEB[-.]?DL|WEBRip|BluRay|HDTV)', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*\[[^\]]*\]', '', name)

        # Clean up
        name = name.strip('. -')
        name = ' '.join(name.split())

        return name if name else None

    def _parse_series(self, data: dict, language: str = "en") -> Optional[Series]:
        """Parse series data from API response."""
        if not data:
            return None

        return Series(
            id=data.get("id"),
            name=data.get("name"),
            overview=data.get("overview"),
            first_aired=self._parse_date(data.get("firstAired")),
            network=data.get("network"),
            status=data.get("status"),
            runtime=data.get("averageRuntime"),
            genre=data.get("genres", []),
            rating=data.get("rating"),
            votes=data.get("ratingCount"),
            language=language,
            poster=data.get("image"),
            fanart=data.get("fanart"),
            aliases=data.get("aliases", []),
        )

    def _parse_episode(self, data: dict) -> Episode:
        """Parse episode data from API response."""
        return Episode(
            id=data.get("id"),
            series_id=data.get("seriesId"),
            season=data.get("seasonNumber"),
            episode=data.get("number"),
            absolute_number=data.get("absoluteNumber"),
            title=data.get("name"),
            overview=data.get("overview"),
            first_aired=self._parse_date(data.get("aired")),
            runtime=data.get("runtime"),
            director=data.get("directors", [{}])[0].get("name") if data.get("directors") else None,
            writers=[w.get("name") for w in data.get("writers", [])] if data.get("writers") else [],
            guest_stars=[g.get("name") for g in data.get("guestStars", [])] if data.get("guestStars") else [],
            rating=data.get("rating"),
            votes=data.get("ratingCount"),
            thumbnail=data.get("image"),
        )

    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[date]:
        """Parse date string from API."""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None
