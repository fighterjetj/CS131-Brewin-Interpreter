from intbase import ErrorType
from element import Element
from intbase import InterpreterBase
from constants import *
class Statement:
    def __init__(self, interpreter, parent_statement, statement_node: Element):
        self.parent_statement = parent_statement
        self.type = statement_node.elem_type
        self.trace_output = interpreter.trace_output
        self.interpreter = interpreter
        self.statement_node = statement_node
        if not statement_node.elem_type in STATEMENT_TYPES:
            interpreter.error(ErrorType.TYPE_ERROR, f"Statement type {statement_node.elem_type} not recognized")
        if parent_statement:
            if self.trace_output:
                print("Creating new statement under parent statement")
        else:
            if self.trace_output:
                print("Creating new root statement")
        
        # Because we can't declare functions within the statement of other functions, this is fine
        self.var_map = {}
    
    def error(self, error_type: ErrorType, message: str) -> None:
        if self.trace_output:
            self.dump_info()
        self.interpreter.error(error_type, message)


    def dump_info(self):
        print(f"Statement type: {self.type}")
        print(f"Statement node: {str(self.statement_node)}")
        print(f"Var map: {self.var_map}")
        if self.parent_statement:
            print("Printing my parent statement")
            self.parent_statement.dump_info()
    # We recursively check if the variable exists in the current statement or any parent statements
    # We stop when we reach the invoking function
    def get_var_scope(self, name: str):
        if name in self.var_map:
            return self
        if self.type == InterpreterBase.FCALL_DEF:
            return None
        # Recursively get the scope
        if not self.parent_statement:
            if self.trace_output:
                self.error(ErrorType.FAULT_ERROR, f"The root of this statement tree has been reached and it has type {self.type} instead of {InterpreterBase.FCALL_DEF}")
            return None
        
        return self.parent_statement.get_var_scope(name)

    def get_var(self, name: str) -> Element:
        if name in self.var_map:
            if self.trace_output:
                print(f"Getting variable {name}")
            return self.var_map[name]
        scope = self.get_var_scope(name)
        if not scope:
            self.error(ErrorType.NAME_ERROR, f"No such variable as {name}")
            return None
        return scope.get_var(name)

    def set_var(self, name: str, value: Element) -> None:
        if name in self.var_map:
            if self.trace_output:
                print(f"Setting variable {name} to {str(value)}")
            self.var_map[name] = value
            return
        scope = self.get_var_scope(name)
        if not scope:
            if self.trace_output:
                print(f"Setting variable {name} to {str(value)}")
            self.var_map[name] = value
        else:
            scope.set_var(name, value)
    
    def evaluate_unary_operation(self, expression: Element) -> Element:
        if self.trace_output:
            print(f"Evaluating unary operation {str(expression)}")
        val = self.evaluate_expression(expression.get(OPERAND_1))
        type = val.elem_type
        op_type = expression.elem_type
        if type == InterpreterBase.INT_DEF and not (op_type in UNARY_INT_OPERATORS):
            self.error(ErrorType.TYPE_ERROR, f"Got an int when expected another datatype")
            return NIL_VAL
        if type == InterpreterBase.BOOL_DEF and not (op_type in UNARY_BOOL_OPERATORS):
            self.error(ErrorType.TYPE_ERROR, f"Got a bool when expected another datatype")
            return NIL_VAL
        if type == InterpreterBase.STRING_DEF and not (op_type in UNARY_STRING_OPERATORS):
            self.error(ErrorType.TYPE_ERROR, f"Got a string when expected another datatype")
            return NIL_VAL
        exp_type = expression.elem_type
        if exp_type == InterpreterBase.NEG_DEF:
            return Element(InterpreterBase.INT_DEF, val=-val.get(VALUE))
        if exp_type == InterpreterBase.NOT_DEF:
            return Element(InterpreterBase.BOOL_DEF, val=not val.get(VALUE))
        self.error(ErrorType.TYPE_ERROR, f"Unary operator {expression.elem_type} not implemented")
        return NIL_VAL

    def evaluate_binary_operation(self, expression: Element) -> Element:
        if self.trace_output:
            print(f"Evaluating binary operation {str(expression)}")
        val1 = self.evaluate_expression(expression.get(OPERAND_1))
        val2 = self.evaluate_expression(expression.get(OPERAND_2))
        type1 = val1.elem_type
        type2 = val2.elem_type
        op_type = expression.elem_type
        if type1 != type2:
            self.error(ErrorType.TYPE_ERROR, f"Got {type1} and {type2} when expected same datatype")
            return NIL_VAL
        if type1 == InterpreterBase.INT_DEF and not (op_type in BINARY_INT_OPERATORS):
            self.error(ErrorType.TYPE_ERROR, f"Got an int when expected another datatype")
            return NIL_VAL
        if type1 == InterpreterBase.BOOL_DEF and not (op_type in BINARY_BOOL_OPERATORS):
            self.error(ErrorType.TYPE_ERROR, f"Got a bool when expected another datatype")
            return NIL_VAL
        if type1 == InterpreterBase.STRING_DEF and not (op_type in BINARY_STRING_OPERATORS):
            self.error(ErrorType.TYPE_ERROR, f"Got a string when expected another datatype")
            return NIL_VAL
        exp_type = expression.elem_type
        if exp_type == ADD:
            return Element(type1, val=val1.get(VALUE) + val2.get(VALUE))
        if exp_type == SUBTRACT:
            return Element(type1, val=val1.get(VALUE) - val2.get(VALUE))
        if exp_type == MULTIPLY:
            return Element(type1, val=val1.get(VALUE) * val2.get(VALUE))
        if exp_type == DIVIDE:
            return Element(type1, val=int(val1.get(VALUE) / val2.get(VALUE)))
        if exp_type == OR:
            return Element(type1, val=(val1.get(VALUE) or val2.get(VALUE)))
        if exp_type == AND:
            return Element(type1, val=(val1.get(VALUE) and val2.get(VALUE)))
        self.error(ErrorType.TYPE_ERROR, f"Binary operator {expression.elem_type} not implemented")
        return NIL_VAL
    
    def evaluate_comparison_operation(self, expression: Element) -> Element:
        if self.trace_output:
            print(f"Evaluating comparison operation {str(expression)}")
        val1 = self.evaluate_expression(expression.get(OPERAND_1))
        val2 = self.evaluate_expression(expression.get(OPERAND_2))
        type1 = val1.elem_type
        type2 = val2.elem_type
        op_type = expression.elem_type
        if type1 != type2:
            self.error(ErrorType.TYPE_ERROR, f"Got {type1} and {type2} when expected same datatype")
            return NIL_VAL
        if type1 == InterpreterBase.INT_DEF and not (op_type in COMPARISON_INT_OPERATORS):
            self.error(ErrorType.TYPE_ERROR, f"Got an int when expected another datatype")
            return NIL_VAL
        if type1 == InterpreterBase.BOOL_DEF and not (op_type in COMPARISON_BOOL_OPERATORS):
            self.error(ErrorType.TYPE_ERROR, f"Got a bool when expected another datatype")
            return NIL_VAL
        if type1 == InterpreterBase.STRING_DEF and not (op_type in COMPARISON_STRING_OPERATORS):
            self.error(ErrorType.TYPE_ERROR, f"Got a string when expected another datatype")
            return NIL_VAL
        exp_type = expression.elem_type
        if exp_type == EQUALS:
            return Element(type1, val=(val1.get(VALUE) == val2.get(VALUE)))
        if exp_type == NOT_EQUALS:
            return Element(type1, val=(val1.get(VALUE) != val2.get(VALUE)))
        if exp_type == LESS_THAN:
            return Element(type1, val=(val1.get(VALUE) < val2.get(VALUE)))
        if exp_type == LESS_THAN_EQUALS:
            return Element(type1, val=(val1.get(VALUE) <= val2.get(VALUE)))
        if exp_type == GREATER_THAN:
            return Element(type1, val=(val1.get(VALUE) > val2.get(VALUE)))
        if exp_type == GREATER_THAN_EQUALS:
            return Element(type1, val=(val1.get(VALUE) >= val2.get(VALUE)))
        self.error(ErrorType.TYPE_ERROR, f"Comparison operator {expression.elem_type} not implemented")
        return NIL_VAL
            

    # Technically evaluates expressions, variables, and values, but variables and values are very little work so I fold them in
    def evaluate_expression(self, expression: Element) -> Element:
        if self.trace_output:
            print(f"Evaluating expression {str(expression)}")
        expression_type = expression.elem_type
        if expression_type == InterpreterBase.FCALL_DEF:
            function_statement = Statement(self.interpreter, self, expression)
            return function_statement.run()
        # The scope we want is the scope of the parent statement, not the current statement
        # As the parent statement is where we are being invoked from
        if expression_type == InterpreterBase.VAR_DEF:
            return self.parent_statement.get_var(expression.get(NAME))
        if expression_type in VALUE_TYPES:
            return expression
        if expression_type in OPERATORS:
            if expression_type in UNARY_OPERATORS:
                return self.evaluate_unary_operation(expression)
            if expression_type in BINARY_OPERATORS:
                return self.evaluate_binary_operation(expression)
            if expression_type in COMPARSION_OPERATORS:
                return self.evaluate_comparison_operation(expression)
        self.error(ErrorType.TYPE_ERROR, f"Expression type {expression_type} not recognized")
        return NIL_VAL
            

    
    def run_assignment(self) -> Element:
        name = self.statement_node.get(NAME)
        value = self.statement_node.get(EXPRESSION)
        value = self.evaluate_expression(value)
        if self.trace_output:
            print(f"Running assignment {name} = {str(value)}")
        # The current scope is just the assignment statement, thus we need to assign it in the scope of the parent statement
        self.parent_statement.set_var(name, self.evaluate_expression(value))
        return NIL_VAL

    # Preloaded functions
    def run_print(self) -> Element:
        args = self.statement_node.get(ARGS)
        args = [self.evaluate_expression(arg) for arg in args]
        if self.trace_output:
            print(f"Printing {[str(arg) for arg in args]}")
        output_str = ""
        for arg in args:
            arg_val = arg.get(VALUE)
            if type(arg_val) == bool:
                output_str += str(arg_val).lower()
            else:
                output_str += str(arg_val)
        self.interpreter.output(output_str)
        return NIL_VAL
    
    def get_input(self) -> str:
        if self.trace_output:
            print(f"Getting input from {str(self.statement_node)}")
        args = self.statement_node.get(ARGS)
        if len(args) > 1:
            self.error(ErrorType.TYPE_ERROR, f"Input functions take at most 1 arguments, but got {len(args)}")
            return
        if len(args) == 1:
            self.run_print()
        input_val = self.interpreter.get_input()
        return input_val

    def run_inputi(self) -> Element:
        if self.trace_output:
            print(f"Running inputi {str(self.statement_node)}")
        input_val = self.get_input()
        if not input_val or not input_val.isnumeric():
            self.error(ErrorType.TYPE_ERROR, f"inputi expected int, got {input_val}")
            return NIL_VAL
        return Element(InterpreterBase.INT_DEF, val=int(input_val))
    
    def run_inputs(self) -> Element:
        if self.trace_output:
            print(f"Running inputs {str(self.statement_node)}")
        input_val = self.get_input()
        return Element(InterpreterBase.STRING_DEF, val=input_val)
    
    def run_statements(self, statements) -> Element:
        if self.trace_output:
            print(f"Running statements")
        for statement in statements:
            curr_statement = Statement(self.interpreter, self, statement)
            returned_val = curr_statement.run()
            if returned_val.elem_type == InterpreterBase.RETURN_DEF:
                return returned_val
        return NIL_VAL

    def run_function(self) -> Element:
        if self.trace_output:
            print(f"Running function {str(self.statement_node)}")
        args = self.statement_node.get(ARGS)
        args = [self.evaluate_expression(arg) for arg in args]
        num_args = len(args)
        # Getting the function from the interpreter
        function_name = self.statement_node.get(NAME)
        if function_name in PRELOADED_FUNCS:
            new_node = Element(function_name, args=args)
            new_statement = Statement(self.interpreter, self, new_node)
            return new_statement.run()
        function = self.interpreter.get_func(function_name, num_args)
        # arg names
        arg_names = function.get(ARGS)
        for i in range(len(args)):
            self.var_map[arg_names[i].get(NAME)] = self.evaluate_expression(args[i])
        if self.trace_output:
            print(f"Running function {function_name} with {num_args} arguments")
        # Running the function
        statements = function.get(STATEMENTS)
        return self.run_statements(statements)
    
    def eval_conditional(self, condition: Element) -> bool:
        if self.trace_output:
            print(f"Evaluating conditional {str(condition)}")
        condition = self.evaluate_expression(condition)
        if condition.elem_type != InterpreterBase.BOOL_DEF:
            self.error(ErrorType.TYPE_ERROR, f"Expected bool for if condition, got {condition.elem_type}")
            return False
        return condition.get(VALUE)

    def run_if(self) -> Element:
        if self.trace_output:
            print(f"Running if {str(self.statement_node)}")
        condition = self.statement_node.get(CONDITION)
        if self.eval_conditional(condition):
            statements = self.statement_node.get(STATEMENTS)
        else:
            statements = self.statement_node.get(ELSE_STATEMENTS)
        if statements:
            return self.run_statements(statements)
        return NIL_VAL
    
    def run_while(self) -> Element:
        if self.trace_output:
            print(f"Running while {str(self.statement_node)}")
        condition = self.statement_node.get(CONDITION)
        statements = self.statement_node.get(STATEMENTS)
        # Constantly reevaluate the condition and run the statements until the condition is false
        while self.eval_conditional(condition):
            returned_val = self.run_statements(statements)
            if returned_val.elem_type == InterpreterBase.RETURN_DEF:
                return returned_val
        return NIL_VAL
    
    def run_return(self) -> Element:
        if self.trace_output:
            print(f"Running return {str(self.statement_node)}")
        return_val = self.statement_node.get(EXPRESSION)
        return_val = self.evaluate_expression(return_val)
        return Element(InterpreterBase.RETURN_DEF, expression=return_val)

    def run(self) -> Element:
        if self.trace_output:
            print(f"Running statement {str(self.statement_node)} of type {self.type}")
        # Match statements in Python are stupid - if you match a var it will try and store it's value into it
        # Instead of fixing it I'm just going to use if statements because that's the easy way out
        # Preloaded statements for built in functions (currently print, inputi, and inputs)
        if self.type == PRINT:
            return self.run_print()
        if self.type == INPUTI:
            return self.run_inputi()
        if self.type == INPUTS:
            return self.run_inputs()
        # Statements that are not for preloaded functions
        if self.type == ASSIGNMENT:
            return self.run_assignment()
        if self.type == InterpreterBase.RETURN_DEF:
            return self.run_return()
        if self.type == InterpreterBase.FCALL_DEF:
            name = self.statement_node.get(NAME)
            """if name in self.interpreter.preloaded_funcs:
                new_statement = Statement(self.interpreter, self, Element(elem_type=name, args=self.statement_node.get(ARGS)))
                return new_statement.run()"""
            return self.run_function()
        if self.type == InterpreterBase.IF_DEF:
            return self.run_if()
        if self.type == InterpreterBase.WHILE_DEF:
            return self.run_while()
        if self.trace_output:
            self.dump_info()
        self.error(ErrorType.TYPE_ERROR, f"Statement type {self.type} not recognized")
        return NIL_VAL