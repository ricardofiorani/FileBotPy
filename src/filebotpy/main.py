"""FileBotPy - Main entry point."""

import sys
import argparse


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="FileBotPy - Media file renamer")
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch GUI instead of CLI",
    )
    args = parser.parse_args()

    if args.gui:
        from filebotpy.gui import launch_gui
        launch_gui()
    else:
        from filebotpy.cli.cmdline import main as cli_main
        cli_main()


if __name__ == "__main__":
    main()
