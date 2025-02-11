from dataclasses import dataclass, field
from random import randint

from IPython.display import Markdown, display
from .graphs.graph import build_graph,  CompiledStateGraph
from .graphs.graph_only_researchers import build_graph as build_graph_only_researchers
from .states.state import State

from langgraph.types import Command


@dataclass
class Manager:
    graph: CompiledStateGraph = field(
        default_factory=build_graph
    )
    graph_only_researchers: CompiledStateGraph = field(
        default_factory=build_graph_only_researchers
    )

    def invoke(
            self, 
            inputs: dict, 
            config: dict = {'configurable': {'thread_id': str(randint(1, 1000000))}},
            debug: bool = False
        ) -> dict:

        res: State = self.graph.invoke(inputs, config, debug=debug)
        finished = False
        while not finished:
            state_snapshot = self.graph.get_state(config)
            if state_snapshot.next == ():
                finished = True
                break
            elif state_snapshot.next[0] == 'human_loop':
                print(" --- Plan A --- ")
                display(Markdown(res['plan_a']))
                print(" --- Plan B --- ")
                display(Markdown(res['plan_b']))
                feedback = input('Which plan do you like more? (A/B) ')
                resume_inputs = Command(resume=feedback)
                res = self.graph.invoke(resume_inputs, config, debug=debug)
        return res
    
    def invoke_only_researchers(self, inputs: dict, config: dict = {'configurable': {'thread_id': str(randint(1, 1000000))}}, debug: bool = False) -> dict:
        # you need to set the state up with the right keys
        res: State = self.graph_only_researchers.invoke(inputs, config, debug=debug)
        return res
