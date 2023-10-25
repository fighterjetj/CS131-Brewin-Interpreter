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
OPERAND_1 = "op1"
OPERAND_2 = "op2"
ARGS = "args"
STATEMENT_TYPES = [ASSIGNMENT, InterpreterBase.FCALL_DEF, InterpreterBase.IF_DEF, InterpreterBase.WHILE_DEF, InterpreterBase.RETURN_DEF]
EXPRESSION_TYPES = [InterpreterBase.FCALL_DEF, ADD, SUBTRACT]
VALUE_TYPES = [InterpreterBase.INT_DEF, InterpreterBase.STRING_DEF]
INPUT = "inputi"
PRINT = "print"
PRELOADED_FUNCS = [PRINT, INPUT]