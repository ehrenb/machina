from rocketry.conds import daily

from base import Base

class TestSub(Base):
    def __init__(self, *args, **kwargs):
        super(TestSub, self).__init__(*args, **kwargs)
        self.cond = daily