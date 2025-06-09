from mrya_lexer import MryaLexer

def run_klyr_file(filename):
	try:
		with open(filename, 'r') as file:
			source = file.read()
			lexer = MryaLexer(source)
			tokens = lexer.scan_tokens()
			for token in tokens:
				print(token)
	except FileNotFoundError:
		print(f"File '{filename}' not found.")

if __name__ == "__main__":
	run_klyr_file("examples/hello.mrya")