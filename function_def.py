from constants import *
import convert_element
from intbase import InterpreterBase
from intbase import ErrorType
from element import Element
import return_type
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
        if (
            element.elem_type != InterpreterBase.FUNC_DEF
            and element.elem_type != InterpreterBase.LAMBDA_DEF
        ):
            raise Exception(f"Expected function definition, got {element.elem_type}")
        self.statements = element.get(STATEMENTS)
        self.statements.append(Element(InterpreterBase.RETURN_DEF))
        # print(f"Statements: {[str(statement) for statement in self.statements]}")
        old_args = element.get(ARGS)
        self.args = []
        for arg in old_args:
            self.args.append(convert_element.convert_element(arg, None))

    def load_args(self, scope, args):
        if len(args) != len(self.args):
            scope.error(ErrorType.NAME_ERROR, "Incorrect number of arguments")
        for i in range(len(args)):
            arg = self.args[i]
            if arg.is_ref():
                # If it isn't a variable, the reference is meaningless
                if args[i].get_type() == InterpreterBase.VAR_DEF and scope.is_var(
                    args[i].get_name()
                ):
                    scope.add_ref_var(arg.get_name(), args[i].get_ref())
                # We don't need to load functions again
                else:
                    scope.add_new_var(arg.get_name(), args[i].evaluate().copy())
            else:
                scope.add_new_var(arg.get_name(), args[i].evaluate().copy())

    def invoke_func(self, scope, args):
        new_scope = scope.make_child_scope()
        self.load_args(new_scope, args)
        return_val = eval_mult_statements(self.statements, new_scope)
        if type(return_val) == return_type.Return:
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
