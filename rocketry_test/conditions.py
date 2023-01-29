from datetime import datetime, timedelta, timezone

from rocketry.conds import condition

from machina.core.models import Base

# https://rocketry.readthedocs.io/en/stable/cookbook/conditions.html#io-related


# n_nodes_added_since
#   * inputs - num of nodes, Node subclass, since timestamp period of time
#   * returns - bool
#   for a given node subclass
#   if last node ts < (datetime now - since): return False <- no new nodes added since
#   else count all nodes with ts in range of (datetime now - since), if > n return true
#   return false


# ex: https://github.com/Miksus/rocketry/blob/master/rocketry/test/app/test_custom.py#L83
# @condition()
def n_nodes_added_since(
    n: int, 
    node_cls: type[Base], 
    duration: timedelta):
    """TODO test"""
    print('checking n_nodes_added_since')

    now = datetime.now(timezone.utc)
    duration_ts = (now - duration)
    
    # print(duration_ts)
    nodes = node_cls.nodes.filter(ts__gte=duration_ts).order_by('ts')
    print(f'num nodes: {len(nodes)}')
    if len(nodes) >= n:
        print('yes')
        return True

    print('nope')
    return False