"""
NamingTemplates - Built-in naming templates for different media types.

Jellyfin-compatible naming formats.
"""

from typing import Dict


class NamingTemplates:
    """Built-in naming templates for Jellyfin-compatible formats."""

    # TV Show templates
    TV_TEMPLATES: Dict[str, str] = {
        # Default: /Show Name/Season 01/Show Name S01E01 - Episode Title.ext
        'default': '{n}/Season {s00}/{n} S{s00}E{e00} - {t}',

        # Compact: /Show Name/S01/Show Name S01E01 Episode Title.ext
        'compact': '{n}/S{s00}/{n} S{s00}E{e00} {t}',

        # Plex style: /Show Name/Season 01/Show Name - S01E01 - Episode Title.ext
        'plex': '{n}/Season {s00}/{n} - S{s00}E{e00} - {t}',

        # Jellyfin style: /Show Name/Season 01/Show Name - S01E01.ext
        'jellyfin': '{n}/Season {s00}/{n} - S{s00}E{e00}',

        # With episode title: Show Name S01E01 - Episode Title.ext
        'with_title': '{n} S{s00}E{e00} - {t}',

        # Kodi style: /Show Name/Season 01/Show Name S01E01 Episode Title.ext
        'kodi': '{n}/Season {s00}/{n} S{s00}E{e00} {t}',

        # Absolute episode: /Show Name/Show Name - 001.ext
        'absolute': '{n}/{n} - {e000}',

        # Anime style: /Show Name/Show Name - S01E01 - Episode Title [Group].ext
        'anime': '{n}/{n} - S{s00}E{e00} - {t} [{group}]',
    }

    # Movie templates
    MOVIE_TEMPLATES: Dict[str, str] = {
        # Default: /Movie Name (Year)/Movie Name (Year).ext
        'default': '{n} ({y})/{n} ({y})',

        # Compact: /Movie Name (Year)/Movie Name.ext
        'compact': '{n} ({y})/{n}',

        # Plex/Jellyfin style: /Movie Name (Year)/Movie Name (Year).ext
        'plex': '{n} ({y})/{n} ({y})',

        # With resolution: /Movie Name (Year)/Movie Name (Year) [1080p].ext
        'with_quality': '{n} ({y})/{n} ({y}) [{vf}]',

        # With quality and codec: /Movie Name (Year)/Movie Name (Year) [1080p x264].ext
        'with_details': '{n} ({y})/{n} ({y}) [{vf} {cf}]',
    }

    # Anime templates
    ANIME_TEMPLATES: Dict[str, str] = {
        # Default: /Anime Name/Anime Name - S01E01 - Episode Title.ext
        'default': '{n}/{n} - S{s00}E{e00} - {t}',

        # Absolute: /Anime Name/Anime Name - 001.ext
        'absolute': '{n}/{n} - {e000}',

        # With group: /Anime Name/[Group] Anime Name - 001.ext
        'with_group': '{n}/[{group}] {n} - {e000}',

        # Batch: /Anime Name/Season 01/Anime Name S01E01 - Episode Title.ext
        'seasonal': '{n}/Season {s00}/{n} S{s00}E{e00} - {t}',
    }

    # Music templates
    MUSIC_TEMPLATES: Dict[str, str] = {
        # Default: /Artist/Album/01 - Track Title.ext
        'default': '{n}/{album}/{track:02} - {t}',

        # By year: /Artist (Year)/Album/01 - Track Title.ext
        'by_year': '{n} ({y})/{album}/{track:02} - {t}',
    }

    @classmethod
    def get_tv_template(cls, style: str = 'default') -> str:
        """Get TV show naming template."""
        return cls.TV_TEMPLATES.get(style, cls.TV_TEMPLATES['default'])

    @classmethod
    def get_movie_template(cls, style: str = 'default') -> str:
        """Get movie naming template."""
        return cls.MOVIE_TEMPLATES.get(style, cls.MOVIE_TEMPLATES['default'])

    @classmethod
    def get_anime_template(cls, style: str = 'default') -> str:
        """Get anime naming template."""
        return cls.ANIME_TEMPLATES.get(style, cls.ANIME_TEMPLATES['default'])

    @classmethod
    def get_music_template(cls, style: str = 'default') -> str:
        """Get music naming template."""
        return cls.MUSIC_TEMPLATES.get(style, cls.MUSIC_TEMPLATES['default'])

    @classmethod
    def list_styles(cls, media_type: str = 'tv') -> Dict[str, str]:
        """List available naming styles for a media type."""
        type_map = {
            'tv': cls.TV_TEMPLATES,
            'movie': cls.MOVIE_TEMPLATES,
            'anime': cls.ANIME_TEMPLATES,
            'music': cls.MUSIC_TEMPLATES,
        }
        return type_map.get(media_type.lower(), cls.TV_TEMPLATES)
