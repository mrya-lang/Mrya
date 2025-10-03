from mrya_lexer import MryaLexer
from mrya_parser import MryaParser, ParseError
from mrya_interpreter import MryaInterpreter
from mrya_errors import MryaRuntimeError, MryaTypeError

import argparse
import sys

# Enable command history and line editing in the REPL if readline is available.
try:
    import readline
except ImportError:
    # This is expected on Windows. For a better experience, users can `pip install pyreadline3`.
    pass

def _print_error_context(source_code, error):
    """Prints a helpful, context-rich error message."""
    if not hasattr(error, 'token') or not error.token:
        print(f"Error: {error.message}", file=sys.stderr)
        return

    line_num = error.token.line
    error_line = source_code.splitlines()[line_num - 1]
    
    # Calculate the position of the arrow, accounting for leading whitespace
    # This is a simplified column calculation. A real-world implementation would handle tabs.
    col = error.token.lexeme.find(error.token.lexeme)
    # Find the start of the token in the line
    start_col = error_line.find(error.token.lexeme)
    if start_col == -1: start_col = 0 # Fallback

    print(f"\n[Line {line_num}] {type(error).__name__}: {error.message}", file=sys.stderr)
    print(f"  {line_num} | {error_line}", file=sys.stderr)
    print(f"    | {' ' * start_col}{'^' * len(error.token.lexeme)}", file=sys.stderr)

def run_file(filename, show_tokens=False, show_ast=False):
    """
    Run a Mrya source file.
    - filename: path to the .mrya file.
    - show_tokens: if True, print out the tokens from the lexer.
    - show_ast: if True, print out a representation of the parsed statements (AST).
    """
    try:
        with open(filename, 'r') as file:
            source = file.read()
    except OSError as e:
        print(f"Error: could not open file '{filename}': {e}", file=sys.stderr)
        sys.exit(1)

    # Lexing
    lexer = MryaLexer(source)
    tokens = lexer.scan_tokens()
    if show_tokens:
        print("=== Tokens ===")
        for token in tokens:
            print(token)
        print("==============")

    # Parsing
    parser = MryaParser(tokens)
    try:
        statements = parser.parse()
    except ParseError as e:
        _print_error_context(source, e)
        sys.exit(1)

    if show_ast:
        # Assuming your parser.parse() returns some AST representation with a __str__ or similar.
        # Adjust according to your AST node classes.
        print("=== AST / Parsed Statements ===")
        # You might want to pretty-print; here we just do a naive print().
        for stmt in statements:
            print(stmt)
        print("================================")

    # Interpretation
    interpreter = MryaInterpreter()
    try:
        interpreter.interpret(statements)
    except (MryaRuntimeError, MryaTypeError, ) as err:
        _print_error_context(source, err)
        sys.exit(1)

def run_repl(show_tokens=False, show_ast=False):
    """
    A simple REPL loop for Mrya. Reads from stdin until EOF or interruption.
    """
    interpreter = MryaInterpreter()
    print("Mrya REPL. Type your code; use Ctrl+D (Unix) / Ctrl+Z (Windows) to exit.")
    code_buffer = ""
    try:
        while True:
            prompt = ">>> " if not code_buffer else "... "
            line = input(prompt)

            if line.strip().endswith("\\"):
                # Continue building the multi-line block
                code_buffer += line.rstrip("\\") + "\n"
                continue
            else:
                # Line does not end with '\', so we execute
                code_buffer += line + "\n"

            try:
                if not code_buffer.strip(): # Ignore empty input
                    code_buffer = ""
                    continue

                lexer = MryaLexer(code_buffer)
                tokens = lexer.scan_tokens()
                parser = MryaParser(tokens)
                statements = parser.parse()

                interpreter.interpret(statements)

            except (MryaRuntimeError, MryaTypeError) as err:
                _print_error_context(code_buffer, err)
            except ParseError as e:
                _print_error_context(code_buffer, e)
            finally:
                # Reset buffer after every execution attempt
                code_buffer = ""

    except (EOFError, KeyboardInterrupt):
        print("\nExiting Mrya REPL.")
        return

def main():

    parser = argparse.ArgumentParser(
        description="Run Mrya source files or start a REPL."
    )
    parser.add_argument(
        "source",
        nargs="?",
        help="Path to a .mrya source file. If omitted, starts REPL."
    )
    parser.add_argument(
        "-t", "--tokens",
        action="store_true",
        dest="show_tokens",
        help="Print tokens produced by the lexer."
    )
    parser.add_argument(
        "-a", "--ast",
        action="store_true",
        dest="show_ast",
        help="Print AST (parsed statements) before interpretation."
    )
    # You can add more options as needed, e.g., verbose, debug flags, etc.
    args = parser.parse_args()

    if args.source:
        run_file(args.source, show_tokens=args.show_tokens, show_ast=args.show_ast)
    else:
        run_repl(show_tokens=args.show_tokens, show_ast=args.show_ast)

if __name__ == "__main__":
    main()
