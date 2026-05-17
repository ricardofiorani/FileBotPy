# FileBotPy

![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)

A Python clone of FileBot's media renaming feature. Provides automated detection, matching, and renaming of TV shows and movies with Jellyfin-compatible naming formats.

## Features

- **Automatic media detection** - Identifies TV shows and movies from file/folder names
- **Online database matching** - Queries TMDB and TheTVDB for accurate metadata
- **Similarity matching** - Fuzzy matching to handle imperfect file names
- **Customizable naming formats** - Supports multiple naming styles and custom format strings
- **CLI and GUI modes** - Use from the command line or with a PyQt6 graphical interface
- **Jellyfin-compatible** - Output formats work seamlessly with Jellyfin media server

## Installation

### Using uv (recommended)

```bash
uv pip install .
```

### Using pip

```bash
pip install .
```

### Development setup

```bash
uv venv
uv pip install -e ".[dev]"
```

## Usage

### CLI Mode

```bash
# Rename files using the default format
filebotpy rename /path/to/media/

# Specify a custom naming format
filebotpy rename /path/to/media/ --format "{n} - {s00e00} - {t}"

# Detect media without renaming
filebotpy detect /path/to/media/

# Parse file names and show results
filebotpy parse /path/to/media/
```

### GUI Mode

```bash
# Launch the graphical interface
filebotpy-gui

# Or using the main script
python main.py --gui
```

### Direct script execution

```bash
python main.py rename /path/to/media/
python main.py --gui
```

## Project Structure

```
FileBotPy/
├── main.py              # Entry point (CLI/GUI dispatcher)
├── pyproject.toml       # Package configuration
└── src/
   └── filebotpy/
       ├── cli/         # Command-line interface
       ├── gui/         # PyQt6 graphical interface
       ├── media/       # Media file detection and parsing
       ├── naming/      # Naming engine and format processing
       ├── rename/      # Rename action execution
       ├── similarity/  # Fuzzy matching algorithms
       └── web/         # API clients (TMDB, TheTVDB)
```

## License

This project is a Python clone of FileBot's renaming functionality. FileBot is a trademark of FileBot Ltd. This project is not affiliated with or endorsed by FileBot Ltd.
