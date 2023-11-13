from function_def import FunctionDef
from intbase import InterpreterBase


class LambdaDef(FunctionDef):
    def __init__(self, element, scope, trace_output=False):
        super().__init__(element, trace_output)
        self.scope = scope.copy()

    def get_scope(self):
        return self.scope

    def invoke_func(self, scope, args):
        # The scope the lambda is invoked in is at the very outside
        new_scope = self.scope.copy()
        new_scope.add_base_scope(scope)
        return super().invoke_func(new_scope, args)

    def get_type(self):
        return InterpreterBase.LAMBDA_DEF
