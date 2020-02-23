import sys
import time

from pyorient.ogm.declarative import declarative_node, declarative_relationship
from pyorient.ogm import Graph, Config

Node = declarative_node()
Relationship = declarative_relationship()

def init_orientdb(host, port, name, user, password):
    orientdb_url = '{}:{}/{}'.format(host, port, name)
    conf = Config.from_url(orientdb_url, user, password)

    # g = Graph(conf)
    # try:
    #     g.create_all(Node.registry)
    #     g.create_all(Relationship.registry)
    # except Exception as e:
    #     print(e)
    #     pass

    attempts = 0
    max_attempts = 5
    g = None
    while attempts < max_attempts:
        try:
            g = Graph(conf)
            g.create_all(Node.registry)
            g.create_all(Relationship.registry)
            break
        except Exception as e:
            print(e)
        attempts+=1
        time.sleep(1)
    if not g:
        sys.exit()

    return g
