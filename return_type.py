from value import Value
from copy import deepcopy
from element import Element
from intbase import InterpreterBase
from constants import *
import convert_element


class Return:
    def __init__(self, scope, element, trace_output=False):
        self.scope = scope
        self.trace_output = trace_output
        self.__load_element(element)

    def __load_element(self, element):
        if self.trace_output:
            print(f"Loading element {str(element)}")
        if type(element) != Element or element.elem_type != InterpreterBase.RETURN_DEF:
            raise Exception(f"Expected Element, got {type(element)}")
        to_return = element.get(EXPRESSION)
        if to_return is None:
            self.value = Value(None)
        else:
            self.value = convert_element.convert_element(
                element.get(EXPRESSION), self.scope
            )

    def get_val(self):
        return self.value.evaluate()

    def evaluate(self):
        return self

    def __str__(self):
        return f"Return({str(self.value)})"
