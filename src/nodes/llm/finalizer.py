from .base import LLMNode
from ...states.state import State

from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate.from_template(
    "You are an assistant that is responsible for creating a final summary of the trip.\n"
    "You will be given a flight proposal, a hotel proposal, the user input and the proposed plan.\n"
    "You need to create a final summary of the trip, showing the user the all the available options.\n"
    "The flight proposal is: {flight_proposal}\n"
    "The hotel proposal is: {hotel_proposal}\n"
    "The user input is: {user_input}\n"
    "The proposed plan is: {preferred_plan}\n"
)

class TripFinalizer(LLMNode):
    def invoke(self, state: State):
        print("Trip finalizer: creating a final summary of the trip ...\n")
        chain = prompt | self.llm
        res = chain.invoke(
            {
                "flight_proposal": state.flight_proposal,
                "hotel_proposal": state.accomodation_proposal,
                "user_input": state.user_input,
                "preferred_plan": getattr(state, state.preferred_plan)
            }
        )
        return {
            "final_summary": res.content
        }

