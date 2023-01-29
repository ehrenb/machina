
from neomodel import config
from rocketry import Rocketry
from rocketry.conds import minutely, hourly, daily, weekly, monthly

# def test():
#     print('ok')

class Base(object):
    def __init__(self):
        self.app = Rocketry()
        self.cond = None
        
        _cfg = {
            # "host": "neo4j",
            "host": "127.0.0.1",
            "port": 7687,
            "user": "neo4j",
            "pass": "tXOCq81bn7QfGTMJMrkQqP4J1",
            "db_name": "machina"
        }
        config.DATABASE_URL = f"bolt://{_cfg['user']}:{_cfg['pass']}@{_cfg['host']}:{_cfg['port']}/{_cfg['db_name']}"

    def start(self):
        print('starting')
        self.app.task(self.cond, func=self.analyze)
        self.app.run()

    def analyze(self):
        """implement in subclass"""
        raise NotImplemented