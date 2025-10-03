from enum import Enum, auto

class TokenType(Enum):
	# Single character tokens
	LEFT_PAREN = auto()
	RIGHT_PAREN = auto()
	LEFT_BRACE = auto()
	RIGHT_BRACE = auto()
	COMMA = auto()
	DOT = auto()
	MINUS = auto()
	PLUS = auto()
	COLON = auto()
	SEMICOLON = auto()
	SLASH = auto()
	STAR = auto()
	EQUAL = auto()
	BANG = auto()
	LESS = auto()
	GREATER = auto()
	FUNC = auto()
	LEFT_BRACKET = auto()
	RIGHT_BRACKET = auto()

	#One or two character tokens
	EQUAL_EQUAL = auto()
	BANG_EQUAL = auto()
	LESS_EQUAL = auto()
	GREATER_EQUAL = auto()

	#Literals
	IDENTIFIER = auto()
	STRING = auto()
	NUMBER = auto()

	#Keywords
	LET = auto()
	FUNCTION = auto()
	RETURN = auto()
	IF = auto()
	WHILE = auto()
	ELSE = auto()
	TRUE = auto()
	FALSE = auto()
	OUTPUT = auto()
	INPUT = auto()
	DEFINE = auto()
	AND = auto()
	OR = auto()
	FOR = auto()
	CONST = auto()
	IN = auto()
	BREAK = auto()
	CONTINUE = auto()
	IMPORT = auto()
	USING = auto()

	AS = auto()
	#End of .klyr File
	EOF = auto()


class Token:
	def __init__(self, type: TokenType, lexeme: str, literal, line: int):
		self.type = type 
		self.lexeme = lexeme
		self.literal = literal
		self.line	= line	

	def __repr__(self):
		return f'{self.type.name} {self.lexeme} {self.literal}'
		