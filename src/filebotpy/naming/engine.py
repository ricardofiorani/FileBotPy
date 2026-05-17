"""
ExpressionFormat - Expression-based naming format engine.

Based on FileBot's ExpressionFormat class. Supports Groovy-like
expression syntax for flexible naming formats.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional


@dataclass
class FormatBindings:
    """Container for format bindings."""
    n: Optional[str] = None  # Series/Movie name
    name: Optional[str] = None  # Alias for n
    s: Optional[int] = None  # Season number
    season: Optional[int] = None  # Alias for s
    e: Optional[int] = None  # Episode number
    episode: Optional[int] = None  # Alias for e
    t: Optional[str] = None  # Episode title
    title: Optional[str] = None  # Alias for t
    y: Optional[int] = None  # Year
    year: Optional[int] = None  # Alias for y
    c: Optional[int] = None  # CD/part number
    fn: Optional[str] = None  # Original filename
    ext: Optional[str] = None  # File extension
    vf: Optional[str] = None  # Video format (1080p, 720p, etc.)
    cf: Optional[str] = None  # Video codec (x264, x265, etc.)
    af: Optional[str] = None  # Audio format (AAC, AC3, etc.)
    ac: Optional[str] = None  # Audio channels (5.1, 7.1, etc.)
    source: Optional[str] = None  # Source (BluRay, WEB-DL, etc.)
    group: Optional[str] = None  # Release group
    resolution: Optional[str] = None  # Resolution
    hdr: Optional[str] = None  # HDR type
    languages: Optional[str] = None  # Languages
    subs: Optional[str] = None  # Subtitles

    def get(self, key: str) -> Any:
        """Get binding value by key."""
        alias_map = {
            'n': 'n', 'name': 'n',
            's': 's', 'season': 's',
            'e': 'e', 'episode': 'e',
            't': 't', 'title': 't',
            'y': 'y', 'year': 'y',
            'c': 'c',
            'fn': 'fn',
            'ext': 'ext',
            'vf': 'vf',
            'cf': 'cf',
            'af': 'af',
            'ac': 'ac',
            'source': 'source',
            'group': 'group',
            'resolution': 'resolution',
            'hdr': 'hdr',
            'languages': 'languages',
            'subs': 'subs',
        }
        return getattr(self, alias_map.get(key, key), None)


class ExpressionFormat:
    """Expression-based format engine.

    Supports Groovy-like expression syntax:
    - Simple bindings: {n}, {s}, {e}, {t}
    - Formatted: {s00}, {e00}
    - Conditional: {t} or {fn}
    - Transformations: {n.replaceAll(' ', '.')}
    """

    # Built-in functions for expressions
    FUNCTIONS: Dict[str, Callable] = {
        'lower': lambda s: s.lower() if s else '',
        'upper': lambda s: s.upper() if s else '',
        'title': lambda s: s.title() if s else '',
        'space': lambda s: s.replace('.', ' ').replace('_', ' ') if s else '',
        'dot': lambda s: s.replace(' ', '.').replace('_', '.') if s else '',
        'underscore': lambda s: s.replace(' ', '_').replace('.', '_') if s else '',
        'left': lambda s, n: s[:n] if s else '',
        'right': lambda s, n: s[-n:] if s else '',
        'replaceAll': lambda s, pattern, replacement: re.sub(pattern, replacement, s) if s else '',
        'replaceFirst': lambda s, pattern, replacement: re.sub(pattern, replacement, s, count=1) if s else '',
        'truncate': lambda s, n: s[:n] if s and len(s) > n else s or '',
    }

    def __init__(self, template: str):
        """Initialize with a format template string."""
        self.template = template
        self._parsed = self._parse_template(template)

    def format(self, bindings: FormatBindings) -> str:
        """Format the template with given bindings."""
        result = self._apply_bindings(bindings)

        # Clean up the result
        result = self._cleanup(result)

        return result

    def _parse_template(self, template: str) -> list:
        """Parse template into segments."""
        segments = []
        pattern = re.compile(r'\{([^}]+)\}')
        last_end = 0

        for match in pattern.finditer(template):
            # Add literal text before this match
            if match.start() > last_end:
                segments.append(('literal', template[last_end:match.start()]))

            # Add binding expression
            expr = match.group(1).strip()
            segments.append(('expression', expr))
            last_end = match.end()

        # Add remaining literal text
        if last_end < len(template):
            segments.append(('literal', template[last_end:]))

        return segments

    def _apply_bindings(self, bindings: FormatBindings) -> str:
        """Apply bindings to parsed template."""
        result = []

        for seg_type, seg_value in self._parsed:
            if seg_type == 'literal':
                result.append(seg_value)
            elif seg_type == 'expression':
                value = self._evaluate_expression(seg_value, bindings)
                if value is not None:
                    result.append(str(value))

        return ''.join(result)

    def _evaluate_expression(self, expr: str, bindings: FormatBindings) -> Optional[str]:
        """Evaluate a single expression."""
        # Check for function calls: {n.lower()}
        func_match = re.match(r'^(\w+)\.(\w+)\(([^)]*)\)$', expr)
        if func_match:
            binding = func_match.group(1)
            func_name = func_match.group(2)
            func_args = func_match.group(3)

            value = bindings.get(binding)
            if value is None:
                return None

            if func_name in self.FUNCTIONS:
                args = [a.strip().strip("'\"") for a in func_args.split(',') if a.strip()]
                try:
                    return self.FUNCTIONS[func_name](value, *args)
                except (TypeError, ValueError):
                    return str(value)

        # Check for formatted numbers: {s00}, {e00}, {s000}
        # Pattern: letter followed by digits (e.g., s00 -> s with width 2)
        num_match = re.match(r'^([a-zA-Z])(0+)$', expr)
        if num_match:
            binding = num_match.group(1)
            width = len(num_match.group(2))  # Number of zeros = width

            value = bindings.get(binding)
            if value is not None:
                try:
                    return str(int(value)).zfill(width)
                except (ValueError, TypeError):
                    return str(value)

        # Simple binding: {n}, {s}, {e}, {t}
        value = bindings.get(expr)
        if value is not None:
            return str(value)

        return None

    def _cleanup(self, result: str) -> str:
        """Clean up the formatted result."""
        # Remove trailing/leading whitespace and dots
        result = result.strip()

        # Remove multiple consecutive spaces
        result = re.sub(r' {2,}', ' ', result)

        # Remove trailing/leading dots
        result = result.strip('.')

        return result

    def __repr__(self) -> str:
        return f"ExpressionFormat('{self.template}')"
