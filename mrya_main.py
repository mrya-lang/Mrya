from mrya_lexer import MryaLexer
from mrya_parser import MryaParser
from mrya_interpreter import MryaInterpreter
from mrya_errors import MryaRuntimeError

def run_file(filename):
	with open(filename, 'r') as file:
		source = file.read()

	lexer = MryaLexer(source)
	tokens = lexer.scan_tokens()

	parser = MryaParser(tokens)
	try:
		statements = parser.parse()
		interpreter = MryaInterpreter()
		interpreter.interpret(statements)
	except MryaRuntimeError as err:
		print(f"[Line {err.token.line}] Mrya runtime error: {err.message}")

if __name__ == "__main__":
	run_file("examples/hello.mrya")