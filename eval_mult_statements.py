import return_type
import convert_element


def eval_mult_statements(statements, scope):
    for statement in statements:
        proper_statement = convert_element.convert_element(statement, scope)
        returned = proper_statement.evaluate()
        if type(returned) == return_type.Return:
            return returned
