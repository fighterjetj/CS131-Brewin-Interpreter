from constants import *
from element import Element
from intbase import InterpreterBase


class Variable:
    def __init__(self, scope, element, trace_output=False):
        self.trace_output = trace_output
        self.scope = scope
        self.__load_element(element)

    def __load_element(self, element):
        if type(element) != Element or element.elem_type != InterpreterBase.VAR_DEF:
            raise Exception(f"Expected Variable Element, got {type(element)}")
        self.name = element.get(NAME)

    def get_name(self):
        return self.name

    def get_ref(self):
        return self.scope.get_ref_var(self.name)

    def get_type(self):
        return InterpreterBase.VAR_DEF

    def evaluate(self):
        if self.trace_output:
            print(f"Evaluating {str(self)}")
        return self.scope.get_var(self.name)
