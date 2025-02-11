from langgraph.types import interrupt
from ...states.state import State

class HumanLoop:
    def invoke(self, state: State) -> dict:
        # we need to pass in the state even if we don't use it
        feedback = interrupt('Which plan do you like more?')
        return {
            'human_feedback': feedback
        }

