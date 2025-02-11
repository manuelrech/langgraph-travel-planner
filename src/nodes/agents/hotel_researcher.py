from datetime import datetime
from .tools.amadeus.search_hotels import search_hotels
from ...states.hotel_state import HotelState
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import PromptTemplate
from ...config import HOTEL_RESEARCHER_MODEL_NAME
from ...states.state import State
from dataclasses import dataclass

prompt = PromptTemplate.from_template(
    "You are an agent taksed with finding accomodation for a user.\n"
    "You will be given a city, a check in and a check out date and a number of adults.\n"
    "You must use the tool 'search_hotels' to find hotels.\n"
    "Do always one tool call at a time.\n"
    "today is {today}\n"
    "\n{messages}\n"
)

@dataclass
class HotelAgent:
    model_name: str = HOTEL_RESEARCHER_MODEL_NAME

    def __post_init__(self):
        self.agent = create_react_agent(
            model=self.model_name,
            tools=[search_hotels],
            state_modifier=prompt,
            state_schema=HotelState
        )

    def invoke(self, state: State):
        print("Hotel researcher: searching for accomodation ...\n")
        res: HotelState = self.agent.invoke(
            {
                "today": datetime.now().strftime("%Y-%m-%d"),
                "messages": state.request_for_agent
            }
        )
        return {
            'accomodation_proposal': [res['messages'][-1].content]
        }
