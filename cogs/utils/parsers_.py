from typing import Union

from rply import ParserGenerator
from rply.token import BaseBox

# the Abstract Syntax Tree for it, it uses polymorphism

class Number(BaseBox):
    def __init__(self, value):
        self.value = value

    def _eval(self) -> Union[int, float]:
        return self.value

class Op(BaseBox):
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Add(Op):
    def _eval(self) -> Union[int, float]:
        return self.left._eval() + self.right._eval()

class Sub(Op):
    def _eval(self) -> Union[int, float]:
        return self.left._eval() - self.right._eval()

class Mul(Op):
    def _eval(self) -> Union[int, float]:
        return self.left._eval() * self.right._eval()

class Div(Op):
    def _eval(self) -> Union[int, float]:
        return self.left._eval() / self.right._eval()

class Exponent(Op):
    """AST for exponent token"""

    def _eval(self) -> Union[int, float]:
        return self.left._eval()**self.right._eval()

pg = ParserGenerator(
    [
        'NUMBER', 
        'ADDITION', 
        'SUBTRACTION', 
        'MULTIPLICATION', 
        'EXPONENT', 
        'DIVISION', 
        'FIRST_BRACKETS', 
        'SECOND_BRACKETS', 
        'FIRST_PARENTHESIS', 
        'SECOND_PARENTHESIS', 
        'FIRST_BRACES', 
        'SECOND_BRACES',
        ],
        precedence=[
            ('left', [
                'FIRST_PARENTHESIS', 'SECOND_PARENTHESIS', 
                'FIRST_BRACKETS', 'SECOND_BRACKETS', 
                'FIRST_BRACES', 'SECOND_BRACES',
                ]
                ),
            ('left', ['ADDITION', 'SUBTRACTION']),
            ('left', ['EXPONENT','MULTIPLICATION', 'DIVISION']),
        ]
    )

@pg.production('expression : NUMBER')
def return_numbers(p) -> Union[int, float]:
    return Number(float(p[0].getstr()))

@pg.production('expression : FIRST_PARENTHESIS expression SECOND_PARENTHESIS')
@pg.production('expression : FIRST_BRACKETS expression SECOND_BRACKETS')
@pg.production('expression : FIRST_BRACES expression SECOND_BRACES')
def expression_parens(p):
    return p[1]

@pg.production('expression : expression ADDITION expression')
@pg.production('expression : expression SUBTRACTION expression')
@pg.production('expression : expression MULTIPLICATION expression')
@pg.production('expression : expression DIVISION expression')
@pg.production('expression : expression EXPONENT expression')
def expression_parser(p) -> Union[int, float]:
    left, right = p[0], p[2] # the numbers to the left and right of the operator

    ALL_ASTS = {
        'ADDITION':Add(left, right),
        'SUBTRACTION':Sub(left, right),
        'MULTIPLICATION':Mul(left, right),
        'DIVISION':Div(left, right),
        'EXPONENT':Exponent(left, right),
        }
    
    if p[1].gettokentype() in ALL_ASTS.keys(): 
        output = ALL_ASTS[p[1].gettokentype()]
        return output

    return None

parser = pg.build()
