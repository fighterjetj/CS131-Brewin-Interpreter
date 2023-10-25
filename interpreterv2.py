from intbase import InterpreterBase, ErrorType
from brewparse import parse_program
from element import Element

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
    OPERAND_1 = "op1"
    OPERAND_2 = "op2"
    ARGS = "args"
    STATEMENT_TYPES = [ASSIGNMENT, InterpreterBase.FCALL_DEF, InterpreterBase.IF_DEF, InterpreterBase.WHILE_DEF, InterpreterBase.RETURN_DEF]
    EXPRESSION_TYPES = [InterpreterBase.FCALL_DEF, ADD, SUBTRACT]
    VALUE_TYPES = [InterpreterBase.INT_DEF, InterpreterBase.STRING_DEF]
    INPUT = "inputi"
    PRINT = "print"
    PRELOADED_FUNCS = [PRINT, INPUT]

    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.function_map = {}
        self.var_map = {}
        self.preloaded_funcs = set()
        self.trace_output = trace_output
    
    def get_func_name(self, function):
        return function.get(Interpreter.NAME)
    
    def load_func(self, function: Element) -> None:
        # Checking we were passed a function element
        if function.elem_type != InterpreterBase.FUNC_DEF:
            super().error(ErrorType.TYPE_ERROR, f"Tried to load node {str(function)}, which is not a function but a {function.elem_type}")
            return
        
        name = self.get_func_name(function)
        if not name:
            super().error(ErrorType.FAULT_ERROR, f"No name associated with the function {str(function)}")
            return
        num_args = len(function.get(Interpreter.ARGS))
        # For each function, we store it as a map between the function name and a map between the number of arguments and the function itself
        # This allows us to overload functions
        if name in self.function_map:
            # Overloading the function
            self.function_map[name][num_args] = function
            if self.trace_output:
                print(f"Function {name} already exists, overloading it")
        
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
        print_statements = [] # No statements - currently preloaded funcs are hardcoded
        input_statements = []

        print_func = Element(InterpreterBase.FUNC_DEF, name=Interpreter.PRINT, statement = print_statements)
        input_func = Element(InterpreterBase.FUNC_DEF, name=Interpreter.INPUT, statement = input_statements)
        
        funcs_to_load = [print_func, input_func]

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
    
    def run_preloaded_func(self, function, args):
        if self.trace_output:
            print(f"Running preloaded function {str(function)} with args {str(args)}")
        match self.get_func_name(function):
                case Interpreter.PRINT:
                    super().output("".join([str(arg.get(Interpreter.VALUE)) for arg in args]))
                case Interpreter.INPUT:
                    if len(args) > 1:
                        return super().error(ErrorType.NAME_ERROR, "Inputi function takes at most one argument")
                    if len(args) == 1:
                        super().output(str(args[0].get(Interpreter.VALUE)))
                    input_val = super().get_input()
                    if input_val.isnumeric():
                        return Element(InterpreterBase.INT_DEF, val=int(input_val))
                    else:
                        super.error(ErrorType.TYPE_ERROR, f"Inputi function expected int, got {input_val}")
                case _:
                    super().error(ErrorType.TYPE_ERROR, f"Preloaded function {function.get(Interpreter.NAME)} not implemented")
            
    
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
        for function in root_node.get(Interpreter.FUNCTIONS):
            self.load_func(function)
        if Interpreter.MAIN_FUNC_NAME not in self.function_map:
            super().error(ErrorType.NAME_ERROR, f"Main function {Interpreter.MAIN_FUNC_NAME} not found")
        if self.trace_output:
            print("Running main")
        # Now we can evaluate the program - assume it has no arguments passed
        self.run_function(Interpreter.MAIN_FUNC_NAME, [])
            

    def run_function(self, function_name, args):
        if self.trace_output:
            print(f"Running {function_name} with args {str(args)}")
        num_args = len(args)
        function = self.get_func(function_name, num_args)
        # Evaluating the arguments before running the function
        eval_args = []
        for arg in args:
            eval_args.append(self.evaluate_node(arg))
        if self.trace_output:
            print(f"Evaluated args: {[str(arg) for arg in eval_args]}")
        
        # Preloaded functions are treated differently than user-defined functions
        if self.is_preloaded(function_name):
            return self.run_preloaded_func(function, eval_args)

        # Executing all statements in the function
        for statement in function.get(Interpreter.STATEMENT):
            # For the future - attempt at implementing return statements.  Not necessary for project 1
            """
            if statement.elem_type == InterpreterBase.RETURN_DEF:
                return self.evaluate_node(statement.get(Interpreter.EXPRESSION))
            """
            self.run_statement(statement)
        if self.trace_output:
            print(f"Finished running {function_name}")
    

    # We run the statement by checking its type and executing the appropriate code
    def run_statement(self, statement) -> None:
        match statement.elem_type:
            case Interpreter.ASSIGNMENT:
                self.run_assignment(statement)
            case InterpreterBase.FCALL_DEF:
                self.run_function(statement.get(Interpreter.NAME), statement.get(Interpreter.ARGS))
            case _:
                super().error(ErrorType.TYPE_ERROR, "Statement type not recognized")
                return
    
    # Assignment makes use of our var_map to store the variable name and its value, which is the evaluation of the expression
    def run_assignment(self, statement) -> None:
        if self.trace_output:
            print(f"Running assignment {statement}")
        self.var_map[statement.get(Interpreter.NAME)] = self.evaluate_node(statement.get(Interpreter.EXPRESSION))
        
    
    # Evaluates Value, Variable, and Expression nodes
    def evaluate_node(self, node) -> Element:
        type = node.elem_type
        # Most value types just directly return their values, no shenanigans necessary
        if type in Interpreter.VALUE_TYPES:
            return node

        # Variables are just looked up in the var_map - they are executed upon assignment, not lazily upon use, so we don't need to worry about them much
        elif type == InterpreterBase.VAR_DEF:
            if (node.get(Interpreter.NAME) not in self.var_map):
                super().error(ErrorType.NAME_ERROR, f"Variable {node.get(Interpreter.NAME)} not found")
            return self.var_map[node.get(Interpreter.NAME)]
        
        # Expressions are evaluated recursively - if it's a function, we'll run the function, but otherwise we just evaluate the operands recursively until we get returned values which are then used
        elif type in Interpreter.EXPRESSION_TYPES:
            match type:
                case InterpreterBase.FCALL_DEF:
                    return self.run_function(node.get(Interpreter.NAME), node.get(Interpreter.ARGS))
                case Interpreter.ADD:
                    op1 = self.evaluate_node(node.get(Interpreter.OPERAND_1))
                    op2 = self.evaluate_node(node.get(Interpreter.OPERAND_2))
                    if op1.elem_type != InterpreterBase.INT_DEF or op2.elem_type != InterpreterBase.INT_DEF:
                        super().error(ErrorType.TYPE_ERROR, "Invalid type for addition - expected int, got string")
                        # return str(self.evaluate_node(node.get(Interpreter.OPERAND_1)).get(Interpreter.VALUE)) + str(self.evaluate_node(node.get(Interpreter.OPERAND_2)).get(Interpreter.VALUE))
                    sum_vals = op1.get(Interpreter.VALUE) + op2.get(Interpreter.VALUE)
                    return Element(InterpreterBase.INT_DEF, val=sum_vals)
                case Interpreter.SUBTRACT:
                    op1 = self.evaluate_node(node.get(Interpreter.OPERAND_1))
                    op2 = self.evaluate_node(node.get(Interpreter.OPERAND_2))
                    if op1.elem_type != InterpreterBase.INT_DEF or op2.elem_type != InterpreterBase.INT_DEF:
                        super().error(ErrorType.TYPE_ERROR, "Invalid type for addition - expected int, got string")
                        # return str(self.evaluate_node(node.get(Interpreter.OPERAND_1)).get(Interpreter.VALUE)) + str(self.evaluate_node(node.get(Interpreter.OPERAND_2)).get(Interpreter.VALUE))
                    diff_vals = op1.get(Interpreter.VALUE) - op2.get(Interpreter.VALUE)
                    return Element(InterpreterBase.INT_DEF, val=diff_vals)
                case _:
                    super().error(ErrorType.TYPE_ERROR, f"Valid expression type {type} but executing the expression isn't yet implemented")
        else:
            super().error(ErrorType.TYPE_ERROR, f"{type} cannot be evaluated")
