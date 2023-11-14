from constants import *
import convert_element
from eval_mult_statements import eval_mult_statements
import return_type


class Conditional:
    def __init__(self, scope, element, is_while, trace_output=False):
        self.scope = scope.make_child_scope()
        self.trace_output = trace_output
        self.is_while = is_while
        self.__load_element(element)

    def __load_element(self, element):
        self.condition = convert_element.convert_element(
            element.get(CONDITION), self.scope
        )
        self.statements = element.get(STATEMENTS)
        self.else_statements = element.get(ELSE_STATEMENTS)
        self.has_else = self.else_statements != None

    def evaluate(self):
        if self.trace_output:
            print(f"Evaluating {str(self)}")
        condition_met = self.condition.evaluate()
        if (
            condition_met.get_type() != InterpreterBase.BOOL_DEF
            and condition_met.get_type() != InterpreterBase.INT_DEF
        ):
            raise Exception(f"Expected boolean or nil, got {condition_met.get_type()}")
        if condition_met.get_val():
            returned_val = eval_mult_statements(self.statements, self.scope)
            if type(returned_val) == return_type.Return:
                return returned_val
            # If we are a while loop we evaluate again
            if self.is_while:
                return self.evaluate()
        elif self.has_else:
            returned_val = eval_mult_statements(self.else_statements, self.scope)
            if type(returned_val) == return_type.Return:
                return returned_val
