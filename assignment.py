from element import Element
from constants import *
import convert_element


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
        self.scope.set_var(self.name, self.value)

    def __str__(self):
        return f"Assignment({self.name}, {str(self.value)})"
