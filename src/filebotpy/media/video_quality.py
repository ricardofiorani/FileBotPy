"""
VideoQuality - Video quality detection and classification.

Based on FileBot's VideoQuality class and VideoFormat.properties.
"""

from dataclasses import dataclass
from typing import Optional


# Resolution steps from VideoFormat.properties
RESOLUTION_STEPS_W = [15360, 7680, 3840, 2560, 2040, 1920, 1280, 1024, 854, 720, 640, 640, 512, 320, 160]
RESOLUTION_STEPS_H = [8640, 4320, 2160, 1440, 1080, 1080, 720, 576, 576, 480, 480, 360, 240, 240, 120]

# Resolution names mapping
RESOLUTION_NAMES = {
    "7680x4320": "8K",
    "3840x2160": "4K",
    "2560x1440": "QHD",
    "2048x1080": "2K",
    "1920x1080": "FHD",
    "1280x720": "HD",
    "1024x576": "SD",
    "720x480": "SD",
    "640x360": "LD",
}


@dataclass
class VideoQuality:
    """Video quality information."""
    width: Optional[int] = None
    height: Optional[int] = None
    resolution: Optional[str] = None
    name: Optional[str] = None
    is_hdr: bool = False
    hdr_type: Optional[str] = None
    bit_depth: Optional[int] = None
    frame_rate: Optional[float] = None
    video_codec: Optional[str] = None
    audio_codec: Optional[str] = None
    audio_channels: Optional[str] = None

    @classmethod
    def from_resolution(cls, resolution: str) -> "VideoQuality":
        """Create VideoQuality from resolution string."""
        res_lower = resolution.lower().replace('p', '').replace('i', '')

        # Parse WxH format
        if 'x' in resolution.lower():
            parts = resolution.lower().split('x')
            width = int(parts[0])
            height = int(parts[1])
        else:
            # Assume height-only (e.g., "1080p")
            width = None
            height = int(res_lower)

        # Find matching resolution name
        name = cls._get_resolution_name(width, height)

        return cls(
            width=width,
            height=height,
            resolution=resolution,
            name=name,
        )

    @classmethod
    def _get_resolution_name(cls, width: Optional[int], height: Optional[int]) -> Optional[str]:
        """Get human-readable resolution name from dimensions."""
        if height is None and width is None:
            return None

        # Try exact match first
        if width and height:
            key = f"{width}x{height}"
            if key in RESOLUTION_NAMES:
                return RESOLUTION_NAMES[key]

        # Match by height
        if height:
            for i, h in enumerate(RESOLUTION_STEPS_H):
                if height >= h:
                    w = RESOLUTION_STEPS_W[i]
                    key = f"{w}x{h}"
                    return RESOLUTION_NAMES.get(key, f"{height}p")

        # Match by width
        if width:
            for i, w in enumerate(RESOLUTION_STEPS_W):
                if width >= w:
                    h = RESOLUTION_STEPS_H[i]
                    key = f"{w}x{h}"
                    return RESOLUTION_NAMES.get(key, f"{width}p")

        return f"{height or width}p"

    @property
    def vf(self) -> str:
        """Get video format string (e.g., '1080p', '720p')."""
        if self.name:
            return self.name
        if self.height:
            return f"{self.height}p"
        if self.width:
            return f"{self.width}p"
        return "SD"

    @property
    def source(self) -> str:
        """Get source type based on quality."""
        if self.name in ("8K", "4K"):
            return "UHD"
        if self.name in ("FHD", "2K", "QHD"):
            return "BD"
        if self.name == "HD":
            return "HDTV"
        return "SD"
