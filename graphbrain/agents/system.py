from importlib import import_module
from collections import defaultdict
import json
from graphbrain.op import apply_op
from graphbrain.parsers import create_parser


def run_agent(agent_module_str, lang=None, hg=None, infile=None,
              sequence=None):
    system = System(lang=lang, hg=hg, infile=infile, sequence=sequence)
    agent = create_agent(agent_module_str)
    system.add(agent_module_str, agent)
    system.run()


def load_system(system_file, lang=None, hg=None, infile=None, sequence=None):
    with open(system_file, 'r') as f:
        json_str = f.read()
    system_json = json.loads(json_str)
    system = System(name=system_file, lang=lang, hg=hg, infile=infile,
                    sequence=sequence)
    for agent_name in system_json:
        module_str = system_json[agent_name]['agent']
        depends_on = None
        input = None
        write = True
        if 'depends_on' in system_json[agent_name]:
            depends_on = system_json[agent_name]['depends_on']
        if 'input' in system_json[agent_name]:
            input = system_json[agent_name]['input']
        if 'write' in system_json[agent_name]:
            write = system_json[agent_name]['write']
        agent = create_agent(module_str)
        system.add(agent_name, agent, input=input, depends_on=depends_on,
                   write=write)
    return system


def run_system(system_file, lang=None, hg=None, infile=None, sequence=None):
    system = load_system(system_file, lang=lang, hg=hg, infile=infile,
                         sequence=sequence)
    system.run()


def create_agent(agent_module_str, silent=False):
    if '.' in agent_module_str:
        module_str = agent_module_str
    else:
        module_str = 'graphbrain.agents.{}'.format(agent_module_str)
    class_name_parts = module_str.split('.')[-1].split('_')
    class_name = ''.join([part.title() for part in class_name_parts])
    class_obj = getattr(import_module(module_str), class_name)
    obj = class_obj()
    obj.silent = silent
    return obj


class System(object):
    def __init__(self, name=None, lang=None, hg=None, infile=None,
                 sequence=None):
        self.name = name
        self.lang = lang
        self.hg = hg
        self.infile = infile
        self.sequence = sequence
        self.agents = {}
        self.outputs = defaultdict(set)
        self.dependants = defaultdict(set)
        self.roots = set()
        self.agent_seq = []
        self.parser = None
        self.counters = {}
        self.write = {}

    def add(self, name, agent, input=None, depends_on=None, write=True):
        agent.system = self
        self.agents[name] = agent
        if input:
            self.outputs[input].add(name)
        if depends_on:
            self.dependants[depends_on].add(name)
        # if agent has no inputs and depends on no other agents, then it is
        # a root agent
        if not (input or depends_on):
            self.roots.add(name)
        self.write[name] = write

    def run(self):
        # start by running the roots
        for root in self.roots:
            self._run_agent(root)
        # terminate all agents
        for agent_name in self.agent_seq:
            agent = self.agents[agent_name]
            print('\nstopping agent "{}"...'.format(agent_name))
            if agent.running:
                for op in agent.on_end():
                    self._process_op(agent_name, op)
            print('[*] agent "{}" stopped.'.format(agent_name))
            print('{} edges were added.'.format(self.counters[agent_name][0]))
            print('{} edges already existed.'.format(
                self.counters[agent_name][1]))
            report = agent.report()
            if len(report) > 0:
                print(report)

        if self.name:
            print('\nsystem "{}" stopped.'.format(self.name))

    def get_parser(self, agent):
        if self.parser is None:
            self.parser = create_parser(
                name=self.lang, lemmas=True, resolve_corefs=True)
        return self.parser

    def get_infile(self, agent):
        return self.infile

    def get_hg(self, agent):
        return self.hg

    def _reset_counters(self, agent_name):
        self.counters[agent_name] = [0, 0]

    def _start_agent(self, agent_name):
        agent = self.agents[agent_name]
        if not agent.running:
            self.agent_seq.append(agent_name)
            print('\n[>] agent "{}" started.'.format(agent.name()))
            self._reset_counters(agent_name)
            agent.on_start()
            agent.running = True

    def _process_op(self, agent_name, op):
        if self.write[agent_name]:
            if apply_op(self.hg, op):
                self.counters[agent_name][0] += 1
            else:
                self.counters[agent_name][1] += 1
        for output in self.outputs[agent_name]:
            self._start_agent(output)
            downstream_ops = self.agents[output].input_edge(op['edge'])
            if downstream_ops:
                for dop in downstream_ops:
                    self._process_op(output, dop)

    def _run_agent(self, agent_name):
        agent = self.agents[agent_name]
        self._start_agent(agent_name)

        ops = agent.run()
        if ops:
            for op in ops:
                self._process_op(agent_name, op)

        ops = agent.on_end()
        if ops:
            for op in ops:
                self._process_op(agent_name, op)
        agent.running = False

        for dependant in self.dependants[agent_name]:
            self._run_agent(dependant)
