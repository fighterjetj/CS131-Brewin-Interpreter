from element import Element
from intbase import InterpreterBase
from intbase import ErrorType
from constants import *
import convert_element
import scope
from value import Value


class FuncCall:
    def __init__(self, scope, element, trace_output=False):
        self.scope = scope
        self.trace_output = trace_output
        self.__load_element(element)

    def __load_element(self, element):
        if self.trace_output:
            print(f"Loading element {str(element)}")
        if type(element) != Element or element.elem_type != InterpreterBase.FCALL_DEF:
            raise Exception(f"Expected Element, got {type(element)}")
        self.name = element.get(NAME)
        self.args = []
        for arg in element.get(ARGS):
            self.args.append(convert_element.convert_element(arg, self.scope))

    def run_preloaded(self):
        num_args = len(self.args)
        if self.name == PRINT:
            self.scope.output(self.args)
        elif self.name in INPUT_TAKERS:
            if num_args > 1:
                self.scope.error(
                    ErrorType.NAME_ERROR,
                    f"Expected 0 or 1 arguments, got {num_args}",
                )
                return
            elif num_args == 1:
                self.scope.output(self.args)
            input_val = self.scope.get_input()
            if self.name == INPUTI:
                if not input_val or not input_val.isnumeric():
                    self.scope.error(
                        ErrorType.TYPE_ERROR,
                        f"Expected integer input, got {input_val}",
                    )
                return Value(int(input_val))
            else:
                return Value(input_val)

    def evaluate(self):
        if self.trace_output:
            print(f"Evaluating {str(self)}")
        num_args = len(self.args)
        if self.name in PRELOADED_FUNCS:
            return self.run_preloaded()
        return self.scope.get_func(self.name, num_args).invoke_func(
            self.scope, self.args
        )

    def __str__(self):
        return f"FuncCall({self.name}, {[str(arg) for arg in self.args]})"
