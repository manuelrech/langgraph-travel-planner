from .base import LLMNode
from ...states.state import State
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime
AGENTS = {
    'Flight Researcher': 'This agent is responsible for researching flights.',
    'Hotel Researcher': 'This agent is responsible for researching hotels.',
    'Finalizer': 'Once there is a proposal for a flight and a hotel, this agent is responsible for finalizing the trip.'
}

class ResearchersManagerResponse(BaseModel):
    next_agent: Literal[*AGENTS.keys()] # type: ignore
    request_for_agent: str = Field(description="A request to the agent that follows, with the minimum amount of information needed to complete the task")

prompt_template = PromptTemplate.from_template(
    "You are a manager of a set of agents that are responsible for researching flights and hotels.\n"
    "You need to decide which agent to call next.\n"
    "Give the agent a request that is as minimal as possible, while still being complete.\n"
    "today's date is: {today_date}\n"
    "You can have these possible agents to follow: {agents}"
    "The user input is: {enriched_user_input}\n"
    "The plan we have so far is: {preferred_plan}"
    "The accomodation proposal we have so far is: {accomodation_proposal}"
    "The flight proposal we have so far is: {flight_proposal}"
)

class ResearchersManager(LLMNode):
    def invoke(self, state: State):
        print("Researchers manager: deciding which agent to call next ...\n")
        prompt = prompt_template.partial(agents=AGENTS)
        chain = prompt | self.llm.with_structured_output(ResearchersManagerResponse)
        res = chain.invoke(
            {
                "enriched_user_input": state.enriched_user_input,
                "preferred_plan": getattr(state, state.preferred_plan),
                "accomodation_proposal": state.accomodation_proposal,
                "flight_proposal": state.flight_proposal,
                "today_date": datetime.now().strftime("%Y-%m-%d")
            }
        )
        return {
            "next_agent": res.next_agent,
            "request_for_agent": res.request_for_agent
        }