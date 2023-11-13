from constants import *


class Arg:
    def __init__(self, element, trace_output=False):
        self.trace_output = trace_output
        self.__load_element(element)

    def __load_element(self, element):
        if self.trace_output:
            print(f"Loading element {str(element)}")
        if type(element) != Element:
            raise Exception(f"Expected Element, got {type(element)}")
        if element.elem_type == InterpreterBase.ARG_DEF:
            self.name = element.get(NAME)
            self.ref = False
        elif element.elem_type == InterpreterBase.REFARG_DEF:
            self.name = element.get(NAME)
            self.ref = True

    def get_name(self):
        return self.name

    def is_ref(self):
        return self.ref

    def evaluate(self):
        return self
