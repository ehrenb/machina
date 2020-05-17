import json

import ssdeep

from machina.core.worker import Worker
from machina.core.models.relationships.similar import Similar

class SimilarityAnalysis(Worker):

    # Invoked explicitly
    types = []

    def __init__(self, *args, **kwargs):
        super(SimilarityAnalysis, self).__init__(*args, **kwargs)

    def callback(self, data, properties):
        # self.logger.info(data)
        data = json.loads(data)
        ssdeep_threshold = int(self.config['worker']['ssdeep_threshold'])
        comparison_rules = self.config['worker']['comparison_type_rules']

        # resolve obj
        obj = self.graph.get_vertex(data['id'])
        obj_node_type = obj.__class__.__name__.lower()

        # TODO: smooth this out
        types_to_compare = []
        for stype, ttypes in comparison_rules.items():
            # ['*']:['*'] everything is compared to everything, also *:['apk'] will act identically - "everything is compared to apk, and apk is compared to everything"
            if stype == '*' or '*' in ttypes:
                types_to_compare = self.config['types']['available_types'].copy()
                types_to_compare.remove('*')
                break
            # ['apk']:['jar','dex']
            if obj_node_type == stype:
                types_to_compare = ttypes
            # ['jar']:['apk','dex']
            if obj_node_type in ttypes:
                types_to_compare = [stype]

        self.logger.info("Comparing against types: {}".format(types_to_compare))

        for type_to_compare in types_to_compare:
            c = self.resolve_db_node_cls(type_to_compare)
            targets = c.objects.query()
            for t in targets:
                # avoid comparing with self
                if t._id == obj._id:
                    continue
                # ensure node to compare against has ssdeep computed
                if t.ssdeep:
                    # do compare
                    result = ssdeep.compare(obj.ssdeep, t.ssdeep)
                    # check threshold
                    if result > ssdeep_threshold:
                        self.logger.info("Establishing similarity link between {} {} with result {}".format(obj._id, t._id, result))

                        # TODO: figure out how to add data to relationship
                        data = {
                            "measurements": {
                                "ssdeep_similarity": result
                            }
                        }
                        self.create_edge(Similar, obj._id, t._id, data=data)

