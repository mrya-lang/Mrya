from mrya_lexer import MryaLexer
from mrya_parser import MryaParser
from mrya_interpreter import MryaInterpreter
from mrya_errors import MryaRuntimeError

import argparse
import sys

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
    except Exception as e:
        # If your MryaParser raises custom parse errors, catch and print here.
        print(f"Parse error: {e}", file=sys.stderr)
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
    except MryaRuntimeError as err:
        # err.token.line assumed available; adjust if your error stores location differently.
        print(f"[Line {err.token.line}] Mrya runtime error: {err.message}", file=sys.stderr)
        sys.exit(1)

def run_repl(show_tokens=False, show_ast=False):
    """
    A simple REPL loop for Mrya. Reads from stdin until EOF or interruption.
    """
    interpreter = MryaInterpreter()
    print("Mrya REPL. Type your code; use Ctrl+D (Unix) / Ctrl+Z (Windows) to exit.")
    buffer = ""
    prompt = ">>> "
    try:
        while True:
            # Read one line at a time
            line = input(prompt)
            buffer += line + "\n"
            # You might want to detect end-of-statement (e.g., semicolon) before parsing.
            # For simplicity, attempt to parse every line or block:
            try:
                lexer = MryaLexer(buffer)
                tokens = lexer.scan_tokens()
                if show_tokens:
                    print("=== Tokens ===")
                    for token in tokens:
                        print(token)
                    print("==============")
                parser = MryaParser(tokens)
                statements = parser.parse()
                if show_ast:
                    print("=== AST ===")
                    for stmt in statements:
                        print(stmt)
                    print("============")
                interpreter.interpret(statements)
                # Clear buffer upon successful execution
                buffer = ""
                prompt = ">>> "
            except MryaRuntimeError as err:
                print(f"[Line {err.token.line}] Mrya runtime error: {err.message}", file=sys.stderr)
                # Clear buffer or keep? Here we clear to let user start fresh.
                buffer = ""
                prompt = ">>> "
            except Exception as e:
                # Parsing error or incomplete input?
                # If you want multi-line support, detect incomplete; here we simply print error and reset.
                print(f"Error: {e}", file=sys.stderr)
                buffer = ""
                prompt = ">>> "
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
