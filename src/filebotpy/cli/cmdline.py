"""
CmdlineOperations - Command-line interface for FileBotPy.

Based on FileBot's CmdlineOperations class.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from filebotpy.media.detector import AutoDetection, MediaType
from filebotpy.media.release_info import ReleaseInfoParser
from filebotpy.similarity.episode import SeasonEpisodeMatcher
from filebotpy.similarity.series import SeriesNameMatcher
from filebotpy.naming.engine import ExpressionFormat, FormatBindings
from filebotpy.naming.templates import NamingTemplates
from filebotpy.rename.action import MoveAction, CopyAction, HardlinkAction, SymlinkAction, RenameActionType
from filebotpy.rename.conflict import ConflictAction, ConflictResolver


class CmdlineOperations:
    """Command-line operations for FileBotPy."""

    def __init__(self):
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser."""
        parser = argparse.ArgumentParser(
            prog='filebotpy',
            description='FileBotPy - Media file renaming tool',
        )

        subparsers = parser.add_subparsers(dest='command', help='Available commands')

        # Rename command
        rename_parser = subparsers.add_parser('rename', help='Rename media files')
        rename_parser.add_argument('files', nargs='+', help='Files or directories to process')
        rename_parser.add_argument('--format', '-f', help='Custom format string')
        rename_parser.add_argument('--style', '-s', default='jellyfin',
                                  help='Naming style (default, jellyfin, plex, kodi, compact)')
        rename_parser.add_argument('--action', '-a', default='move',
                                  choices=['move', 'copy', 'hardlink', 'symlink'],
                                  help='Rename action (default: move)')
        rename_parser.add_argument('--conflict', '-c', default='auto',
                                  choices=['auto', 'overwrite', 'skip', 'fail'],
                                  help='Conflict resolution (default: auto)')
        rename_parser.add_argument('--output', '-o', help='Output directory')
        rename_parser.add_argument('--dry-run', '-n', action='store_true',
                                  help='Show what would be done without actually doing it')
        rename_parser.add_argument('--tvdb-api-key', help='TheTVDB API key')
        rename_parser.add_argument('--tmdb-api-key', help='TMDb API key')

        # Detect command
        detect_parser = subparsers.add_parser('detect', help='Detect media type')
        detect_parser.add_argument('files', nargs='+', help='Files to detect')

        # Parse command
        parse_parser = subparsers.add_parser('parse', help='Parse filename info')
        parse_parser.add_argument('files', nargs='+', help='Files to parse')

        return parser

    def run(self, args: Optional[List[str]] = None) -> int:
        """Run command-line operations."""
        parsed = self.parser.parse_args(args)

        if parsed.command is None:
            self.parser.print_help()
            return 0

        if parsed.command == 'rename':
            return self._cmd_rename(parsed)
        elif parsed.command == 'detect':
            return self._cmd_detect(parsed)
        elif parsed.command == 'parse':
            return self._cmd_parse(parsed)

        return 1

    def _cmd_rename(self, args) -> int:
        """Execute rename command."""
        # Collect files
        files = self._collect_files(args.files)
        if not files:
            print("No files found to process.")
            return 1

        # Get naming template
        if args.format:
            template = args.format
        else:
            # Determine template based on media type (default to TV)
            template = NamingTemplates.get_tv_template(args.style)

        # Create format engine
        formatter = ExpressionFormat(template)

        # Create rename action
        action_map = {
            'move': MoveAction(),
            'copy': CopyAction(),
            'hardlink': HardlinkAction(),
            'symlink': SymlinkAction(),
        }
        action = action_map.get(args.action, MoveAction())

        # Create conflict resolver
        conflict_map = {
            'auto': ConflictAction.AUTO_RENAME,
            'overwrite': ConflictAction.OVERWRITE,
            'skip': ConflictAction.SKIP,
            'fail': ConflictAction.FAIL,
        }
        resolver = ConflictResolver(conflict_map.get(args.conflict, ConflictAction.AUTO_RENAME))

        # Process each file
        processed = 0
        for file_path in files:
            result = self._process_file(
                file_path, formatter, action, resolver,
                output_dir=args.output,
                dry_run=args.dry_run,
            )
            if result:
                processed += 1

        print(f"\nProcessed {processed}/{len(files)} files.")
        return 0

    def _process_file(self, file_path: Path, formatter: ExpressionFormat,
                     action, resolver, output_dir: Optional[str] = None,
                     dry_run: bool = False) -> bool:
        """Process a single file."""
        # Detect media type
        media_type = AutoDetection.detect(file_path)
        if media_type == MediaType.UNKNOWN:
            print(f"  SKIP: {file_path.name} (unknown media type)")
            return False

        # Parse release info
        release_info = ReleaseInfoParser.parse(file_path.name)

        # Parse episode info
        episode_info = SeasonEpisodeMatcher.match(file_path.name)

        # Extract series name
        series_name = SeriesNameMatcher.extract_series_name(file_path.name)

        # Create bindings
        bindings = FormatBindings(
            n=series_name or release_info.title or file_path.stem,
            s=episode_info.episodes[0].season if episode_info and episode_info.episodes else None,
            e=episode_info.episodes[0].episode if episode_info and episode_info.episodes else None,
            y=release_info.year,
            vf=release_info.resolution or 'SD',
            cf=release_info.video_codec or '',
            af=release_info.audio_codec or '',
            ac=release_info.audio_channels or '',
            source=release_info.source or '',
            group=release_info.group or '',
            resolution=release_info.resolution or '',
            hdr=release_info.hdr or '',
            ext=file_path.suffix,
            fn=file_path.stem,
        )

        # Format new filename
        new_name = formatter.format(bindings)

        # Build destination path
        if output_dir:
            dest = Path(output_dir) / new_name / file_path.name
        else:
            dest = file_path.parent / new_name / file_path.name

        # Add extension if not present
        if not dest.suffix:
            dest = dest.with_suffix(file_path.suffix)

        # Resolve conflicts
        final_dest = resolver.get_final_path(file_path, dest)
        if final_dest is None:
            print(f"  SKIP: {file_path.name} (conflict - skip)")
            return False

        if dry_run:
            print(f"  DRY-RUN: {file_path.name}")
            print(f"    -> {final_dest}")
            return True

        # Execute rename
        result = action.execute(file_path, final_dest)
        if result.success:
            print(f"  OK: {file_path.name}")
            print(f"    -> {final_dest}")
            return True
        else:
            print(f"  ERROR: {file_path.name} - {result.error}")
            return False

    def _cmd_detect(self, args) -> int:
        """Execute detect command."""
        files = self._collect_files(args.files)
        for file_path in files:
            media_type = AutoDetection.detect(file_path)
            print(f"{file_path.name}: {media_type.value}")
        return 0

    def _cmd_parse(self, args) -> int:
        """Execute parse command."""
        for filename in args.files:
            path = Path(filename)
            release_info = ReleaseInfoParser.parse(path.name)
            episode_info = SeasonEpisodeMatcher.match(path.name)
            series_name = SeriesNameMatcher.extract_series_name(path.name)

            print(f"\n{path.name}:")
            print(f"  Series: {series_name or 'N/A'}")
            print(f"  Year: {release_info.year or 'N/A'}")
            print(f"  Resolution: {release_info.resolution or 'N/A'}")
            print(f"  Video Codec: {release_info.video_codec or 'N/A'}")
            print(f"  Audio Codec: {release_info.audio_codec or 'N/A'}")
            print(f"  Source: {release_info.source or 'N/A'}")
            print(f"  Group: {release_info.group or 'N/A'}")

            if episode_info:
                for ep in episode_info.episodes:
                    print(f"  Episode: S{ep.season:02d}E{ep.episode:02d}")
            else:
                print(f"  Episode: N/A")

        return 0

    @staticmethod
    def _collect_files(paths: List[str]) -> List[Path]:
        """Collect files from paths (files or directories)."""
        files = []
        for path_str in paths:
            path = Path(path_str)
            if path.is_file():
                files.append(path)
            elif path.is_dir():
                # Recursively collect media files
                for ext in ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg', '.m2ts', '.ts']:
                    files.extend(path.rglob(f'*{ext}'))
                    files.extend(path.rglob(f'*{ext.upper()}'))

        return sorted(set(files))


def main():
    """Main entry point."""
    ops = CmdlineOperations()
    sys.exit(ops.run())


if __name__ == '__main__':
    main()
