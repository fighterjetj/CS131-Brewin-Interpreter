from constants import *
import convert_element
from intbase import InterpreterBase
from intbase import ErrorType
from element import Element
from return_type import Return
from eval_mult_statements import eval_mult_statements
from copy import deepcopy


class FunctionDef:
    def __init__(self, element, trace_output=False):
        self.trace_output = trace_output
        self.__load_element(element)

    def __load_element(self, element):
        if self.trace_output:
            print(f"Loading element {str(element)}")
        if type(element) != Element:
            raise Exception(f"Expected Element, got {type(element)}")
        if element.elem_type != InterpreterBase.FUNCTION_DEF:
            raise Exception(f"Expected function definition, got {element.elem_type}")
        self.statements = element.get(STATEMENTS)
        self.statements.append(element(InterpreterBase.RETURN_DEF))
        old_args = element.get(ARGS)
        self.args = []
        for arg in old_args:
            self.args.append(convert_element.convert_element(arg, None))

    def invoke_func(self, scope, args):
        new_scope = scope.make_child_scope()
        if len(args) != len(self.args):
            self.error(ErrorType.NAME_ERROR, "Incorrect number of arguments")
        for i in range(len(args)):
            arg = self.args[i]
            if arg.is_ref():
                if args[i].get_type() == InterpreterBase.VAR_DEF:
                    new_scope.add_ref_var(arg.get_name(), args[i].get_ref())
            else:
                new_scope.add_new_var(arg.get_name(), args[i].evaluate().copy())
        conv_statements = [
            convert_element.convert_element(statement, new_scope)
            for statement in self.statements
        ]
        return_val = eval_mult_statements(conv_statements)
        if type(return_val) == Return:
            return return_val.get_val()
        raise Exception("No return statement found")

    def get_statements(self):
        return self.statements

    def get_args(self):
        return self.args

    def get_num_args(self):
        return len(self.args)

    def get_type(self):
        return InterpreterBase.FUNC_DEF

    def evaluate(self):
        return self

    def copy(self):
        return deepcopy(self)

    def __str__(self):
        return f"FunctionDef - Args: {[str(arg) for arg in self.args]} - Statements: {[str(statement) for statement in self.statements]}"
