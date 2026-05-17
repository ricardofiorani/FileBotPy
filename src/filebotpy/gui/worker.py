"""Background worker for matching files."""

import re
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal

from filebotpy.media.detector import AutoDetection, MediaType
from filebotpy.media.release_info import ReleaseInfoParser
from filebotpy.naming.engine import ExpressionFormat, FormatBindings
from filebotpy.naming.templates import NamingTemplates
from filebotpy.similarity.episode import SeasonEpisodeMatcher
from filebotpy.similarity.series import SeriesNameMatcher
from filebotpy.web.tmdb import TMDbClient
from filebotpy.web.tvdb import TheTVDBClient


class MatchingWorker(QObject):
    """Worker thread for matching files to media databases."""

    progress = pyqtSignal(str)
    match_complete = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, tmdb_api_key: str = "", tvdb_api_key: str = ""):
        super().__init__()
        self._files = []
        self._tmdb_api_key = tmdb_api_key
        self._tvdb_api_key = tvdb_api_key
        self._tmdb_client: Optional[TMDbClient] = None
        self._tvdb_client: Optional[TheTVDBClient] = None

    def set_api_keys(self, tmdb_api_key: str, tvdb_api_key: str):
        """Set API keys for TMDb and TVDB."""
        self._tmdb_api_key = tmdb_api_key
        self._tvdb_api_key = tvdb_api_key
        self._tmdb_client = None
        self._tvdb_client = None

    def set_files(self, files: list[str]):
        """Set files to process."""
        self._files = files

    def run(self):
        """Run the matching process."""
        try:
            mappings = []
            for i, file_path in enumerate(self._files):
                self.progress.emit(f"Processing {i + 1}/{len(self._files)}: {Path(file_path).name}")

                try:
                    path = Path(file_path)
                    release_info = ReleaseInfoParser.parse(path.name)
                    detection = AutoDetection.detect(path)

                    if detection == MediaType.TV:
                        template = NamingTemplates.get_tv_template('with_title')
                        series_name, season, episode, episode_title = self._match_tv_episode(path.name, release_info)
                        bindings = self._create_tv_bindings(release_info, series_name, season, episode, episode_title)
                    elif detection == MediaType.MOVIE:
                        template = NamingTemplates.get_movie_template('default')
                        movie_name, movie_year = self._match_movie(path.name, release_info)
                        bindings = self._create_movie_bindings(release_info, movie_name, movie_year)
                    else:
                        new_name = path.stem
                        new_path = str(path.parent / new_name)
                        mappings.append((file_path, new_path))
                        continue

                    formatter = ExpressionFormat(template)
                    new_name = formatter.format(bindings)
                    ext = path.suffix
                    new_path = str(path.parent / f"{new_name}{ext}")
                    mappings.append((file_path, new_path))
                except Exception as e:
                    mappings.append((file_path, ""))

            self.match_complete.emit(mappings)
        except Exception as e:
            self.error.emit(str(e))

    def _get_tvdb_client(self) -> Optional[TheTVDBClient]:
        """Get or create TVDB client."""
        if not self._tvdb_api_key:
            return None
        if self._tvdb_client is None:
            try:
                self._tvdb_client = TheTVDBClient(self._tvdb_api_key)
            except Exception:
                return None
        return self._tvdb_client

    def _get_tmdb_client(self) -> Optional[TMDbClient]:
        """Get or create TMDb client."""
        if not self._tmdb_api_key:
            return None
        if self._tmdb_client is None:
            try:
                self._tmdb_client = TMDbClient(self._tmdb_api_key)
            except Exception:
                return None
        return self._tmdb_client

    def _match_tv_episode(self, filename: str, release_info) -> tuple[str, int, int, Optional[str]]:
        """Match TV episode using API lookup.
        
        Returns (series_name, season, episode, episode_title).
        """
        episode_info = SeasonEpisodeMatcher.match(filename)
        season = episode_info.episodes[0].season if episode_info and episode_info.episodes else 1
        episode = episode_info.episodes[0].episode if episode_info and episode_info.episodes else 1

        series_name = SeriesNameMatcher.extract_series_name(filename)
        
        if not series_name:
            series_name = release_info.title

        episode_title = release_info.title

        if series_name and self._tvdb_api_key:
            self.progress.emit(f"Looking up '{series_name}' on TheTVDB...")
            tvdb_client = self._get_tvdb_client()
            if tvdb_client:
                try:
                    results = tvdb_client.search_series(series_name)
                    if results:
                        canonical_name = results[0].name
                        self.progress.emit(f"Found: {canonical_name}")
                        return canonical_name, season, episode, episode_title
                except Exception:
                    pass

        return series_name or "Unknown Series", season, episode, episode_title

    def _match_movie(self, filename: str, release_info) -> tuple[str, Optional[int]]:
        """Match movie using API lookup.
        
        Returns (movie_name, year).
        """
        from filebotpy.similarity.movie import MovieMatcher
        
        movie_info = MovieMatcher.extract_movie_info(filename)
        movie_name = movie_info[0] if movie_info else None
        movie_year = movie_info[1] if movie_info else release_info.year

        if not movie_name:
            movie_name = release_info.title

        if movie_name and self._tmdb_api_key:
            self.progress.emit(f"Looking up '{movie_name}' on TMDb...")
            tmdb_client = self._get_tmdb_client()
            if tmdb_client:
                try:
                    results = tmdb_client.search_movie(movie_name, movie_year)
                    if results:
                        canonical_title = results[0].title
                        canonical_year = results[0].year
                        self.progress.emit(f"Found: {canonical_title} ({canonical_year})")
                        return canonical_title, canonical_year
                except Exception:
                    pass

        return movie_name or "Unknown Movie", movie_year

    def _create_tv_bindings(self, release_info, series_name: str, season: int, episode: int, episode_title: Optional[str] = None) -> FormatBindings:
        """Create bindings for TV shows."""
        return FormatBindings(
            n=series_name,
            s=season,
            e=episode,
            t=episode_title or f"Episode {episode}",
            y=release_info.year or 0,
            vf=release_info.resolution_name or "",
            cf=release_info.video_codec or "",
            ac=release_info.audio_codec or "",
            fn=release_info.filename or "",
            group=release_info.group or "",
            source=release_info.source or "",
            hdr=release_info.hdr or "",
        )

    def _create_movie_bindings(self, release_info, movie_name: str, movie_year: Optional[int]) -> FormatBindings:
        """Create bindings for movies."""
        return FormatBindings(
            n=movie_name,
            y=movie_year or 0,
            vf=release_info.resolution_name or "",
            cf=release_info.video_codec or "",
            ac=release_info.audio_codec or "",
            fn=release_info.filename or "",
            group=release_info.group or "",
            source=release_info.source or "",
            hdr=release_info.hdr or "",
        )
