from intbase import InterpreterBase
from constants import *
from element import Element
import value
import binary_operator
import unary_operator
import function_def
import lambda_def
import assignment
import conditional
import return_type
import arg
import func_call
import variable


def convert_element(element, scope=None):
    if type(element) != Element:
        raise Exception(f"Expected Element, got {type(element)}")
    elem_type = element.elem_type
    if elem_type in VALUE_TYPES:
        return value.Value(element)
    if elem_type == InterpreterBase.FUNC_DEF:
        return function_def.FunctionDef(element)
    if elem_type in BINARY_OPERATORS:
        return binary_operator.BinaryOperator(scope, element)
    if elem_type in UNARY_OPERATORS:
        return unary_operator.UnaryOperator(scope, element)
    if elem_type in ARG_TYPES:
        return arg.Arg(element)
    if elem_type == InterpreterBase.LAMBDA_DEF:
        return lambda_def.LambdaDef(scope, element)
    if elem_type == ASSIGNMENT:
        return assignment.Assignment(scope, element)
    if elem_type in CONDITIONALS:
        return conditional.Conditional(
            scope, element, elem_type == InterpreterBase.WHILE_DEF
        )
    if elem_type == InterpreterBase.RETURN_DEF:
        return return_type.Return(scope, element)
    if elem_type == InterpreterBase.VAR_DEF:
        return variable.Variable(scope, element)
    if elem_type == InterpreterBase.FUNC_CALL:
        return func_call.FuncCall(scope, element)
    raise Exception(f"Unknown element type {elem_type}")
