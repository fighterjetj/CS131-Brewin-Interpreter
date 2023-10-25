from intbase import ErrorType
from element import Element
from interpreterv2 import InterpreterV2

class Statement:
    def __init__(self, interpreter, parent_statement, type, trace_output=False):
        self.parent_statement = parent_statement
        self.type = type
        if parent_statement:
            if trace_output:
                print("Creating new statement under parent statement")
            self.root_var_map = parent_statement.var_map
        else:
            if trace_output:
                print("Creating new root statement")
            self.root_var_map = {}
        
        # Because we can't declare functions within the statement of other functions, this is fine
        self.function_map = function_map

        self.local_var_map = {}
        self.trace_output = trace_output