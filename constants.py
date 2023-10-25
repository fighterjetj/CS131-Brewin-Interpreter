from element import Element
from intbase import InterpreterBase

FUNCTIONS = "functions"
VALUE = "val"
NAME = "name"
MAIN_FUNC_NAME = "main"
STATEMENT = "statements"
EXPRESSION = "expression"
ASSIGNMENT = "="
ADD = "+"
SUBTRACT = "-"
MULTIPLY = "*"
DIVIDE = "/"
EQUALS = "=="
NOT_EQUALS = "!="
LESS_THAN = "<"
LESS_THAN_EQUALS = "<="
GREATER_THAN = ">"
GREATER_THAN_EQUALS = ">="
OR = "||"
AND = "&&"
BINARY_INT_OPERATORS = [ADD, SUBTRACT, MULTIPLY, DIVIDE]
COMPARISON_INT_OPERATORS = [EQUALS, NOT_EQUALS, LESS_THAN, LESS_THAN_EQUALS, GREATER_THAN, GREATER_THAN_EQUALS]
UNARY_INT_OPERATORS = [InterpreterBase.NEG_DEF]
BINARY_BOOL_OPERATORS = [OR, AND]
COMPARISON_BOOL_OPERATORS = [EQUALS, NOT_EQUALS]
UNARY_BOOL_OPERATORS = [InterpreterBase.NOT_DEF]
BINARY_STRING_OPERATORS = [ADD]
COMPARISON_STRING_OPERATORS = [EQUALS, NOT_EQUALS]
UNARY_STRING_OPERATORS = []
BINARY_OPERATORS = BINARY_INT_OPERATORS + BINARY_BOOL_OPERATORS + BINARY_STRING_OPERATORS
COMPARSION_OPERATORS = COMPARISON_INT_OPERATORS + COMPARISON_BOOL_OPERATORS + COMPARISON_STRING_OPERATORS
UNARY_OPERATORS = UNARY_INT_OPERATORS + UNARY_BOOL_OPERATORS + UNARY_STRING_OPERATORS
OPERATORS = BINARY_OPERATORS + UNARY_OPERATORS
OPERAND_1 = "op1"
OPERAND_2 = "op2"
ARGS = "args"
INPUTI = "inputi"
INPUTS = "inputs"
PRINT = "print"
PRELOADED_FUNCS = [PRINT, INPUTI, INPUTS]
STATEMENT_TYPES = [ASSIGNMENT, InterpreterBase.FCALL_DEF, InterpreterBase.IF_DEF, InterpreterBase.WHILE_DEF, InterpreterBase.RETURN_DEF]
STATEMENT_TYPES += PRELOADED_FUNCS
EXPRESSION_TYPES = [InterpreterBase.FCALL_DEF] + OPERATORS
VALUE_TYPES = [InterpreterBase.INT_DEF, InterpreterBase.STRING_DEF, InterpreterBase.BOOL_DEF, InterpreterBase.NIL_DEF]
NIL_VAL = Element(InterpreterBase.NIL_DEF)