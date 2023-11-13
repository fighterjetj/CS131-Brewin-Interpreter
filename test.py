from copy import deepcopy


class X:
    def __init__(self):
        self.x = [1, 2, 3]

    def h(self):
        print("Hello")

    def g(self):
        print("Goodbye")

    def f(self):
        return deepcopy(self)


class Y(X):
    def __init__(self):
        super().__init__()

    def g(self):
        print("Goodbye cruel world")


y = Y()
x = y.f()
x.x.append(4)
print(y.x)
print(x.x)
