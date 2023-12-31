from element import Element
from constants import *
import convert_element
from intbase import ErrorType


class Assignment:
    def __init__(self, scope, element, trace_output=False):
        self.scope = scope
        self.trace_output = trace_output
        self.__load_element(element)

    def __load_element(self, element):
        if self.trace_output:
            print(f"Loading element {str(element)}")
        if type(element) != Element or element.elem_type != ASSIGNMENT:
            raise Exception(f"Expected Element, got {type(element)}")
        self.name = element.get(NAME)
        self.value = convert_element.convert_element(
            element.get(EXPRESSION), self.scope
        )

    def evaluate(self):
        if self.trace_output:
            print(f"Evaluating {str(self)}")
        self.value = self.value.evaluate()
        if "." in self.name:
            name, field = self.name.split(".")
            var = self.scope.get_var(name)
            if var.get_type() != InterpreterBase.OBJ_DEF:
                self.scope.error(
                    ErrorType.TYPE_ERROR, f"Cannot assign field to non-object"
                )
            self.scope.get_var(name).set_field(field, self.value)
            return
        self.scope.set_var(self.name, self.value)

    def __str__(self):
        return f"Assignment({self.name}, {str(self.value)})"
