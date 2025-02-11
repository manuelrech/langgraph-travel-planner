from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.memory import MemorySaver

from ..config import (
    RESEARCHERS_MANAGER_MODEL_NAME,
    FLIGHT_RESEARCHER_MODEL_NAME,
    HOTEL_RESEARCHER_MODEL_NAME,
    TRIP_FINALIZER_MODEL_NAME
)
from ..states.state import State
from ..nodes.llm.research_manager import ResearchersManager
from ..nodes.agents.flight_researcher import FlightAgent
from ..nodes.agents.hotel_researcher import HotelAgent
from ..nodes.llm.finalizer import TripFinalizer


def route_to_agent(state: State) -> str:
    return state.next_agent


def build_graph(memory_saver: MemorySaver = MemorySaver()) -> CompiledStateGraph:
    graph = StateGraph(State)

    # Add the nodes starting from researchers_manager downwards
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

    # Set the entry point to the researchers_manager node
    graph.set_entry_point('researchers_manager')

    # Define conditional edges coming from researchers_manager based on the next_agent value
    graph.add_conditional_edges(
        source='researchers_manager',
        path=route_to_agent,
        path_map={
            'Flight Researcher': 'flight_researcher',
            'Hotel Researcher': 'hotel_researcher',
            'Finalizer': 'trip_finalizer'
        }
    )

    # Route back from the researchers to allow iterative handling
    graph.add_edge('flight_researcher', 'researchers_manager')
    graph.add_edge('hotel_researcher', 'researchers_manager')

    # Set the final finish node of the graph
    graph.set_finish_point('trip_finalizer')

    return graph.compile(checkpointer=memory_saver)