from element import Element
from value import Value
from constants import *
import convert_element
from intbase import InterpreterBase
from intbase import ErrorType


class UnaryOperator:
    def __init__(self, scope, element, trace_output=False):
        self.scope = scope
        self.trace_output = trace_output
        self.__load_element(element)

    def __load_element(self, element):
        if self.trace_output:
            print(f"Loading element {str(element)}")
        if type(element) != Element:
            raise Exception(f"Expected Element, got {type(element)}")
        self.type = element.elem_type
        if not self.type in UNARY_OPERATORS:
            raise Exception(f"Unknown element type {self.type}")
        self.value = convert_element.convert_element(element.get(OPERAND_1), self.scope)

    def evaluate(self):
        if self.trace_output:
            print(f"Evaluating {str(self)}")
        self.value = self.value.evaluate()
        if self.type == InterpreterBase.NOT_DEF:
            return self.__eval_not()
        elif self.type == InterpreterBase.NEG_DEF:
            return self.__eval_neg()

    def __eval_not(self):
        value = self.value
        if self.value.get_type() == InterpreterBase.INT_DEF:
            value = self.value.converted_type(InterpreterBase.BOOL_DEF)
        elif self.value.get_type() != InterpreterBase.BOOL_DEF:
            self.scope.error(
                ErrorType.TYPE_ERROR,
                "Cannot perform boolean operations on non-boolean values",
            )
        if value:
            return Value(not value.get_val())

    def __eval_neg(self):
        val_type = self.value.get_type()
        if val_type == InterpreterBase.INT_DEF:
            return Value(-self.value.get_val())
        self.scope.error(ErrorType.TYPE_ERROR, "Cannot negate non-integers")

    def __str__(self):
        return f"UnaryOperator({self.type}, {str(self.value)})"
