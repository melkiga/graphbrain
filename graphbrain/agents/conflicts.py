from graphbrain import hedge
from graphbrain.meaning.concepts import (all_concepts,
                                         strip_concept,
                                         has_proper_concept)
from graphbrain.meaning.lemmas import deep_lemma
from graphbrain.meaning.corefs import main_coref
from graphbrain.meaning.actors import is_actor
from graphbrain.agents.agent import Agent
from graphbrain.op import create_op


CONFLICT_PRED_LEMMAS = {'warn', 'kill', 'accuse', 'condemn', 'slam', 'arrest',
                        'clash', 'blame'}

CONFLICT_TOPIC_TRIGGERS = {'of/T/en', 'over/T/en', 'against/T/en', 'for/T/en'}


class Conflicts(Agent):
    def __init__(self):
        super().__init__()
        self.conflicts = 0
        self.conflict_topics = 0

    def name(self):
        return 'conflicts'

    def languages(self):
        return {'en'}

    def on_start(self):
        self.conflicts = 0
        self.conflict_topics = 0

    def _topics(self, hg, actor_orig, actor_targ, edge):
        for item in edge[1:]:
            if item.type()[0] == 's':
                if item[0].to_str() in CONFLICT_TOPIC_TRIGGERS:
                    for concept in all_concepts(item[1]):
                        if hg.degree(concept) > 1:
                            yield create_op(('conflict-topic/P/.', actor_orig,
                                             actor_targ, concept, edge))
                            self.conflict_topics += 1

    def input_edge(self, edge):
        hg = self.system.get_hg(self)

        if not edge.is_atom():
            ct = edge.connector_type()
            if ct[:2] == 'Pd':
                pred = edge[0]
                if (len(edge) > 2 and
                        deep_lemma(hg,
                                   pred).root() in CONFLICT_PRED_LEMMAS):
                    subjects = edge.edges_with_argrole('s')
                    objects = edge.edges_with_argrole('o')
                    if len(subjects) == 1 and len(objects) == 1:
                        subject = strip_concept(subjects[0])
                        obj = strip_concept(objects[0])
                        if (subject and obj and
                                has_proper_concept(subject) and
                                has_proper_concept(obj)):
                            actor_orig = main_coref(hg, subject)
                            actor_targ = main_coref(hg, obj)
                            conflict_edge = hedge(
                                ('conflict/P/.', actor_orig, actor_targ, edge))
                            if (is_actor(hg, actor_orig) and
                                    is_actor(hg, actor_targ)):
                                yield create_op(conflict_edge)
                                for wedge in self._topics(
                                        hg, actor_orig, actor_targ, edge):
                                    yield wedge
                                self.conflicts += 1

    def report(self):
        return 'conflict edges: {}\nconflict-topic pairs: {}'.format(
            self.conflicts, self.conflict_topics)
