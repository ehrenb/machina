from datetime import timedelta, datetime
from rocketry.conds import minutely, hourly, daily, weekly, monthly, true, false

from base import Base
from machina.core.models import Artifact
from conditions import n_nodes_added_since

class Example(Base):
    def __init__(self, *args, **kwargs):
        super(Example, self).__init__(*args, **kwargs)

        # including the condition here (and uncommenting the @condition in conditions
        # results in the custom condition executing constantly)
        self.cond = hourly #& n_nodes_added_since(5, Artifact, timedelta(seconds=5))

    def analyze(self):
        if n_nodes_added_since(
            5,
            Artifact,
            timedelta(seconds=60)
        ):
            print('im analyzing!')