"""Media detection and analysis module."""

from filebotpy.media.detector import AutoDetection
from filebotpy.media.release_info import ReleaseInfo
from filebotpy.media.video_quality import VideoQuality
from filebotpy.media.clutter_filter import ClutterFileFilter

__all__ = [
    "AutoDetection",
    "ReleaseInfo",
    "VideoQuality",
    "ClutterFileFilter",
]
