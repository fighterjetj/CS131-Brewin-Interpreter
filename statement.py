from intbase import ErrorType
from element import Element
from intbase import InterpreterBase
from constants import *
class Statement:
    def __init__(self, interpreter, parent_statement, statement_node: Element):
        if type(interpreter) != InterpreterBase:
            raise Exception("Interpreter must be of type InterpreterBase")
        self.parent_statement = parent_statement
        self.statement_node = statement_node
        if not statement_node.elem_type in interpreter.statement_types:
            interpreter.super().error(ErrorType.TYPE_ERROR, f"Statement type {statement_node.elem_type} not recognized")
            return
        self.type = statement_node.elem_type
        self.trace_output = interpreter.trace_output
        if parent_statement:
            if self.trace_output:
                print("Creating new statement under parent statement")
        else:
            if self.trace_output:
                print("Creating new root statement")
        
        # Because we can't declare functions within the statement of other functions, this is fine
        self.function_map = interpreter.function_map
        self.var_map = {}

    def get_statement_scope(self):
        if self.type == InterpreterBase.FUNC_DEF:
            return self
        if not self.parent_statement:
            if self.trace_output:
                print(f"All non-function statements should have a parent statement, but this one doesn't!  Very interesting...")
            return None
        return self.parent_statement.get_statement_scope()
    # We recursively check if the variable exists in the current statement or any parent statements
    # We stop when we reach the invoking function
    def get_var_scope(self, name: str):
        if name in self.var_map:
            return self
        if self.type == InterpreterBase.FUNC_DEF:
            return None
        # Recursively get the scope
        if not self.parent_statement:
            if self.trace_output:
                print(f"All non-function statements should have a parent statement, but this one doesn't!  Very interesting...")
            return None
        
        return self.parent_statement.get_var_scope(name)

    def get_var(self, name: str) -> Element:
        scope = self.get_var_scope(name)
        if not scope:
            self.interpreter.super().error(ErrorType.NAME_ERROR, f"No such variable as {name}")
            return NIL_VAL
        return scope.var_map[name]

    def set_var(self, name: str, value: Element) -> None:
        scope = self.get_var_scope(name)
        if not scope:
            self.var_map[name] = value
        else:
            scope.var_map[name] = value
    
    def evaluate_unary_operation(self, expression: Element) -> Element:
        val = self.evaluate_expression(expression.get(OPERAND_1))
        type = val.elem_type
        if type == InterpreterBase.INT_DEF and not (type in UNARY_INT_OPERATORS):
            self.interpreter.super().error(ErrorType.TYPE_ERROR, f"Got an int when expected another datatype")
            return NIL_VAL
        if type == InterpreterBase.BOOL_DEF and not (type in UNARY_BOOL_OPERATORS):
            self.interpreter.super().error(ErrorType.TYPE_ERROR, f"Got a bool when expected another datatype")
            return NIL_VAL
        if type == InterpreterBase.STRING_DEF and not (type in UNARY_STRING_OPERATORS):
            self.interpreter.super().error(ErrorType.TYPE_ERROR, f"Got a string when expected another datatype")
            return NIL_VAL
        match expression.elem_type:
            case InterpreterBase.NEG_DEF:
                return Element(InterpreterBase.INT_DEF, value=-val.get(VALUE))
            case InterpreterBase.NOT_DEF:
                return Element(InterpreterBase.BOOL_DEF, value=not val.get(VALUE))
    
    def evaluate_binary_operation(self, expression: Element) -> Element:
        val1 = self.evaluate_expression(expression.get(OPERAND_1))
        val2 = self.evaluate_expression(expression.get(OPERAND_2))
        type1 = val1.elem_type
        type2 = val2.elem_type
        if type1 != type2:
            self.interpreter.super().error(ErrorType.TYPE_ERROR, f"Got {type1} and {type2} when expected same datatype")
            return NIL_VAL
        if type1 == InterpreterBase.INT_DEF and not (type1 in BINARY_INT_OPERATORS):
            self.interpreter.super().error(ErrorType.TYPE_ERROR, f"Got an int when expected another datatype")
            return NIL_VAL
        if type1 == InterpreterBase.BOOL_DEF and not (type1 in BINARY_BOOL_OPERATORS):
            self.interpreter.super().error(ErrorType.TYPE_ERROR, f"Got a bool when expected another datatype")
            return NIL_VAL
        if type1 == InterpreterBase.STRING_DEF and not (type1 in BINARY_STRING_OPERATORS):
            self.interpreter.super().error(ErrorType.TYPE_ERROR, f"Got a string when expected another datatype")
            return NIL_VAL
        match expression.elem_type:
            case str(ADD):
                return Element(type1, value=val1.get(VALUE) + val2.get(VALUE))
            case str(SUBTRACT):
                return Element(type1, value=val1.get(VALUE) - val2.get(VALUE))
            case str(MULTIPLY):
                return Element(type1, value=val1.get(VALUE) * val2.get(VALUE))
            case str(DIVIDE):
                return Element(type1, value=int(val1.get(VALUE) / val2.get(VALUE)))
            case str(OR):
                return Element(type1, value=(val1.get(VALUE) or val2.get(VALUE)))
            case str(AND):
                return Element(type1, value=(val1.get(VALUE) and val2.get(VALUE)))
            case _:
                self.interpreter.super().error(ErrorType.TYPE_ERROR, f"Binary operator {expression.elem_type} not implemented")
                return NIL_VAL
    
    def evaluate_comparison_operation(self, expression: Element) -> Element:
        val1 = self.evaluate_expression(expression.get(OPERAND_1))
        val2 = self.evaluate_expression(expression.get(OPERAND_2))
        type1 = val1.elem_type
        type2 = val2.elem_type
        if type1 != type2:
            self.interpreter.super().error(ErrorType.TYPE_ERROR, f"Got {type1} and {type2} when expected same datatype")
            return NIL_VAL
        if type1 == InterpreterBase.INT_DEF and not (type1 in COMPARISON_INT_OPERATORS):
            self.interpreter.super().error(ErrorType.TYPE_ERROR, f"Got an int when expected another datatype")
            return NIL_VAL
        if type1 == InterpreterBase.BOOL_DEF and not (type1 in COMPARISON_BOOL_OPERATORS):
            self.interpreter.super().error(ErrorType.TYPE_ERROR, f"Got a bool when expected another datatype")
            return NIL_VAL
        if type1 == InterpreterBase.STRING_DEF and not (type1 in COMPARISON_STRING_OPERATORS):
            self.interpreter.super().error(ErrorType.TYPE_ERROR, f"Got a string when expected another datatype")
            return NIL_VAL
        match expression.elem_type:
            case str(EQUALS):
                return Element(type1, value=(val1.get(VALUE) == val2.get(VALUE)))
            case str(NOT_EQUALS):
                return Element(type1, value=(val1.get(VALUE) != val2.get(VALUE)))
            case str(LESS_THAN):
                return Element(type1, value=(val1.get(VALUE) < val2.get(VALUE)))
            case str(LESS_THAN_EQUALS):
                return Element(type1, value=(val1.get(VALUE) <= val2.get(VALUE)))
            case str(GREATER_THAN):
                return Element(type1, value=(val1.get(VALUE) > val2.get(VALUE)))
            case str(GREATER_THAN_EQUALS):
                return Element(type1, value=(val1.get(VALUE) >= val2.get(VALUE)))
            case _:
                self.interpreter.super().error(ErrorType.TYPE_ERROR, f"Comparison operator {expression.elem_type} not implemented")
                return NIL_VAL
            

    # Technically evaluates expressions, variables, and values, but variables and values are very little work so I fold them in
    def evaluate_expression(self, expression: Element) -> Element:
        expression_type = expression.elem_type
        if expression_type == InterpreterBase.FCALL_DEF:
            function_statement = Statement(self.interpreter, self, expression)
            return function_statement.run()
        if expression_type == InterpreterBase.VAR_DEF:
            return self.get_var(expression.get(NAME))
        if expression_type in VALUE_TYPES:
            return expression
        if expression_type in OPERATORS:
            if expression_type in UNARY_OPERATORS:
                return self.evaluate_unary_operation(expression)
            if expression_type in BINARY_OPERATORS:
                return self.evaluate_binary_operation(expression)
            if expression_type in COMPARSION_OPERATORS:
                return self.evaluate_comparison_operation(expression)
            

    
    def run_assignment(self) -> None:
        name = self.statement_node.get(NAME)
        value = self.statement_node.get(VALUE)
        self.set_var(name, self.evaluate_expression(value))

    # Preloaded functions
    def run_print(self) -> None:
        args = self.statement_node.get(ARGS)
        output_str = ""
        for arg in args:
            if type(arg) == bool:
                output_str += str(arg).lower()
            else:
                output_str += str(arg)
        self.interpreter.super().output(output_str)
    
    def get_input(self):
        args = self.statement_node.get(ARGS)
        if len(args) > 1:
            self.interpreter.super().error(ErrorType.TYPE_ERROR, f"inputi takes at most 1 arguments, but got {len(args)}")
            return
        if len(args) == 1:
            self.run_print()
        input_val = self.interpreter.super().get_input()
        return input_val

    def run_inputi(self) -> Element:
        input_val = self.get_input()
        if not input_val or not input_val.isnumeric():
            self.interpreter.super().error(ErrorType.TYPE_ERROR, f"inputi expected int, got {input_val}")
            return NIL_VAL
        return Element(InterpreterBase.INT_DEF, value=int(input_val))
    
    def run_inputs(self) -> Element:
        input_val = self.get_input()
        return Element(InterpreterBase.STRING_DEF, value=input_val)
    
    def run_statements(self, statements) -> Element:
        for statement in statements:
            curr_statement = Statement(self.interpreter, self, statement)
            returned_val = curr_statement.run()
            if returned_val.elem_type == InterpreterBase.RETURN_DEF:
                return returned_val
        return NIL_VAL

    def run_function(self) -> Element:
        args = self.statement_node.get(ARGS)
        num_args = len(args)
        # Getting the function from the interpreter
        function_name = self.statement_node.get(NAME)
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
    
    def run_if(self) -> None:
        condition = self.statement_node.get(CONDITION)
        condition = self.evaluate_expression(condition)
        statements = []
        if condition.get(VALUE):
            statements = self.statement_node.get(STATEMENTS)
        else:
            statements = self.statement_node.get(ELSE_STATEMENTS)
        if statements:
            return self.run_statements(statements)
    
    def run_while(self) -> None:
        condition = self.statement_node.get(CONDITION)
        statements = self.statement_node.get(STATEMENTS)
        # Constantly reevaluate the condition and run the statements until the condition is false
        while self.evaluate_expression(condition).get(VALUE):
            returned_val = self.run_statements(statements)
            if returned_val.elem_type == InterpreterBase.RETURN_DEF:
                return returned_val
    
    def run_return(self) -> Element:
        return_val = self.statement_node.get(EXPRESSION)
        return_val = self.evaluate_expression(return_val)
        return Element(InterpreterBase.RETURN_DEF, expression=return_val)

    def run(self) -> Element:
        # Match statements in Python are stupid - if you match a var it will try and store it's value into it?
        # I have no idea why it's like this, but it is, so by wrapping it in str() we get around this
        # Also, if you access a var from another object it also works?  See evaluate_unary_operation for example
        match self.type:
            # Preloaded statements for built in functions (currently print, inputi, and inputs)
            case str(PRINT):
                self.run_print()
            case str(INPUTI):
                return self.run_inputi()
            case str(INPUTS):
                return self.run_inputs()
            
            # Statements that are not for preloaded functions
            case str(ASSIGNMENT):
                self.run_assignment()
            case str(InterpreterBase.FUNC_DEF):
                return self.run_function()
            case str(InterpreterBase.IF_DEF):
                return self.run_if()
            case str(InterpreterBase.WHILE_DEF):
                return self.run_while()
            case _:
                self.interpreter.super().error(ErrorType.TYPE_ERROR, f"Statement type {self.type} not recognized")
                return NIL_VAL
        # By default, we just return nil
        return NIL_VAL