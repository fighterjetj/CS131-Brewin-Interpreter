from intbase import InterpreterBase, ErrorType
from constants import *
from copy import deepcopy
from element import Element
import scope


class ObjectDef:
    def __init__(self, element, trace_output=False):
        self.trace_output = trace_output
        self.__load_element(element)
        self.scope = scope.Scope(None, trace_output=self.trace_output)
        self.has_prototype = False

    def __load_element(self, element):
        if type(element) != Element or element.elem_type != InterpreterBase.OBJ_DEF:
            raise Exception(f"Expected Object Element, got {type(element)}")

    def get_field(self, field_name):
        return self.get_field_ref(field_name).get_val()

    def get_prototype(self):
        if not self.has_prototype:
            return None
        return self.get_field(PROTO)

    def get_field_ref(self, field_name):
        if self.has_field(field_name):
            if self.scope.is_var(field_name):
                return self.scope.get_var_ref(field_name)
            return self.get_prototype().get_field_ref(field_name)
        self.scope.error(ErrorType.NAME_ERROR, f"Field {field_name} not defined")

    def set_field(self, field_name, value):
        if field_name == PROTO:
            if self.trace_output:
                print(f"Setting prototype of {str(self)} to {str(value)}")
            if value.get_type() == InterpreterBase.NIL_DEF:
                self.has_prototype = False
                return
            if value.get_type() != InterpreterBase.OBJ_DEF:
                self.scope.error(
                    ErrorType.TYPE_ERROR, "Cannot assign prototype to non-object"
                )
            self.has_prototype = True
        self.scope.set_var(field_name, value)

    def has_field(self, var_name):
        if self.scope.is_var(var_name):
            return True
        if self.has_prototype:
            return self.get_prototype().has_field(var_name)
        return False

    def invoke_method(self, invoke_scope, method_name, args):
        if self.trace_output:
            print(f"Invoking method {method_name} on {str(self)}")
        method = self.get_field(method_name)
        if (
            method.get_type() != InterpreterBase.FUNC_DEF
            and method.get_type() != InterpreterBase.LAMBDA_DEF
        ):
            self.scope.error(
                ErrorType.TYPE_ERROR, f"Expected function, got {method.get_type()}"
            )
            return
        return method.invoke_func(invoke_scope, args)

    def get_type(self):
        return InterpreterBase.OBJ_DEF

    def evaluate(self):
        return self

    def copy(self):
        return deepcopy(self)
