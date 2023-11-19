from intbase import InterpreterBase
from constants import *
from element import Element


class MCall:
    def __init__(self, scope, element, trace_output=False):
        self.trace_output = trace_output
        self.scope = scope
        self.__load_element(element)

    def __load_element(self, element):
        if self.trace_output:
            print(f"Loading element {str(element)}")
        if type(element) != Element or element.elem_type != InterpreterBase.MCALL_DEF:
            raise Exception(f"Expected Element, got {type(element)}")
        self.objref = element.get(OBJREF)
        self.name = element.get(NAME)
        self.args = element.get(ARGS)

    def evaluate(self):
        obj = self.scope.get_var(self.objref)
        if obj.get_type() != InterpreterBase.OBJECT_DEF:
            raise Exception(f"Expected Object, got {obj.get_type()}")
        return obj.invoke_method(self.scope, self.name, self.args)
