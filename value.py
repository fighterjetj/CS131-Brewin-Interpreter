from element import Element
from intbase import InterpreterBase
from constants import *
from copy import deepcopy


class Value:
    def __init__(self, element, trace_output=False):
        self.trace_output = trace_output
        self.__load_element(element)

    def __load_element(self, element):
        # Checking if we have been passed a raw value or an element object
        if type(element) == Element:
            if self.trace_output:
                print(f"Loading element {str(element)}")
            self.type = element.elem_type
            if self.type == InterpreterBase.INT_DEF:
                self.value = int(element.get(VALUE))
            elif self.type == InterpreterBase.BOOL_DEF:
                self.value = element.get(VALUE)
            elif self.type == InterpreterBase.STRING_DEF:
                self.value = element.get(VALUE)
            elif self.type == InterpreterBase.NIL_DEF:
                self.value = None
            else:
                raise Exception(f"Unknown element type {self.type}")
        elif type(element) == Value:
            if self.trace_output:
                print(f"Loading value {str(element)}")
            self.value = element.get_val()
            self.type = element.get_type()
        else:
            if self.trace_output:
                print(f"Loading raw value {element}")
            self.value = element
            if type(element) == int:
                self.type = InterpreterBase.INT_DEF
            elif type(element) == bool:
                self.type = InterpreterBase.BOOL_DEF
            elif type(element) == str:
                self.type = InterpreterBase.STRING_DEF
            elif element == None:
                self.type = InterpreterBase.NIL_DEF
            else:
                raise Exception(f"Unknown raw value type {type(element)}")

    def get_val(self):
        return self.value

    def get_type(self):
        return self.type

    def set_val(self, element):
        self.__load_element(element)

    def evaluate(self):
        return self

    def converted_type(self, type):
        if type == self.type:
            return self
        if type == InterpreterBase.INT_DEF:
            if self.type == InterpreterBase.BOOL_DEF:
                return Value(1 if self.value else 0)
        if type == InterpreterBase.BOOL_DEF:
            if self.type == InterpreterBase.INT_DEF:
                return Value(self.value != 0)
        return None

    def copy(self):
        return deepcopy(self)

    def __str__(self):
        return f"Value({self.value} of type {self.type})"
