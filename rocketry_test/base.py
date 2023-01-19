from rocketry import Rocketry

class Base(object):
    def __init__(self, cond):
        self.app = Rocketry()
        self.cond = cond

    def start(self):
        self.app.task(self.cond, func=self.analyze)
        self.app.run()

    def analyze(self):
        """implement in subclass"""
        raise NotImplemented