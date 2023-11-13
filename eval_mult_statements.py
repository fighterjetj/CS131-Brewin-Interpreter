from return_type import Return


def eval_mult_statements(statements):
    for statement in statements:
        returned = statement.evaluate()
        if type(returned) == Return:
            return returned
