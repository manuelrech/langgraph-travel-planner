from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.memory import MemorySaver

from ..config import (
    CONTEXT_ENRICHER_MODEL_NAME, 
    USER_INPUT_SUMMARY_MODEL_NAME, 
    PLANNER_MODEL_NAME, 
    ROUTER_MODEL_NAME,
    RESEARCHERS_MANAGER_MODEL_NAME,
    FLIGHT_RESEARCHER_MODEL_NAME,
    HOTEL_RESEARCHER_MODEL_NAME,
    TRIP_FINALIZER_MODEL_NAME
)
from ..states.state import State
from ..nodes.agents.context_enricher import ContextEnricher
from ..nodes.agents.flight_researcher import FlightAgent
from ..nodes.agents.hotel_researcher import HotelAgent
from ..nodes.llm.user_input_summary import UserInputSummary
from ..nodes.llm.planner import Planner
from ..nodes.llm.router import Router
from ..nodes.llm.research_manager import ResearchersManager
from ..nodes.llm.finalizer import TripFinalizer
from ..nodes.hil.human_loop import HumanLoop


def route_to_agent(state: State) -> str:
    return state.next_agent

def build_graph(memory_saver: MemorySaver = MemorySaver()) -> CompiledStateGraph:
    graph = StateGraph(State)

    graph.add_node(
        node='context_enricher',
        action=lambda state: ContextEnricher(model_name=CONTEXT_ENRICHER_MODEL_NAME).invoke(state)
    )

    graph.add_node(
        node='user_input_summary',
        action=lambda state: UserInputSummary(model_name=USER_INPUT_SUMMARY_MODEL_NAME).invoke(state)
    )

    graph.add_node(
        node='planner',
        action=lambda state: Planner(model_name=PLANNER_MODEL_NAME).invoke(state)
    )

    graph.add_node(
        node='human_loop',
        action=lambda state: HumanLoop().invoke(state)
    )

    graph.add_node(
        node='router',
        action=lambda state: Router(model_name=ROUTER_MODEL_NAME).invoke(state)
    )
    graph.add_node(
        node='researchers_manager',
        action=lambda state: ResearchersManager(model_name=RESEARCHERS_MANAGER_MODEL_NAME).invoke(state)
    )

    graph.add_node(
        node='flight_researcher',
        action=lambda state: FlightAgent(model_name=FLIGHT_RESEARCHER_MODEL_NAME).invoke(state)
    )

    graph.add_node(
        node='hotel_researcher',
        action=lambda state: HotelAgent(model_name=HOTEL_RESEARCHER_MODEL_NAME).invoke(state)
    )

    graph.add_node(
        node='trip_finalizer',
        action=lambda state: TripFinalizer(model_name=TRIP_FINALIZER_MODEL_NAME).invoke(state)
    )

    graph.set_entry_point('context_enricher')
    
    graph.add_edge('context_enricher', 'user_input_summary')
    graph.add_edge('user_input_summary', 'planner')
    graph.add_edge('planner', 'human_loop')
    graph.add_edge('human_loop', 'router')
    graph.add_conditional_edges(
        'router',
        route_to_agent,
        {
            'Planner': 'planner',
            'Finalizer': 'researchers_manager'
        }
    )

    graph.add_conditional_edges(
        source='researchers_manager',
        path=route_to_agent,
        path_map={
            'Flight Researcher': 'flight_researcher',
            'Hotel Researcher': 'hotel_researcher',
            'Finalizer': 'trip_finalizer'
        }
    )
    
    graph.add_edge('flight_researcher', 'researchers_manager')
    graph.add_edge('hotel_researcher', 'researchers_manager')
    
    graph.set_finish_point('trip_finalizer')
    
    return graph.compile(checkpointer=memory_saver)
