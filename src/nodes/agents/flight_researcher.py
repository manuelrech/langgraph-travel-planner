from datetime import datetime
from .tools.amadeus.search_flights import search_flights
from ...states.flight_state import FlightState
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import PromptTemplate
from dataclasses import dataclass
from ...config import FLIGHT_RESEARCHER_MODEL_NAME
from ...states.state import State

prompt = PromptTemplate.from_template(
        "You are an agent tasked with finding flights for a user.\n"
    "You will be given an origin city, a destination city, and a departure date.\n"
    "You must use the tool 'search_flights' to find available flights.\n"
    "Do always one tool call at a time.\n"
    "Today is {today}\n"
    "User request: {messages}"
)

@dataclass
class FlightAgent:
    model_name: str = FLIGHT_RESEARCHER_MODEL_NAME

    def __post_init__(self):
        self.agent = create_react_agent(
            model=self.model_name,
            tools=[search_flights],
            state_modifier=prompt,
            state_schema=FlightState
        )

    def invoke(self, state: State):
        print("Flight researcher: searching for flights ...\n")
        res: FlightState = self.agent.invoke(
            {
                "today": datetime.now().strftime("%Y-%m-%d"),
                "messages": state.request_for_agent
            }
        )
        return {
            'flight_proposal': [res['messages'][-1].content]
        }
