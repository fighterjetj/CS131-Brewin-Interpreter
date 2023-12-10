from element import Element
from value import Value
from constants import *
import convert_element
from intbase import InterpreterBase
from intbase import ErrorType


class BinaryOperator:
    def __init__(self, scope, element, trace_output=False):
        self.scope = scope
        self.trace_output = trace_output
        self.__load_element(element)

    def __load_element(self, element):
        if self.trace_output:
            print(f"Loading element {str(element)}")
        if type(element) != Element:
            raise Exception(f"Expected Element, got {type(element)}")
        self.type = element.elem_type
        if not self.type in BINARY_OPERATORS:
            raise Exception(f"Unknown element type {self.type}")
        self.left = convert_element.convert_element(element.get(OPERAND_1), self.scope)
        self.right = convert_element.convert_element(element.get(OPERAND_2), self.scope)

    def evaluate(self):
        if self.trace_output:
            print(f"Evaluating {str(self)}")
        self.left = self.left.evaluate()
        self.right = self.right.evaluate()
        if self.trace_output:
            print(f"Left: {str(self.left)}")
            print(f"Right: {str(self.right)}")

        if self.type in BINARY_ARITH:
            return self.__eval_arith()

        elif self.type in BINARY_BOOL:
            return self.__eval_bool()

        elif self.type in BINARY_COMP:
            return self.__eval_comp()

    def __eval_comp(self):
        if self.type == EQUALS:
            return self.__eval_equal()
        elif self.type == NOT_EQUALS:
            return self.__eval_not_equal()
        elif self.type == GREATER_THAN:
            return self.__eval_greater()
        elif self.type == GREATER_THAN_EQUALS:
            return self.__eval_greater_equal()
        elif self.type == LESS_THAN:
            return self.__eval_less()
        elif self.type == LESS_THAN_EQUALS:
            return self.__eval_less_equal()
        raise Exception(f"Unknown comparison operator {self.type}")

    def __eval_equal(self):
        left_type = self.left.get_type()
        right_type = self.right.get_type()
        if left_type == right_type:
            if (
                left_type == InterpreterBase.FUNC_DEF
                or left_type == InterpreterBase.LAMBDA_DEF
                or left_type == InterpreterBase.OBJ_DEF
            ):
                return Value(self.left is self.right)
            return Value(self.left.get_val() == self.right.get_val())
        # If we have a bool and an int we compare their bool values
        if (
            left_type == InterpreterBase.BOOL_DEF
            and right_type == InterpreterBase.INT_DEF
        ):
            return Value(self.left.get_val() == bool(self.right.get_val()))
        if (
            left_type == InterpreterBase.INT_DEF
            and right_type == InterpreterBase.BOOL_DEF
        ):
            return Value(bool(self.left.get_val()) == self.right.get_val())
        # If the types are different, they aren't equal
        return Value(False)

    def __eval_not_equal(self):
        return Value(not self.__eval_equal().get_val())

    def __eval_greater(self):
        left_type = self.left.get_type()
        right_type = self.right.get_type()
        if left_type == right_type and left_type == InterpreterBase.INT_DEF:
            return Value(self.left.get_val() > self.right.get_val())
        self.scope.error(
            ErrorType.TYPE_ERROR,
            f"Cannot compare {self.left.get_type()} and {self.right.get_type()}",
        )

    def __eval_less(self):
        left_type = self.left.get_type()
        right_type = self.right.get_type()
        if left_type == right_type and left_type == InterpreterBase.INT_DEF:
            return Value(self.left.get_val() < self.right.get_val())
        self.scope.error(
            ErrorType.TYPE_ERROR,
            f"Cannot compare {self.left.get_type()} and {self.right.get_type()}",
        )

    def __eval_greater_equal(self):
        return Value(not self.__eval_less().get_val())

    def __eval_less_equal(self):
        return Value(not self.__eval_greater().get_val())

    def __eval_bool(self):
        self.left = self.left.converted_type(InterpreterBase.BOOL_DEF)
        self.right = self.right.converted_type(InterpreterBase.BOOL_DEF)
        if (not self.left) or (not self.right):
            self.scope.error(
                ErrorType.TYPE_ERROR,
                "Cannot perform boolean operations on non-boolean values",
            )
        if self.type == AND:
            return self.__eval_and()
        elif self.type == OR:
            return self.__eval_or()

    def __eval_and(self):
        return Value(self.left.get_val() and self.right.get_val())

    def __eval_or(self):
        return Value(self.left.get_val() or self.right.get_val())

    def __eval_arith(self):
        left_type = self.left.get_type()
        right_type = self.right.get_type()
        if (
            left_type == InterpreterBase.NIL_DEF
            or right_type == InterpreterBase.NIL_DEF
        ):
            self.scope.error(ErrorType.TYPE_ERROR, "Cannot perform arithmetic on nil")
        # Converting bools to ints
        if left_type == InterpreterBase.BOOL_DEF:
            self.left = self.left.converted_type(InterpreterBase.INT_DEF)
            left_type = InterpreterBase.INT_DEF
        if right_type == InterpreterBase.BOOL_DEF:
            self.right = self.right.converted_type(InterpreterBase.INT_DEF)
            right_type = InterpreterBase.INT_DEF

        if self.type == ADD:
            return self.__eval_add()
        elif self.type == SUBTRACT:
            return self.__eval_sub()
        elif self.type == MULTIPLY:
            return self.__eval_mul()
        elif self.type == DIVIDE:
            return self.__eval_div()
        raise Exception(f"Unknown arithmetic operator {self.type}")

    def __eval_add(self):
        left_type = self.left.get_type()
        right_type = self.right.get_type()
        # We add either 2 ints or 2 strings
        if (
            left_type == right_type
            and (
                left_type == InterpreterBase.INT_DEF
                or left_type == InterpreterBase.STRING_DEF
            )
        ) or (
            self.left.get_type() == InterpreterBase.STRING_DEF
            and self.right.get_type() == InterpreterBase.STRING_DEF
        ):
            return Value(self.left.get_val() + self.right.get_val())
        self.scope.error(
            ErrorType.TYPE_ERROR,
            f"Cannot add {self.left.get_type()} and {self.right.get_type()}",
        )

    def __eval_sub(self):
        left_type = self.left.get_type()
        right_type = self.right.get_type()
        if left_type == right_type and left_type == InterpreterBase.INT_DEF:
            return Value(self.left.get_val() - self.right.get_val())
        self.scope.error(
            ErrorType.TYPE_ERROR,
            f"Cannot subtract {self.left.get_type()} and {self.right.get_type()}",
        )

    def __eval_mul(self):
        left_type = self.left.get_type()
        right_type = self.right.get_type()
        if left_type == right_type and left_type == InterpreterBase.INT_DEF:
            return Value(self.left.get_val() * self.right.get_val())
        self.scope.error(
            ErrorType.TYPE_ERROR,
            f"Cannot multiply {self.left.get_type()} and {self.right.get_type()}",
        )

    def __eval_div(self):
        left_type = self.left.get_type()
        right_type = self.right.get_type()
        if left_type == right_type and left_type == InterpreterBase.INT_DEF:
            return Value(int(self.left.get_val() // self.right.get_val()))
        self.scope.error(
            ErrorType.TYPE_ERROR,
            f"Cannot divide {self.left.get_type()} and {self.right.get_type()}",
        )

    def __str__(self):
        return f"BinaryOperator({self.type}, {str(self.left)}, {str(self.right)})"
