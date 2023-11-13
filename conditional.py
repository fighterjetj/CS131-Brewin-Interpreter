from constants import *
import convert_element
from eval_mult_statements import eval_mult_statements
from return_type import Return


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
        self.cond_statements = [
            convert_element.convert_element(statement, self.scope)
            for statement in element.get(STATEMENTS)
        ]
        # If this is a while loop and not an if statement, we must invoke it again at the end if the conditional is met
        if self.is_while:
            self.cond_statements.append(self)
        self.else_statements = element.get(ELSE_STATEMENTS)
        self.has_else = self.else_statements != None
        if self.has_else:
            self.else_statements = [
                convert_element.convert_element(statement, self.scope)
                for statement in self.else_statements
            ]

    def evaluate(self):
        if self.trace_output:
            print(f"Evaluating {str(self)}")
        condition_met = self.condition.evaluate()
        if (
            condition_met.get_type() != InterpreterBase.BOOL_DEF
            or condition_met.get_type() != InterpreterBase.INT_DEF
        ):
            raise Exception(f"Expected boolean or nil, got {self.condition.get_type()}")
        if self.condition.get_val():
            returned_val = eval_mult_statements(self.cond_statements)
            if type(returned_val) == Return:
                return returned_val
        elif self.has_else:
            returned_val = eval_mult_statements(self.else_statements)
            if type(returned_val) == Return:
                return returned_val
