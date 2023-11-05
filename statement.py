from intbase import ErrorType
from element import Element
from intbase import InterpreterBase
from constants import *
from copy import deepcopy


class Statement:
    def __init__(self, interpreter, parent_statement, statement_node: Element):
        self.parent_statement = parent_statement
        self.type = statement_node.elem_type
        self.trace_output = interpreter.trace_output
        self.interpreter = interpreter
        self.statement_node = statement_node
        if not self.type in STATEMENT_TYPES:
            interpreter.error(
                ErrorType.TYPE_ERROR,
                f"Statement type {statement_node.elem_type} not recognized",
            )
        if parent_statement:
            if self.trace_output:
                print("Creating new statement under parent statement")
        else:
            if self.trace_output:
                print("Creating new root statement")

        # Because we can't declare functions within the statement of other functions, this is fine
        self.var_map = {}

    def get_copy_of_scope(self) -> dict:
        if self.trace_output:
            print("Getting copy of scope")
        if not self.parent_statement:
            return deepcopy(self.var_map)
        parent_scope = self.parent_statement.get_copy_of_scope()
        for key, value in self.var_map.items():
            parent_scope[deepcopy(key)] = deepcopy(value)
        return parent_scope

    def copy_scope_to(self, other_statement):
        if self.trace_output:
            print("Copying scope")
        scope_copy = self.get_copy_of_scope()
        for key in scope_copy.keys():
            value = scope_copy[key]
            other_statement.var_map[key] = value

    def error(self, error_type: ErrorType, message: str) -> None:
        if self.trace_output:
            self.dump_info()
        # self.dump_info()
        self.interpreter.error(error_type, message)

    def deep_copy_value(self, val: Element) -> Element:
        if val.elem_type == InterpreterBase.FUNC_DEF:
            return Element(
                InterpreterBase.FUNC_DEF,
                name=val.get(NAME),
                func_ind=self.interpreter.get_func_ind(),
            )
        if val.elem_type == LAMBDA_PTR:
            old_lambda = self.interpreter.get_lambda(val.get(LAMBDA_PTR))
            new_lambda = deepcopy(old_lambda)
            new_ind = self.interpreter.add_lambda(new_lambda)
            return Element(LAMBDA_PTR, lambda_ptr=new_ind)
        return deepcopy(val)

    def dump_info(self):
        print("\nDumping statement info")
        print(f"Statement type: {self.type}")
        print(f"Statement node: {str(self.statement_node)}")
        print(f"Var map: {self.var_map}")
        if self.parent_statement:
            print("\nPrinting my parent statement")
            self.parent_statement.dump_info()

    # We recursively check if the variable exists in the current statement or any parent statements
    # We stop when we reach the invoking function
    def get_var_scope(self, name: str):
        if name in self.var_map:
            if self.trace_output:
                print(f"Found variable {name} in this scope")
            if self.var_map[name].elem_type == InterpreterBase.REFARG_DEF:
                return self.parent_statement.get_var_scope(self.var_map[name].get(NAME))
            return self
        # Recursively get the scope
        if not self.parent_statement:
            if self.trace_output:
                print("Reached the root statement!")
            return None
        return self.parent_statement.get_var_scope(name)

    def follow_ref_to_name(self, name: str):
        if name in self.var_map:
            if self.trace_output:
                print(f"Found variable {name} in this scope")
            if self.var_map[name].elem_type == InterpreterBase.REFARG_DEF:
                return self.parent_statement.follow_ref_to_name(
                    self.var_map[name].get(NAME)
                )
            return name
        # Recursively get the scope
        if not self.parent_statement:
            if self.trace_output:
                print("Reached the root statement!")
            return None
        return self.parent_statement.follow_ref_to_name(name)

    def get_var(self, name: str) -> Element:
        scope = self.get_var_scope(name)
        true_name = self.follow_ref_to_name(name)
        if not scope:
            # We make a unique reference to the function
            if self.interpreter.number_funcs(name) == 1:
                return Element(
                    InterpreterBase.FUNC_DEF,
                    name=name,
                    func_ind=0,
                )
            elif self.interpreter.number_funcs(name) > 1:
                self.error(
                    ErrorType.NAME_ERROR,
                    f"Function {name} is overloaded, cannot be gotten as a variable",
                )
            else:
                self.error(ErrorType.NAME_ERROR, f"No such variable as {name}")
            return None
        return scope.var_map[true_name]

    def add_var(self, name: str, value: Element) -> None:
        if name in self.var_map:
            """self.error(
                ErrorType.NAME_ERROR,
                f"Variable {name} already exists in this scope, cannot add it",
            )"""
        if self.trace_output:
            print(f"Making new variable {name} set to {str(value)}")
        self.var_map[name] = value

    def set_var(self, name: str, value: Element) -> None:
        scope = self.get_var_scope(name)
        true_name = self.follow_ref_to_name(name)
        if not scope:
            self.add_var(name, value)
        else:
            scope.var_map[true_name] = value

    def get_func(self, name: str, num_args: int) -> Element:
        if self.trace_output:
            print(f"Getting function {name} with {num_args} arguments")
        var_func_scope = self.get_var_scope(name)
        if var_func_scope:
            var_func = var_func_scope.get_var(name)
            if var_func.elem_type == InterpreterBase.FUNC_DEF:
                base_func_name = var_func.get(NAME)
                return self.interpreter.get_func(base_func_name, num_args)
            if var_func.elem_type == LAMBDA_PTR:
                lambda_ind = var_func.get(LAMBDA_PTR)
                return self.interpreter.get_lambda(lambda_ind)
            else:
                self.error(
                    ErrorType.TYPE_ERROR,
                    f"Variable {name} exists but is not a function",
                )
                return NIL_VAL
        if self.interpreter.is_preloaded(name):
            return Element(InterpreterBase.FUNC_DEF, name=name)
        return self.interpreter.get_func(name, num_args)

    def evaluate_unary_operation(self, expression: Element) -> Element:
        if self.trace_output:
            print(f"Evaluating unary operation {str(expression)}")
        val = self.evaluate_expression(expression.get(OPERAND_1))
        type = val.elem_type
        exp_type = expression.elem_type
        if type == InterpreterBase.INT_DEF and not (exp_type in UNARY_INT_OPERATORS):
            self.error(
                ErrorType.TYPE_ERROR, f"Got an int when expected another datatype"
            )
            return NIL_VAL
        if type == InterpreterBase.BOOL_DEF and not (exp_type in UNARY_BOOL_OPERATORS):
            self.error(
                ErrorType.TYPE_ERROR, f"Got a bool when expected another datatype"
            )
            return NIL_VAL
        if type == InterpreterBase.STRING_DEF and not (
            exp_type in UNARY_STRING_OPERATORS
        ):
            self.error(
                ErrorType.TYPE_ERROR, f"Got a string when expected another datatype"
            )
            return NIL_VAL
        if exp_type == InterpreterBase.NEG_DEF:
            return Element(InterpreterBase.INT_DEF, val=-val.get(VALUE))
        if exp_type == InterpreterBase.NOT_DEF:
            return Element(InterpreterBase.BOOL_DEF, val=not val.get(VALUE))
        self.error(
            ErrorType.TYPE_ERROR,
            f"Unary operator {expression.elem_type} not implemented",
        )
        return NIL_VAL

    def evaluate_binary_operation(self, expression: Element) -> Element:
        if self.trace_output:
            print(f"Evaluating binary operation {str(expression)}")
        val1 = self.evaluate_expression(expression.get(OPERAND_1))
        val2 = self.evaluate_expression(expression.get(OPERAND_2))
        type1 = val1.elem_type
        type2 = val2.elem_type
        exp_type = expression.elem_type
        if type1 != type2:
            if not (exp_type in MIXED_TYPE_BINARY_OPERATORS):
                self.error(
                    ErrorType.TYPE_ERROR,
                    f"Got {type1} and {type2} when expected same datatype",
                )
                return NIL_VAL
            # Mixed types have to be int and/or bool
            if (
                type1 != InterpreterBase.INT_DEF and type1 != InterpreterBase.BOOL_DEF
            ) or (
                type2 != InterpreterBase.BOOL_DEF and type2 != InterpreterBase.INT_DEF
            ):
                self.error(
                    ErrorType.TYPE_ERROR,
                    f"Got {type1} and {type2} when both must be an int or a bool",
                )
                return NIL_VAL
        if type1 == InterpreterBase.INT_DEF and not (exp_type in BINARY_INT_OPERATORS):
            self.error(
                ErrorType.TYPE_ERROR, f"Got an int when expected another datatype"
            )
            return NIL_VAL
        if type1 == InterpreterBase.BOOL_DEF and not (
            exp_type in BINARY_BOOL_OPERATORS
        ):
            self.error(
                ErrorType.TYPE_ERROR, f"Got a bool when expected another datatype"
            )
            return NIL_VAL
        if type1 == InterpreterBase.STRING_DEF and not (
            exp_type in BINARY_STRING_OPERATORS
        ):
            self.error(
                ErrorType.TYPE_ERROR, f"Got a string when expected another datatype"
            )
            return NIL_VAL
        if exp_type == ADD:
            if type1 == InterpreterBase.STRING_DEF and type1 == type2:
                return Element(
                    InterpreterBase.STRING_DEF, val=val1.get(VALUE) + val2.get(VALUE)
                )
            return Element(
                InterpreterBase.INT_DEF, val=val1.get(VALUE) + val2.get(VALUE)
            )
        if exp_type == SUBTRACT:
            return Element(
                InterpreterBase.INT_DEF, val=val1.get(VALUE) - val2.get(VALUE)
            )
        if exp_type == MULTIPLY:
            return Element(
                InterpreterBase.INT_DEF, val=val1.get(VALUE) * val2.get(VALUE)
            )
        if exp_type == DIVIDE:
            return Element(
                InterpreterBase.INT_DEF, val=int(val1.get(VALUE) // val2.get(VALUE))
            )
        if exp_type == OR:
            return Element(
                InterpreterBase.BOOL_DEF, val=bool(val1.get(VALUE) or val2.get(VALUE))
            )
        if exp_type == AND:
            return Element(
                InterpreterBase.BOOL_DEF, val=bool(val1.get(VALUE) and val2.get(VALUE))
            )
        self.error(
            ErrorType.TYPE_ERROR,
            f"Binary operator {expression.elem_type} not implemented for types {type1} and {type2}",
        )
        return NIL_VAL

    def evaluate_comparison_operation(self, expression: Element) -> Element:
        if self.trace_output:
            print(f"Evaluating comparison operation {str(expression)}")
        val1 = self.evaluate_expression(expression.get(OPERAND_1))
        val2 = self.evaluate_expression(expression.get(OPERAND_2))
        type1 = val1.elem_type
        type2 = val2.elem_type
        exp_type = expression.elem_type
        if type1 != type2:
            if not (exp_type in MIXED_TYPE_COMPARISON_OPERATORS):
                self.error(
                    ErrorType.TYPE_ERROR,
                    f"Got {type1} and {type2} when expected same datatype",
                )
                return NIL_VAL
        if type1 == InterpreterBase.INT_DEF and not (
            exp_type in COMPARISON_INT_OPERATORS
        ):
            self.error(
                ErrorType.TYPE_ERROR, f"Got an int when expected another datatype"
            )
            return NIL_VAL
        if type1 == InterpreterBase.BOOL_DEF and not (
            exp_type in COMPARISON_BOOL_OPERATORS
        ):
            self.error(
                ErrorType.TYPE_ERROR, f"Got a bool when expected another datatype"
            )
            return NIL_VAL
        if type1 == InterpreterBase.STRING_DEF and not (
            exp_type in COMPARISON_STRING_OPERATORS
        ):
            self.error(
                ErrorType.TYPE_ERROR, f"Got a string when expected another datatype"
            )
            return NIL_VAL
        if type1 == InterpreterBase.NIL_DEF and not (
            exp_type in COMPARISON_NIL_OPERATORS
        ):
            self.error(
                ErrorType.TYPE_ERROR, f"Got a nil when expected another datatype"
            )
            return NIL_VAL
        if exp_type == EQUALS:
            if type1 != type2:
                # Handling casting ints to bools
                if (
                    type1 == InterpreterBase.BOOL_DEF
                    and type2 == InterpreterBase.INT_DEF
                ):
                    return Element(
                        InterpreterBase.BOOL_DEF,
                        val=(val1.get(VALUE) == bool(val2.get(VALUE))),
                    )
                if (
                    type1 == InterpreterBase.INT_DEF
                    and type2 == InterpreterBase.BOOL_DEF
                ):
                    return Element(
                        InterpreterBase.BOOL_DEF,
                        val=(bool(val1.get(VALUE)) == val2.get(VALUE)),
                    )
                return Element(InterpreterBase.BOOL_DEF, val=False)
            if type1 == InterpreterBase.NIL_DEF:
                return Element(InterpreterBase.BOOL_DEF, val=(type1 == type2))
            if type1 == InterpreterBase.FUNC_DEF:
                return Element(
                    InterpreterBase.BOOL_DEF,
                    val=(val1.get(FUNC_IND) == val2.get(FUNC_IND))
                    and (val1.get(NAME) == val2.get(NAME)),
                )
            if type1 == LAMBDA_PTR:
                return Element(
                    InterpreterBase.BOOL_DEF,
                    val=(val1.get(LAMBDA_PTR) == val2.get(LAMBDA_PTR)),
                )
            return Element(
                InterpreterBase.BOOL_DEF, val=(val1.get(VALUE) == val2.get(VALUE))
            )
        if exp_type == NOT_EQUALS:
            if type1 != type2:
                # Handling casting ints to bools
                if (
                    type1 == InterpreterBase.BOOL_DEF
                    and type2 == InterpreterBase.INT_DEF
                ):
                    return Element(
                        InterpreterBase.BOOL_DEF,
                        val=(val1.get(VALUE) != bool(val2.get(VALUE))),
                    )
                if (
                    type1 == InterpreterBase.INT_DEF
                    and type2 == InterpreterBase.BOOL_DEF
                ):
                    return Element(
                        InterpreterBase.BOOL_DEF,
                        val=(bool(val1.get(VALUE)) != val2.get(VALUE)),
                    )
                return Element(InterpreterBase.BOOL_DEF, val=True)
            if type1 == InterpreterBase.NIL_DEF:
                return Element(InterpreterBase.BOOL_DEF, val=(type1 != type2))
            if type1 == InterpreterBase.FUNC_DEF:
                return Element(
                    InterpreterBase.BOOL_DEF,
                    val=(val1.get(FUNC_IND) != val2.get(FUNC_IND))
                    or (val1.get(NAME) != val2.get(NAME)),
                )
            return Element(
                InterpreterBase.BOOL_DEF, val=(val1.get(VALUE) != val2.get(VALUE))
            )
        if exp_type == LESS_THAN:
            return Element(
                InterpreterBase.BOOL_DEF, val=(val1.get(VALUE) < val2.get(VALUE))
            )
        if exp_type == LESS_THAN_EQUALS:
            return Element(
                InterpreterBase.BOOL_DEF, val=(val1.get(VALUE) <= val2.get(VALUE))
            )
        if exp_type == GREATER_THAN:
            return Element(
                InterpreterBase.BOOL_DEF, val=(val1.get(VALUE) > val2.get(VALUE))
            )
        if exp_type == GREATER_THAN_EQUALS:
            return Element(
                InterpreterBase.BOOL_DEF, val=(val1.get(VALUE) >= val2.get(VALUE))
            )
        self.error(
            ErrorType.TYPE_ERROR,
            f"Comparison operator {exp_type} not implemented for types {type1} and {type2}",
        )
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
            if expression_type in COMPARISON_OPERATORS:
                return self.evaluate_comparison_operation(expression)
        if expression_type == InterpreterBase.LAMBDA_DEF:
            scoped_statement = Statement(
                self.interpreter, None, Element(InterpreterBase.LAMBDA_DEF)
            )
            self.copy_scope_to(scoped_statement)
            statements = expression.get(STATEMENTS)
            statements.append(Element(InterpreterBase.RETURN_DEF))
            new_element = Element(
                InterpreterBase.LAMBDA_DEF,
                scope=scoped_statement,
                args=expression.get(ARGS),
                statements=statements,
            )
            lambda_ind = self.interpreter.add_lambda(new_element)
            return Element(LAMBDA_PTR, lambda_ptr=lambda_ind)
        self.error(
            ErrorType.TYPE_ERROR, f"Expression type {expression_type} not recognized"
        )
        return NIL_VAL

    def run_assignment(self) -> Element:
        name = self.statement_node.get(NAME)
        value = self.statement_node.get(EXPRESSION)
        value = self.evaluate_expression(value)
        if self.trace_output:
            print(f"Running assignment {name} = {str(value)}")
        # The current scope is just the assignment statement, thus we need to assign it in the scope of the parent statement
        self.parent_statement.set_var(name, value)
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
            self.error(
                ErrorType.TYPE_ERROR,
                f"Input functions take at most 1 arguments, but got {len(args)}",
            )
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

    def load_args(self, arg_names, args):
        if len(arg_names) != len(args):
            self.error(
                ErrorType.TYPE_ERROR,
                f"Expected {len(arg_names)} arguments, got {len(args)}",
            )
            return NIL_VAL
        for i in range(len(arg_names)):
            if arg_names[i].elem_type == InterpreterBase.ARG_DEF:
                self.add_var(arg_names[i].get(NAME), self.evaluate_expression(args[i]))
            elif arg_names[i].elem_type == InterpreterBase.REFARG_DEF:
                # Only matters if we are being passed a variable, otherwise the reference is to nowhere
                if args[i].elem_type == InterpreterBase.VAR_DEF:
                    ref_elem = Element(
                        InterpreterBase.REFARG_DEF, name=args[i].get(NAME)
                    )
                    self.add_var(arg_names[i].get(NAME), ref_elem)
                else:
                    self.add_var(
                        arg_names[i].get(NAME), self.evaluate_expression(args[i])
                    )

    def run_function(self, function) -> Element:
        if self.trace_output:
            print(f"Running function {str(self.statement_node)}")
        args = self.statement_node.get(ARGS)
        num_args = len(args)
        # Getting the function from the interpreter
        function_name = self.statement_node.get(NAME)
        true_name = self.interpreter.get_func_name(function)
        if self.interpreter.is_preloaded(true_name):
            new_node = Element(function_name, args=args)
            new_statement = Statement(self.interpreter, self, new_node)
            return new_statement.run()
        # arg names
        arg_names = function.get(ARGS)
        # Loading the arguments into the function's scope
        self.load_args(arg_names, args)

        if self.trace_output:
            print(f"Running function {function_name} with {num_args} arguments")
        # Running the function
        statements = function.get(STATEMENTS)
        # Adding return at the very end - it will only run if there isn't already a return
        statements.append(Element(InterpreterBase.RETURN_DEF))
        returned_val = self.run_statements(statements)
        if returned_val.elem_type == InterpreterBase.RETURN_DEF:
            return returned_val.get(RETURNED)
        self.error("Function did not return anything")
        return NIL_VAL

    def run_lambda(self, lambda_func) -> Element:
        if self.trace_output:
            print(f"Running lambda {str(self.statement_node)}")
        # Getting the lambda from the lambda pointer
        args = self.statement_node.get(ARGS)
        arg_names = lambda_func.get(ARGS)
        # Loading the scope
        lambda_scope = lambda_func.get(SCOPE)
        lambda_scope.load_args(arg_names, args)
        lambda_scope.parent_statement = self
        lambda_scope.statement_node = Element(
            InterpreterBase.LAMBDA_DEF, statements=lambda_func.get(STATEMENTS)
        )
        returned_val = lambda_scope.run_statements(lambda_func.get(STATEMENTS))
        if returned_val.elem_type == InterpreterBase.RETURN_DEF:
            return returned_val.get(RETURNED)
        self.error("Lambda did not return anything")

    def run_fcall(self) -> Element:
        if self.trace_output:
            print(f"Running fcall {str(self.statement_node)}")
        function = self.get_func(
            self.statement_node.get(NAME), len(self.statement_node.get(ARGS))
        )
        if function.elem_type == InterpreterBase.FUNC_DEF:
            # print("Starting the dump")
            # self.dump_info()
            return self.run_function(function)
        if function.elem_type == InterpreterBase.LAMBDA_DEF:
            return self.run_lambda(function)

    def eval_conditional(self, condition: Element) -> bool:
        if self.trace_output:
            print(f"Evaluating conditional {str(condition)}")
        condition = self.evaluate_expression(condition)
        if (
            condition.elem_type != InterpreterBase.BOOL_DEF
            and condition.elem_type != InterpreterBase.INT_DEF
        ):
            self.error(
                ErrorType.TYPE_ERROR,
                f"Expected bool for condition, got {condition.elem_type}",
            )
            return False
        return bool(condition.get(VALUE))

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
        if return_val:
            return_val = self.evaluate_expression(return_val)
            return Element(
                InterpreterBase.RETURN_DEF, returned=self.deep_copy_value(return_val)
            )
        return Element(
            InterpreterBase.RETURN_DEF, returned=self.deep_copy_value(NIL_VAL)
        )

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
            """name = self.statement_node.get(NAME)
            if name in self.interpreter.preloaded_funcs:
                new_statement = Statement(self.interpreter, self, Element(elem_type=name, args=self.statement_node.get(ARGS)))
                return new_statement.run()"""
            return self.run_fcall()
        if self.type == InterpreterBase.IF_DEF:
            return self.run_if()
        if self.type == InterpreterBase.WHILE_DEF:
            return self.run_while()
        if self.type == InterpreterBase.LAMBDA_DEF:
            returned = self.run_statements(self.statement_node.get(STATEMENTS))
            if returned.elem_type == InterpreterBase.RETURN_DEF:
                return returned.get(RETURNED)
            self.error("No return statement in lambda")
            return NIL_VAL
        if self.trace_output:
            self.dump_info()
        self.error(ErrorType.TYPE_ERROR, f"Statement type {self.type} not recognized")
        return NIL_VAL
