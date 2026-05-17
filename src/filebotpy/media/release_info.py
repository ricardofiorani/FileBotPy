"""
ReleaseInfo - Parses release information from filenames.

Based on FileBot's ReleaseInfo.properties patterns.
"""

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ReleaseInfo:
    """Parsed release information from a filename."""
    filename: str
    title: Optional[str] = None
    year: Optional[int] = None
    season: Optional[int] = None
    episode: Optional[int] = None
    multi_episodes: list = field(default_factory=list)
    resolution: Optional[str] = None
    source: Optional[str] = None
    video_codec: Optional[str] = None
    audio_codec: Optional[str] = None
    audio_channels: Optional[str] = None
    group: Optional[str] = None
    tags: list = field(default_factory=list)
    is_3d: bool = False
    is_repack: bool = False
    is_extended: bool = False
    is_theatrical: bool = False
    is_uncut: bool = False
    is_unrated: bool = False
    is_imax: bool = False
    bit_depth: Optional[str] = None
    frame_rate: Optional[str] = None
    hdr: Optional[str] = None

    @property
    def resolution_name(self) -> Optional[str]:
        """Get human-readable resolution name."""
        if self.resolution is None:
            return None
        resolution_map = {
            "7680x4320": "8K",
            "3840x2160": "4K",
            "2560x1440": "QHD",
            "2048x1080": "2K",
            "1920x1080": "1080p",
            "1280x720": "720p",
            "1024x576": "576p",
            "720x480": "480p",
            "640x360": "360p",
        }
        return resolution_map.get(self.resolution, self.resolution)


class ReleaseInfoParser:
    """Parses release information from filenames using regex patterns."""

    # Video format patterns from ReleaseInfo.properties
    VIDEO_TAGS_PATTERN = re.compile(
        r'(?:Special\.|Extended\.|Ultimate\.)?'
        r'(?:Director\.?s|Collector\.?s|Theatrical|Ultimate|Final|Extended|Rogue|'
        r'Special|Diamond|Despecialized|R\.Rated|Super\.Duper|'
        r'(?:(?:1st|2nd|3rd|[4-9]th)\.?)?Anniversary)'
        r'\.(?:Cut|Edition|Version)|'
        r'Extended|Theatrical|Remastered|Recut|Uncut|Uncensored|'
        r'Censored|Unrated|IMAX|Alternate\.Ending|Open\.Matte',
        re.IGNORECASE
    )

    S3D_PATTERN = re.compile(
        r'(?:(?:H|HALF|F|FULL)[^\w]{0,2})?(?:SBS|TAB|OU)',
        re.IGNORECASE
    )

    REPACK_PATTERN = re.compile(
        r'REPACK|PROPER|RERIP',
        re.IGNORECASE
    )

    VIDEO_FORMAT_PATTERN = re.compile(
        r'The\.[0-9]{3,4}\b|'
        r'DivX[345]?|Xvid|AVC|[xh]\.?(?:264|265)|HEVC|3ivx|PGS|'
        r'MP[E]?G[45]?|HDR[+0-9]*|DV|DoVi|Dolby\.Vision|'
        r'(?:Multi\.)?(?:FLAC|AAC|AC3|MP3|MP4|DTS|TrueHD|\bDD)'
        r'(?:[. ]?(?:HD|P|[+]))?'
        r'(?:[. \-\(]*(?:Atmos|HRA|HD|MA|ES|EX|X\b))?'
        r'(?:[. \)]*[1-9][. ]?[01])?|'
        r'[1-9]ch|FLAC(?:x[2-3])?|AAC|AC3|MP3|MP4|TrueHD|Atmos|'
        r'(?:HD|BD)?[M0]?(?:480|576|720|1080|2160|4320)[pix]+(?:60)?|'
        r'[-](?:2D|3D|480|576|720|1080|2160|4320)|'
        r'(?:7680|3840|2040|1920|1280|720|640)x[0-9]{3,4}|'
        r'(?:8|10)\.?bit|'
        r'(?:24|30|60)FPS|'
        r'Hi10[P]?|'
        r'[A-Z]{2,3}\.(?:[257][.][01])|'
        r'(?:19|20)[0-9]+\.S[0-9]+(?!\.?E[0-9]+)|'
        r'[0-9]v[0-4]|'
        r'\bCD[0-9]+\b',
        re.IGNORECASE
    )

    # Resolution patterns
    RESOLUTION_PATTERN = re.compile(
        r'(?P<width>7680|3840|2560|2048|1920|1280|1024|854|720|640|512|320)'
        r'[xX]'
        r'(?P<height>4320|2160|1440|1080|720|576|480|360|240|120)',
        re.IGNORECASE
    )

    # Common resolution shorthand
    RESOLUTION_SHORTHAND = re.compile(
        r'\b(?P<res>4320p|2160p|1440p|1080p|1080i|720p|576p|480p|360p|240p)\b',
        re.IGNORECASE
    )

    # Video codec patterns
    VIDEO_CODEC_PATTERN = re.compile(
        r'\b(?P<codec>x264|x265|h264|h265|HEVC|AVC|DivX[345]?|Xvid|MPEG[245]?|VP[89]|AV1)\b',
        re.IGNORECASE
    )

    # Audio codec patterns
    AUDIO_CODEC_PATTERN = re.compile(
        r'\b(?P<codec>'
        r'DTS(?:[.\-]?HD)?(?:[.\-]?MA)?(?:[.\-]?ES)?(?:[.\-]?EX)?|'
        r'TrueHD|Atmos|'
        r'DD(?:P|[+])?(?:[.\-]?5\.1|[.\-]?7\.1|[.\-]?2\.0)?|'
        r'AC3|AAC(?:[.\-]?LC)?|'
        r'FLAC(?:x[2-3])?|'
        r'MP3|'
        r'EAC3|'
        r'PCM'
        r')\b',
        re.IGNORECASE
    )

    # Audio channels pattern
    AUDIO_CHANNELS_PATTERN = re.compile(
        r'\b(?P<channels>[1-9]\.1|[1-9]\.0|[1-9]ch)\b',
        re.IGNORECASE
    )

    # HDR patterns
    HDR_PATTERN = re.compile(
        r'\b(?P<hdr>HDR10\+|HDR10|HDR|DoVi|Dolby\s*Vision|DV)\b',
        re.IGNORECASE
    )

    # Bit depth pattern
    BIT_DEPTH_PATTERN = re.compile(
        r'\b(?P<bit>8|10|12)\s*bit\b',
        re.IGNORECASE
    )

    # Frame rate pattern
    FRAME_RATE_PATTERN = re.compile(
        r'\b(?P<fps>24|25|30|48|50|60|120)\s*(?:fps|FPS)\b',
        re.IGNORECASE
    )

    # Source patterns
    SOURCE_PATTERN = re.compile(
        r'\b(?P<source>'
        r'BluRay|BDRip|BRRip|'
        r'WEBRip|WEB-DL|WEBDL|WEB|'
        r'HDTV|HDTVRip|'
        r'DVDRip|DVD|DVDScr|'
        r'CAM|CAMRip|TS|TC|'
        r'SCREENER|SCR|'
        r'REMUX'
        r')\b',
        re.IGNORECASE
    )

    # Release group pattern (usually at the end, after last dash or bracket)
    GROUP_PATTERN = re.compile(
        r'[-\s]+(?P<group>[A-Z][A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)\s*(?:\[[^\]]*\])?\s*\.\w+$',
        re.IGNORECASE
    )

    # Year pattern
    YEAR_PATTERN = re.compile(
        r'(?:^|[.\s\-\(\[])(?P<year>(?:19|20)\d{2})(?:[.\s\-\)\]]|$)'
    )

    # Episode title patterns (text after episode number)
    EPISODE_TITLE_PATTERNS = [
        # Ep. 01 - TITLE or Ep 01 - TITLE
        re.compile(r'[Ee][Pp]\.?\s*\d+\s*[-–]\s*(.+)', re.IGNORECASE),
        # Episode 01 - TITLE
        re.compile(r'[Ee]pisode\s*\d+\s*[-–]\s*(.+)', re.IGNORECASE),
        # S01E01 - TITLE
        re.compile(r'[Ss]\d+[Ee]\d+\s*[-–]\s*(.+)', re.IGNORECASE),
        # 01x01 - TITLE
        re.compile(r'\d{1,2}[xX]\d{2,4}\s*[-–]\s*(.+)', re.IGNORECASE),
    ]

    # Patterns to remove from episode titles
    TITLE_CLEANUP_PATTERNS = [
        # Remove parenthesized content containing resolution/quality: (480p - DVDRip), (720p), (1080p WEB-DL)
        re.compile(r'\s*\([^)]*(?:\d+[ip]|WEB|BluRay|HDTV|CAM|Rip|DL|REMUX)[^)]*\)\s*', re.IGNORECASE),
        # Remove [1080p], [720p], etc.
        re.compile(r'\s*\[\d+(?:i|p)\]\s*'),
        # Remove [Group] tags
        re.compile(r'\s*\[[^\]]*\]\s*'),
    ]

    @classmethod
    def extract_episode_title(cls, filename: str) -> Optional[str]:
        """Extract episode title from filename."""
        name = filename.rsplit('.', 1)[0] if '.' in filename else filename

        for pattern in cls.EPISODE_TITLE_PATTERNS:
            match = pattern.search(name)
            if match:
                title = match.group(1).strip()
                title = cls._clean_episode_title(title)
                return title if title else None

        return None

    @classmethod
    def _clean_episode_title(cls, title: str) -> str:
        """Clean episode title by removing resolution, source, etc."""
        for pattern in cls.TITLE_CLEANUP_PATTERNS:
            title = pattern.sub(' ', title)

        title = title.strip(' -–')
        title = ' '.join(title.split())
        return title

    @classmethod
    def parse(cls, filename: str) -> ReleaseInfo:
        """Parse release information from a filename."""
        info = ReleaseInfo(filename=filename)
        name = filename

        # Remove extension for parsing
        name_without_ext = re.sub(r'\.\w+$', '', name)

        # Parse year
        year_match = cls.YEAR_PATTERN.search(name)
        if year_match:
            info.year = int(year_match.group('year'))

        # Parse resolution
        res_match = cls.RESOLUTION_PATTERN.search(name)
        if res_match:
            info.resolution = f"{res_match.group('width')}x{res_match.group('height')}"
        else:
            res_short = cls.RESOLUTION_SHORTHAND.search(name)
            if res_short:
                res_val = res_short.group('res').lower().replace('p', '').replace('i', '')
                height_map = {
                    '4320': '7680x4320',
                    '2160': '3840x2160',
                    '1440': '2560x1440',
                    '1080': '1920x1080',
                    '720': '1280x720',
                    '576': '1024x576',
                    '480': '720x480',
                    '360': '640x360',
                }
                info.resolution = height_map.get(res_val, res_short.group('res'))

        # Parse video codec
        codec_match = cls.VIDEO_CODEC_PATTERN.search(name)
        if codec_match:
            info.video_codec = codec_match.group('codec').lower()

        # Parse audio codec
        audio_match = cls.AUDIO_CODEC_PATTERN.search(name)
        if audio_match:
            info.audio_codec = audio_match.group('codec').upper().replace('.', '')

        # Parse audio channels
        channels_match = cls.AUDIO_CHANNELS_PATTERN.search(name)
        if channels_match:
            info.audio_channels = channels_match.group('channels')

        # Parse HDR
        hdr_match = cls.HDR_PATTERN.search(name)
        if hdr_match:
            info.hdr = hdr_match.group('hdr')

        # Parse bit depth
        bit_match = cls.BIT_DEPTH_PATTERN.search(name)
        if bit_match:
            info.bit_depth = f"{bit_match.group('bit')}-bit"

        # Parse frame rate
        fps_match = cls.FRAME_RATE_PATTERN.search(name)
        if fps_match:
            info.frame_rate = f"{fps_match.group('fps')}fps"

        # Parse source
        source_match = cls.SOURCE_PATTERN.search(name)
        if source_match:
            info.source = source_match.group('source')

        # Parse tags
        tags_match = cls.VIDEO_TAGS_PATTERN.finditer(name)
        for match in tags_match:
            tag = match.group().lower()
            info.tags.append(tag)
            if 'extended' in tag:
                info.is_extended = True
            if 'theatrical' in tag:
                info.is_theatrical = True
            if 'uncut' in tag:
                info.is_uncut = True
            if 'unrated' in tag:
                info.is_unrated = True
            if 'imax' in tag:
                info.is_imax = True

        # Parse 3D
        if cls.S3D_PATTERN.search(name):
            info.is_3d = True
            info.tags.append('3d')

        # Parse repack
        if cls.REPACK_PATTERN.search(name):
            info.is_repack = True
            info.tags.append('repack')

        # Parse release group
        group_match = cls.GROUP_PATTERN.search(name)
        if group_match:
            info.group = group_match.group('group')

        # Parse episode title
        info.title = cls.extract_episode_title(filename)

        return info
