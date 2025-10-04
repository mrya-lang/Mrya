import argparse
import os

from mrya_lexer import MryaLexer
from mrya_parser import MryaParser, ParseError
from mrya_interpreter import MryaInterpreter, ReturnValue
from mrya_errors import MryaRuntimeError, MryaTypeError, LexerError

# -------------------------
# Argument parser setup
# -------------------------
parser = argparse.ArgumentParser(description="Run MRYA test suite.")
parser.add_argument("--no-tests", action="store_true", help="Skip running tests in the 'tests' folder.")
parser.add_argument("--no-packages", action="store_true", help="Skip running package tests in the 'packages' folder.")
args = parser.parse_args()

print("Starting MRYA test suite...")

# -------------------------
# Helper functions
# -------------------------
def color_text(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"

def run_file(filename, show_tokens=False, show_ast=False) -> bool:
    try:
        with open(filename, 'r') as file:
            source = file.read()
    except OSError:
        return False

    # Lexing
    try:
        lexer = MryaLexer(source)
        tokens = lexer.scan_tokens()
    except LexerError:
        return False

    # Parsing
    parser = MryaParser(tokens)
    try:
        statements = parser.parse()
    except ParseError:
        return False

    # Interpretation
    interpreter = MryaInterpreter()
    try:
        interpreter.set_current_directory(os.path.dirname(os.path.abspath(filename)))
        interpreter.interpret(statements)
    except ReturnValue:
        # A top-level return is not an error for a module file.
        return True
    except (MryaRuntimeError, MryaTypeError, LexerError, ParseError):
        return False

    return True

test_passed = 0
test_failed = 0
total_tests = 0

def test(file):
    global total_tests, test_passed, test_failed
    total_tests += 1
    passed = run_file(file)
    if passed:
        test_passed += 1
        print(f"{color_text('✅', '32')} Test {color_text(file, '36')} {color_text('passed.', '32')}")
    else:
        test_failed += 1
        print(f"{color_text('❌', '31')} Test {color_text(file, '36')} {color_text('failed.', '31')}")

# -------------------------
# Main logic
# -------------------------
if __name__ == "__main__":
    warnings = []

    if not args.no_tests:
        for file in os.walk("tests"):
            for f in file[2]:
                if f.endswith(".mrya"):
                    test(os.path.join(file[0], f))

    if not args.no_packages:
        for dat in os.walk("packages"):
            folder_path = dat[0]

            if folder_path == "packages":
                continue

            if os.path.exists(os.path.join(folder_path, "test.mrya")):
                test(os.path.join(folder_path, "test.mrya"))
            else:
                warnings.append(color_text(f"⚠️  Package: {folder_path} doesn't have test.mrya. This is recommended to add!", '93'))

    if len(warnings) != 0:
        print()
        for warning in warnings:
            print(warning)

    print(f"\nTest Summary: {color_text(str(test_passed), '32')}/{color_text(str(total_tests), '36')} tests passed, {color_text(str(test_failed), '31')} failed.")
