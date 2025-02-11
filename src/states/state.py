from dataclasses import dataclass, field
from operator import add
from typing import Annotated

@dataclass
class State:
    user_input: str
    enriched_user_input: str = ''
    ai_user_conversation: list[str] = field(default_factory=list)
    next_agent: str = ''
    plan_a: str = ''
    plan_b: str = ''
    human_feedback: str = ''
    preferred_plan: str = ''
    request_for_agent: str = ''
    accomodation_proposal: Annotated[list[str], add] = field(default_factory=list)
    flight_proposal: Annotated[list[str], add] = field(default_factory=list)
    final_summary: str = ''

