from langgraph.managed import IsLastStep, RemainingSteps
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class HotelState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    today: str
    is_last_step: IsLastStep
    remaining_steps: RemainingSteps