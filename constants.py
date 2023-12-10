from element import Element
from intbase import InterpreterBase

# Simple values
FUNCTIONS = "functions"
VALUE = "val"
NAME = "name"
MAIN_FUNC_NAME = "main"
STATEMENTS = "statements"
ELSE_STATEMENTS = "else_statements"
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
OPERAND_1 = "op1"
OPERAND_2 = "op2"
ARGS = "args"
INPUTI = "inputi"
INPUTS = "inputs"
PRINT = "print"
CONDITION = "condition"
OBJREF = "objref"
PROTO = "proto"

# Binary Operators
BINARY_COMP = [
    EQUALS,
    NOT_EQUALS,
    LESS_THAN,
    LESS_THAN_EQUALS,
    GREATER_THAN,
    GREATER_THAN_EQUALS,
]
BINARY_ARITH = [ADD, SUBTRACT, MULTIPLY, DIVIDE]
BINARY_BOOL = [OR, AND]
BINARY_OPERATORS = BINARY_COMP + BINARY_ARITH + BINARY_BOOL

# Unary Operators
UNARY_OPERATORS = [InterpreterBase.NEG_DEF, InterpreterBase.NOT_DEF]

# All Operators
OPERATORS = BINARY_OPERATORS + UNARY_OPERATORS

# Types of different nodes
PRELOADED_FUNCS = [PRINT, INPUTI, INPUTS]

STATEMENT_TYPES = [
    ASSIGNMENT,
    InterpreterBase.FCALL_DEF,
    InterpreterBase.IF_DEF,
    InterpreterBase.WHILE_DEF,
    InterpreterBase.RETURN_DEF,
]

CONDITIONALS = [InterpreterBase.IF_DEF, InterpreterBase.WHILE_DEF]

EXPRESSION_TYPES = [InterpreterBase.FCALL_DEF] + OPERATORS

INPUT_TAKERS = [INPUTI, INPUTS]

VALUE_TYPES = [
    InterpreterBase.INT_DEF,
    InterpreterBase.STRING_DEF,
    InterpreterBase.BOOL_DEF,
    InterpreterBase.NIL_DEF,
]

ARG_TYPES = [InterpreterBase.ARG_DEF, InterpreterBase.REFARG_DEF]
