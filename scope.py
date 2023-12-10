from constants import *
from intbase import ErrorType
from intbase import InterpreterBase
from copy import deepcopy
from value import Value
from lambda_def import LambdaDef
from function_def import FunctionDef
from value_wrapper import ValueWrapper
from object_def import ObjectDef


class Scope:
    interpreter = None

    def __init__(self, parent_scope, interpreter=None, trace_output=False):
        self.parent_scope = parent_scope
        if interpreter:
            Scope.interpreter = interpreter
        self.__var_map = {}
        self.__functions = {}
        self.trace_output = trace_output

    def get_var_scope(self, var_name):
        if var_name in self.__var_map:
            return self
        if self.parent_scope is None:
            return None
        return self.parent_scope.get_var_scope(var_name)

    def is_var(self, var_name):
        return self.get_var_scope(var_name) is not None

    def get_var_ref(self, var_name):
        scope = self.get_var_scope(var_name)
        if scope is None:
            # Checking for functions that aren't overloaded with the same name
            func_scope = self.get_func_scope(var_name, -1)
            if func_scope is None or len(func_scope.__functions[var_name]) > 1:
                self.error(ErrorType.NAME_ERROR, f"Variable {var_name} not defined")
            num_args = list(func_scope.__functions[var_name].keys())[0]
            return func_scope.__functions[var_name][num_args]
        return scope.__var_map[var_name]

    def get_var(self, var_name):
        return self.get_var_ref(var_name).get_val()

    def add_new_var(self, var_name, value):
        self.__var_map[var_name] = ValueWrapper(value)

    def add_ref_var(self, var_name, value):
        # If this isn't a value wrapper, it isn't a ref
        if type(value) != ValueWrapper:
            raise Exception(f"Expected ValueWrapper, got {type(value)}")
        self.__var_map[var_name] = value

    def set_var(self, var_name, value):
        if (
            type(value) != Value
            and type(value) != LambdaDef
            and type(value) != FunctionDef
            and type(value) != ObjectDef
        ):
            raise Exception(f"Expected savable Value, got {type(value)}")
        if self.trace_output:
            print(f"Setting {var_name} to {value}")
        scope = self.get_var_scope(var_name)
        if scope is None:
            self.add_new_var(var_name, value)
        else:
            scope.__var_map[var_name].set_value(value)

    def get_func_scope(self, func_name, num_args):
        if func_name in self.__functions:
            if num_args == -1:
                if len(self.__functions[func_name]) == 1:
                    return self
                else:
                    return None
            if num_args in self.__functions[func_name]:
                return self
            if self.trace_output:
                print(f"Function {func_name} exists but with different number of args")
        if self.parent_scope is None:
            return None
        return self.parent_scope.get_func_scope(func_name, num_args)

    def get_func_ref(self, func_name, num_args):
        scope = self.get_func_scope(func_name, num_args)
        if scope is None:
            # Check for functions stored in variables
            var_scope = self.get_var_scope(func_name)
            if var_scope is None:
                self.error(ErrorType.NAME_ERROR, f"Function {func_name} not defined")
            func_ref = var_scope.get_var_ref(func_name)
            func_type = func_ref.get_val().get_type()
            if (
                func_type != InterpreterBase.LAMBDA_DEF
                and func_type != InterpreterBase.FUNC_DEF
            ):
                self.error(
                    ErrorType.TYPE_ERROR,
                    f"{func_name} is defined but not as a function",
                )
                return
            return func_ref
        return scope.__functions[func_name][num_args]

    def get_func(self, func_name, num_args):
        return self.get_func_ref(func_name, num_args).get_val()

    def add_new_func(self, func, func_name):
        num_args = len(func.get_args())
        if func_name not in self.__functions:
            self.__functions[func_name] = {}
        self.__functions[func_name][num_args] = ValueWrapper(func)

    def add_ref_func(self, func, func_name):
        num_args = len(func.get_val().get_args())
        # If this isn't a value wrapper, it isn't a ref
        if type(func) != ValueWrapper:
            raise Exception("Expected ValueWrapper")
        if func_name not in self.__functions:
            self.__functions[func_name] = {}
        self.__functions[func_name][num_args] = func

    def set_func(self, func, func_name):
        if type(func) != FunctionDef:
            self.error(ErrorType.TYPE_ERROR, f"Expected FunctionDef, got {type(func)}")
        if self.trace_output:
            print(f"Setting {func_name} to {str(func)}")
        num_args = len(func.get_args())
        scope = self.get_func_scope(func_name, num_args)
        if scope is None:
            self.add_new_func(func, func_name, num_args)
        else:
            scope.__functions[func_name][num_args].set_value(func)

    def copy(self):
        if self.trace_output:
            print("Copying scope")
            print(f"Vars: {self.__var_map}")
            print(f"Functions: {self.__functions}")
        if self.parent_scope is None:
            new_scope = Scope(None)
        else:
            parent_copy = self.parent_scope.copy()
            new_scope = Scope(parent_copy)
        for var in self.__var_map.keys():
            val_ref = self.__var_map[var]
            val = val_ref.get_val()
            val_type = val.get_type()
            if (
                val_type == InterpreterBase.OBJ_DEF
                or val_type == InterpreterBase.FUNC_DEF
                or val_type == InterpreterBase.LAMBDA_DEF
            ):
                new_scope.add_ref_var(var, val_ref)
            else:
                new_scope.add_new_var(var, deepcopy(val))
        for func in self.__functions.keys():
            for num_args in self.__functions[func]:
                new_scope.add_new_func(
                    self.__functions[func][num_args].get_val(), deepcopy(func)
                )
        new_scope.trace_output = self.trace_output
        return new_scope

    def shallow_copy(self):
        if self.trace_output:
            print("Shallow copying scope")
            print(f"Vars: {self.__var_map}")
            print(f"Functions: {self.__functions}")
        if self.parent_scope is None:
            new_scope = Scope(None)
        else:
            parent_copy = self.parent_scope.shallow_copy()
            new_scope = Scope(parent_copy)
        for var in self.__var_map.keys():
            new_scope.add_ref_var(var, self.get_var_ref(var))
        for func_name in self.__functions.keys():
            for num_args in self.__functions[func_name]:
                new_scope.add_ref_func(
                    self.get_func_ref(func_name, num_args), func_name
                )
        new_scope.trace_output = self.trace_output
        return new_scope

    def __dump_info(self):
        print(str(self))

    def get_base_scope(self):
        if self.parent_scope is None:
            return self
        return self.parent_scope.get_base_scope()

    # Finds the base scope and adds the passed scope as the new base scope
    def add_base_scope(self, base_scope):
        self.get_base_scope().parent_scope = base_scope

    def make_child_scope(self):
        return Scope(self)

    def error(self, error_type, message):
        if self.trace_output:
            self.__dump_info()
        Scope.interpreter.error(error_type, message)

    def output(self, args):
        final_str = ""
        for arg in args:
            eval_arg = arg.evaluate()
            if eval_arg.get_type() == InterpreterBase.NIL_DEF:
                final_str += "nil"
            elif eval_arg.get_type() == InterpreterBase.STRING_DEF:
                final_str += eval_arg.get_val()
            elif eval_arg.get_type() == InterpreterBase.INT_DEF:
                final_str += str(eval_arg.get_val())
            elif eval_arg.get_type() == InterpreterBase.BOOL_DEF:
                final_str += "true" if eval_arg.get_val() else "false"
            else:
                self.error(
                    ErrorType.TYPE_ERROR,
                    f"Expected Value, got {eval_arg.get_type()}",
                )
        Scope.interpreter.output(final_str)

    def get_input(self):
        return Scope.interpreter.get_input()

    def __str__(self):
        final_str = ""
        final_str += "Scope info:\n"
        final_str += f"Vars: {self.__var_map}\n"
        final_str += f"Functions: {self.__functions}\n"
        if self.parent_scope is not None:
            final_str += "Parent Scope:\n"
            final_str += str(self.parent_scope)
        return final_str
