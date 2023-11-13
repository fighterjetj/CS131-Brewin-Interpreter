from intbase import InterpreterBase, ErrorType
from brewparse import parse_program
from scope import Scope
from convert_element import convert_element
from constants import *


class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)

    def error(self, error_type: ErrorType, message: str) -> None:
        super().error(error_type, message)

    def output(self, message: str) -> None:
        super().output(message)
        if self.trace_output:
            print(f"Outputting the following: {message}")

    def get_input(self) -> str:
        if self.trace_output:
            print("Getting Input")
        return super().get_input()

    def run(self, program: str) -> None:
        ast = parse_program(program)
        root_node = ast
        # The root_node should be a program node
        if root_node.elem_type != InterpreterBase.PROGRAM_DEF:
            raise Exception(f"Expected program node, received {root_node.elem_type}")
        base_scope = Scope(None, self)
        for function in root_node.get(FUNCTIONS):
            base_scope.add_new_func(convert_element(function), function.get(NAME))
        func_call = convert_element(
            Element(func_call, name="main", args=[]), base_scope
        )
        func_call.evaluate()
