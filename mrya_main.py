import sys

from mrya_lexer import MryaLexer
from mrya_parser import MryaParser
from mrya_interpreter import MryaInterpreter

def run_file(filepath):
	try:
		with open(filepath, "r") as f:
			source = f.read()
	except FileNotFoundError:
		print(f"File {filepath} not found.")
		return

	lexer = MryaLexer(source)
	tokens = lexer.scan_tokens()

	parser = MryaParser(tokens)
	statements = parser.parse()

	interpreter = MryaInterpreter()
	interpreter.interpret(statements)

if __name__ == "__main__":
	run_file("examples/hello.mrya")