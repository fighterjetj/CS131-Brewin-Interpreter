from intbase import InterpreterBase, ErrorType
from constants import *
from element import Element
import scope
import convert_element


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
        self.args = []
        for arg in element.get(ARGS):
            self.args.append(convert_element.convert_element(arg, self.scope))

    def evaluate(self):
        obj = self.scope.get_var(self.objref)
        obj_ref = self.scope.get_var_ref(self.objref)
        if obj.get_type() != InterpreterBase.OBJ_DEF:
            self.scope.error(
                ErrorType.TYPE_ERROR, f"Expected Object, got {obj.get_type()}"
            )
        # Adding this to the scope
        this_scope = scope.Scope(self.scope, trace_output=self.trace_output)
        this_scope.add_ref_var(InterpreterBase.THIS_DEF, obj_ref)
        return obj.invoke_method(this_scope, self.name, self.args)
