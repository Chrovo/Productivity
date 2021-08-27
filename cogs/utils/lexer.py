from rply import LexerGenerator

# lexer for the "calc" command
lg = LexerGenerator()

lg.add('NUMBER', r'[0-9]+[\.]?[0-9]*') # number token

lg.add('ADDITION', r'\+') # operator tokens
lg.add('SUBTRACTION', r'-')
lg.add('MULTIPLICATION', r'\*')
lg.add('EXPONENT', r'\^')
lg.add('DIVISION', r'\/')

lg.add('FIRST_BRACKETS', r'\[') # grouping tokens
lg.add('SECOND_BRACKETS', r'\]')
lg.add('FIRST_BRACES', r'\{')
lg.add('SECOND_BRACES', r'\}')
lg.add('FIRST_PARENTHESIS', r'\(')
lg.add('SECOND_PARENTHESIS', r'\)')

lg.ignore('\s+') # ignore whitespace

l = lg.build()
