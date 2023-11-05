from intbase import InterpreterBase, ErrorType
from brewparse import parse_program
from element import Element
from constants import *
from statement import Statement


class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.function_map = {}
        self.preloaded_funcs = set()
        self.trace_output = trace_output
        self.func_ind = 0

    def get_func_ind(self):
        self.func_ind += 1
        return self.func_ind

    def error(self, error_type: ErrorType, message: str) -> None:
        super().error(error_type, message)
        if self.trace_output:
            print(f"Error: {message}")

    def output(self, message: str) -> None:
        super().output(message)
        if self.trace_output:
            print(f"Outputting the following: {message}")

    def get_input(self) -> str:
        if self.trace_output:
            print("Getting Input")
        return super().get_input()

    def get_func_name(self, function: Element):
        if function.elem_type != InterpreterBase.FUNC_DEF:
            self.error(
                ErrorType.TYPE_ERROR,
                f"Tried to get name of node {str(function)}, which is not a function but a {function.elem_type}",
            )
            return None
        return function.get(NAME)

    def load_func(self, function: Element) -> None:
        if self.trace_output:
            print(f"Beginning to load {str(function)}")
        # Checking we were passed a function element
        if function.elem_type != InterpreterBase.FUNC_DEF:
            self.error(
                ErrorType.TYPE_ERROR,
                f"Tried to load node {str(function)}, which is not a function but a {function.elem_type}",
            )
            return
        name = self.get_func_name(function)
        if not name:
            self.error(
                ErrorType.FAULT_ERROR,
                f"No name associated with the function {str(function)}",
            )
            return
        num_args = len(function.get(ARGS))
        # For each function, we store it as a map between the function name and a map between the number of arguments and the function itself
        # This allows us to overload functions
        if name in self.function_map:
            # Overloading the function
            if self.trace_output:
                print(
                    f"Function {name} already exists: {self.function_map[name]}, overloading it"
                )
            if num_args in self.function_map[name]:
                if self.trace_output:
                    print(
                        f"Function {name} with {num_args} arguments already exists!  Overwriting it"
                    )
            self.function_map[name][num_args] = function
        else:
            self.function_map[name] = {num_args: function}
        if self.trace_output:
            print(f"Function {name} loaded")

    def preload_func(self, function: Element) -> None:
        if self.trace_output:
            print(f"Preloading {str(function)}")
        if function.elem_type != InterpreterBase.FUNC_DEF:
            self.error(
                ErrorType.TYPE_ERROR,
                f"Tried to load node {str(function)}, which is not a function",
            )
            return
        name = self.get_func_name(function)
        if not name:
            self.error(
                ErrorType.FAULT_ERROR,
                f"No name associated with the function {str(function)}",
            )
            return
        self.preloaded_funcs.add(name)
        # self.load_func(function)

    # Function we run at the beginning to load any functions we hardcode in (e.g. print)
    def preload_funcs(self) -> None:
        if self.trace_output:
            print("Preloading functions")
        # Constructing the print and inputi functions
        print_statements = [Element(elem_type=PRINT)]
        inputi_statements = [Element(elem_type=INPUTI)]
        inputs_statements = [Element(elem_type=INPUTS)]

        print_func = Element(
            InterpreterBase.FUNC_DEF, name=PRINT, statement=print_statements
        )
        inputi_func = Element(
            InterpreterBase.FUNC_DEF, name=INPUTI, statement=inputi_statements
        )
        inputs_func = Element(
            InterpreterBase.FUNC_DEF, name=INPUTS, statement=inputs_statements
        )

        funcs_to_load = [print_func, inputi_func, inputs_func]

        for func in funcs_to_load:
            self.preload_func(func)
            if self.trace_output:
                print(f"Preloaded function {str(func)}")

    def get_func(self, name, num_args):
        if self.func_exists(name):
            if num_args in self.function_map[name]:
                return self.function_map[name][num_args]
            self.error(
                ErrorType.NAME_ERROR,
                f"No such function as {name} with {num_args} arguments",
            )
        self.error(ErrorType.NAME_ERROR, f"No such function as {name}")

    def number_funcs(self, name):
        if self.func_exists(name):
            return len(self.function_map[name])
        return 0

    def func_exists(self, name):
        return name in self.function_map

    def is_preloaded(self, function_name):
        return function_name in self.preloaded_funcs

    def run(self, program: str) -> None:
        ast = parse_program(program)
        root_node = ast
        # The root_node should be a program node
        if root_node.elem_type != InterpreterBase.PROGRAM_DEF:
            self.error(ErrorType.TYPE_ERROR, "Program node not found")
            return
        # Clearing the variables and functions, in case this isn't the first invocation of the interpreter
        self.function_map = {}
        self.var_map = {}
        self.preload_funcs()
        # Loading functions
        for function in root_node.get(FUNCTIONS):
            self.load_func(function)
        if MAIN_FUNC_NAME not in self.function_map:
            self.error(
                ErrorType.NAME_ERROR, f"Main function {MAIN_FUNC_NAME} not found"
            )
        if self.trace_output:
            print("All functions loaded")
            print(f"Loaded function map: {str(self.function_map)}")
            print("Running main")
        # Now we can evaluate the program - assume it has no arguments passed
        main_func_call = Element(
            InterpreterBase.FCALL_DEF, name=MAIN_FUNC_NAME, args=[]
        )
        main_statement = Statement(self, None, main_func_call)
        main_statement.run()
