from function_def import FunctionDef
from intbase import InterpreterBase


class LambdaDef(FunctionDef):
    def __init__(self, scope, element, trace_output=False):
        super().__init__(element, trace_output)
        # print(f"Making lambda with scope: {str(scope)}")
        self.scope = scope.copy()

    def get_scope(self):
        return self.scope

    def invoke_func(self, scope, args):
        # The scope the lambda is invoked in is at the very outside
        self.scope.add_base_scope(scope)
        returned_val = super().invoke_func(self.scope, args)
        self.scope.parent_scope = None
        return returned_val

    def get_type(self):
        return InterpreterBase.LAMBDA_DEF