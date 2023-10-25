from intbase import InterpreterBase, ErrorType
from brewparse import parse_program
from element import Element
from constants import *

class Interpreter(InterpreterBase):
    FUNCTIONS = "functions"
    VALUE = "val"
    NAME = "name"
    MAIN_FUNC_NAME = "main"
    STATEMENT = "statements"
    EXPRESSION = "expression"
    ASSIGNMENT = "="
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    EQUALS = "=="
    NOT_EQUALS = "!="
    LESS_THAN = "<"
    LESS_THAN_EQUALS = "<="
    GREATER_THAN = ">"
    GREATER_THAN_EQUALS = ">="
    OR = "||"
    AND = "&&"
    BINARY_INT_OPERATORS = [ADD, SUBTRACT, MULTIPLY, DIVIDE]
    COMPARISON_INT_OPERATORS = [EQUALS, NOT_EQUALS, LESS_THAN, LESS_THAN_EQUALS, GREATER_THAN, GREATER_THAN_EQUALS]
    UNARY_INT_OPERATORS = [InterpreterBase.NEG_DEF]
    BINARY_BOOL_OPERATORS = [OR, AND]
    COMPARISON_BOOL_OPERATORS = [EQUALS, NOT_EQUALS]
    UNARY_BOOL_OPERATORS = [InterpreterBase.NOT_DEF]
    BINARY_STRING_OPERATORS = [ADD]
    COMPARISON_STRING_OPERATORS = [EQUALS, NOT_EQUALS]
    UNARY_STRING_OPERATORS = []
    BINARY_OPERATORS = BINARY_INT_OPERATORS + BINARY_BOOL_OPERATORS + BINARY_STRING_OPERATORS
    COMPARSION_OPERATORS = COMPARISON_INT_OPERATORS + COMPARISON_BOOL_OPERATORS + COMPARISON_STRING_OPERATORS
    UNARY_OPERATORS = UNARY_INT_OPERATORS + UNARY_BOOL_OPERATORS + UNARY_STRING_OPERATORS
    OPERATORS = BINARY_OPERATORS + UNARY_OPERATORS
    OPERAND_1 = "op1"
    OPERAND_2 = "op2"
    ARGS = "args"
    INPUTI = "inputi"
    INPUTS = "inputs"
    PRINT = "print"
    PRELOADED_FUNCS = [PRINT, INPUTI, INPUTS]
    STATEMENT_TYPES = [ASSIGNMENT, InterpreterBase.FCALL_DEF, InterpreterBase.IF_DEF, InterpreterBase.WHILE_DEF, InterpreterBase.RETURN_DEF]
    STATEMENT_TYPES += PRELOADED_FUNCS
    EXPRESSION_TYPES = [InterpreterBase.FCALL_DEF] + OPERATORS
    VALUE_TYPES = [InterpreterBase.INT_DEF, InterpreterBase.STRING_DEF, InterpreterBase.BOOL_DEF, InterpreterBase.NIL_DEF]
    NIL_VAL = Element(InterpreterBase.NIL_DEF)

    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.function_map = {}
        self.preloaded_funcs = set()
        self.trace_output = trace_output
    
    def get_func_name(self, function: Element):
        if function.elem_type != InterpreterBase.FUNC_DEF:
            super().error(ErrorType.TYPE_ERROR, f"Tried to get name of node {str(function)}, which is not a function but a {function.elem_type}")
            return None
        return function.get(NAME)
    
    def load_func(self, function: Element) -> None:
        # Checking we were passed a function element
        if function.elem_type != InterpreterBase.FUNC_DEF:
            super().error(ErrorType.TYPE_ERROR, f"Tried to load node {str(function)}, which is not a function but a {function.elem_type}")
            return
        name = self.get_func_name(function)
        if not name:
            super().error(ErrorType.FAULT_ERROR, f"No name associated with the function {str(function)}")
            return
        num_args = len(function.get(ARGS))
        # For each function, we store it as a map between the function name and a map between the number of arguments and the function itself
        # This allows us to overload functions
        if name in self.function_map:
            # Overloading the function
            if self.trace_output:
                print(f"Function {name} already exists, overloading it")
            if num_args in self.function_map[name]:
                if self.trace_output:
                    print(f"Function {name} with {num_args} arguments already exists!  Overwriting it")
            self.function_map[name][num_args] = function
        
        self.function_map[name] = {num_args: function}
        if self.trace_output:
            print(f"Function {name} loaded")

    def preload_func(self, function: Element) -> None:
        if function.elem_type != InterpreterBase.FUNC_DEF:
            super().error(ErrorType.TYPE_ERROR, f"Tried to load node {str(function)}, which is not a function")
            return
        name = self.get_func_name(function)
        if not name:
            super().error(ErrorType.FAULT_ERROR, f"No name associated with the function {str(function)}")
            return
        print(f"Beginning to preload {str(function)}")
        self.preloaded_funcs.add(name)
        self.load_func(function)

    # Function we run at the beginning to load any functions we hardcode in (e.g. print)
    def preload_funcs(self) -> None:
        # Constructing the print and inputi functions
        print_statements = [Element(elem_type=PRINT)]
        inputi_statements = [Element(elem_type=INPUTI)]
        inputs_statements = [Element(elem_type=INPUTS)]

        print_func = Element(InterpreterBase.FUNC_DEF, name=PRINT, statement = print_statements)
        inputi_func = Element(InterpreterBase.FUNC_DEF, name=INPUTI, statement = inputi_statements)
        inputs_func = Element(InterpreterBase.FUNC_DEF, name=INPUTS, statement = inputs_statements)
        
        funcs_to_load = [print_func, inputi_func, inputs_func]

        for func in funcs_to_load:
            self.preload_func(func)
            if self.trace_output:
                print(f"Preloaded function {str(func)}")
    
    def get_func(self, name, num_args):
        if not name in self.function_map:
            super().error(ErrorType.NAME_ERROR, f"No such function as {name}")
            return None
        if not num_args in self.function_map[name]:
            super().error(ErrorType.NAME_ERROR, f"No such function as {name} with {num_args} arguments")
        return self.function_map[name][num_args]

    def is_preloaded(self, function_name):
        return function_name in self.preloaded_funcs
            
    
    def run(self, program: str) -> None:
        ast = parse_program(program)
        root_node = ast
        # The root_node should be a program node
        if root_node.elem_type != InterpreterBase.PROGRAM_DEF:
            super().error(ErrorType.TYPE_ERROR, "Program node not found")
            return
        # Clearing the variables and functions, in case this isn't the first invocation of the interpreter
        self.function_map = {}
        self.var_map = {}
        self.preload_funcs()
        # Loading functions
        for function in root_node.get(FUNCTIONS):
            self.load_func(function)
        if MAIN_FUNC_NAME not in self.function_map:
            super().error(ErrorType.NAME_ERROR, f"Main function {MAIN_FUNC_NAME} not found")
        if self.trace_output:
            print("Running main")
        # Now we can evaluate the program - assume it has no arguments passed
        self.run_function(MAIN_FUNC_NAME, [])

    # We run the statement by checking its type and executing the appropriate code
    def run_statement(self, statement) -> None:
        match statement.elem_type:
            case str(ASSIGNMENT):
                self.run_assignment(statement)
            case InterpreterBase.FCALL_DEF:
                self.run_function(statement.get(NAME), statement.get(ARGS))
            case _:
                super().error(ErrorType.TYPE_ERROR, "Statement type not recognized")
                return