class A(object):
    def __init__(self):
        pass
    def print_self(self):
        print(self.__class__.__name__)
        return self

class B(A):
    pass

b = B()
print(b.print_self().__class__.__name__)