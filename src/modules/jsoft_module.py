import json
import re
from mrya_errors import MryaRuntimeError

def _convert_single_to_double_quotes(json_string):
    """
    Convert single-quoted strings in JSON-like input to double-quoted strings.
    This is a preprocessing step to allow single quotes as string delimiters.
    """
    # Regex to match single-quoted strings, handling escaped quotes inside
    # This regex matches a single quote, then any number of characters that are not unescaped single quotes,
    # allowing escaped single quotes inside, then a closing single quote.
    pattern = re.compile(r"(?<!\\\\)'((?:[^'\\\\]|\\\\.)*?)'")

    def replacer(match):
        inner = match.group(1)
        # Escape any double quotes inside the string
        inner_escaped = inner.replace('"', '\\"')
        return f'"{inner_escaped}"'

    return pattern.sub(replacer, json_string)

def parse(json_string):
    """Parses a JSON string into a Mrya map or list."""
    if not isinstance(json_string, str):
        raise MryaRuntimeError(None, "json.parse() expects a string argument.")
    try:
        # Preprocess to convert single-quoted strings to double-quoted strings
        preprocessed = _convert_single_to_double_quotes(json_string)
        return json.loads(preprocessed)
    except json.JSONDecodeError as e:
        raise MryaRuntimeError(None, f"Failed to parse jsoft: {e}")

def stringify(mrya_object, indent=None):
    """Converts a Mrya map or list into a JSON string."""
    try:
        final_indent = None
        if indent is not None:
            final_indent = int(indent) # Pretty-print
            separators = (',', ': ') # Standard pretty-print separators
        else:
            # Use compact separators when not pretty-printing
            separators = (',', ':')

        return json.dumps(mrya_object, indent=final_indent, separators=separators)
    except (TypeError, ValueError) as e:
        # This can happen with circular references, unsupported types, or invalid indent.
        raise MryaRuntimeError(None, f"Failed to stringify object to jsoft: {e}")
