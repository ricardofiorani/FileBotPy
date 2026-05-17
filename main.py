"""
FileBotPy - A Python implementation of FileBot's renaming feature.

Reverse engineered from FileBot 5.2.1 to provide media detection,
matching, and renaming with Jellyfin-compatible naming formats.

Usage:
    python main.py --gui
    python main.py rename <files> [--format FORMAT] [--style STYLE]
    python main.py detect <files>
    python main.py parse <files>
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent / "src"))


def main():
    if "--gui" in sys.argv:
        sys.argv.remove("--gui")
        from filebotpy.gui import launch_gui
        launch_gui()
    else:
        from filebotpy.cli.cmdline import main as cli_main
        cli_main()


if __name__ == "__main__":
    main()
