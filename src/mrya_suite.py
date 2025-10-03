from mrya_lexer import MryaLexer
from mrya_parser import MryaParser, ParseError
from mrya_interpreter import MryaInterpreter
from mrya_errors import MryaRuntimeError, MryaTypeError, LexerError

import os

print("Starting MRYA test suite...")

def run_file(filename, show_tokens=False, show_ast=False) -> bool:
    try:
        with open(filename, 'r') as file:
            source = file.read()
    except OSError as e:
        return False

    # Lexing
    try:
        lexer = MryaLexer(source)
        tokens = lexer.scan_tokens()
    except LexerError as e:
        return False
    
    # Parsing
    parser = MryaParser(tokens)
    try:
        statements = parser.parse()
    except ParseError as e:
        return False

    # Interpretation
    interpreter = MryaInterpreter()
    try:
        interpreter.interpret(statements)
    except (MryaRuntimeError, MryaTypeError) as err:
        return False
    
    return True

test_passed = 0
test_failed = 0
total_tests = 0

def color_text(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"

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

if __name__ == "__main__":
    for file in os.walk("tests"):
        for f in file[2]:
            if f.endswith(".mrya"):
                test(os.path.join(file[0], f))

    print(f"\nTest Summary: {color_text(str(test_passed), '32')}/{color_text(str(total_tests), '36')} tests passed, {color_text(str(test_failed), '31')} failed.")