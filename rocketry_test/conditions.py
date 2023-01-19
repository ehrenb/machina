from datetime import datetime, timedelta

from rocketry.conds import condition

from machina.core.models import Artifact

# https://rocketry.readthedocs.io/en/stable/cookbook/conditions.html#io-related


# n_nodes_added_since
#   * inputs - num of nodes, Node subclass, since timestamp period of time
#   * returns - bool
#   for a given node subclass
#   if last node ts < (datetime now - since): return False <- no new nodes added since
#   else count all nodes with ts in range of (datetime now - since), if > n return true
#   return false

@condition()
def n_nodes_added_since(
    n: int, 
    node_cls: Artifact, 
    duration: timedelta):
    """TODO test"""

    now = datetime.now()
    nodes = node_cls.nodes.all(ts__gte=(now - duration)).order_by('ts')
    if len(nodes) >= n:
        return True
    return False