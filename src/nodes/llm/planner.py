from .base import LLMNode
from ...states.state import State

from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field


class PlannerOutput(BaseModel):
    plan_a: str = Field(description="A first proposal of the trip, in markdown format")
    plan_b: str = Field(description="A second proposal of the trip, in markdown format")


base_prompt = PromptTemplate.from_template(
"You are an trip planner participating in a multi-agent system that plans a trip.\n"
"Propose a plan without any specific reference to hotels or flights, just a general idea of the trip and activities to do.\n"
"Other agents will handle accomodation and transporation, you will be given a user input and you need to come up with two different plans.\n"
"The plans should be in markdown format.\n"

"User input: {enriched_user_input}\n"
)

feedback_prompt = base_prompt + """
We have generated two plans, but the user has given us feedback. Please modify the plans to reflect the user's feedback.
Plan A: {plan_a}
Plan B: {plan_b}
User feedback: {human_feedback}
"""

class Planner(LLMNode):

    def invoke(self, state: State) -> str:
        print("Planner: generating two proposals for the trip ...\n")
        inputs = {"enriched_user_input": state.enriched_user_input}

        if state.human_feedback:
            inputs = inputs | {
                "plan_a": state.plan_a,
                "plan_b": state.plan_b,
                "human_feedback": state.human_feedback
            }

        prompt = feedback_prompt if state.human_feedback else base_prompt
        chain = prompt | self.llm.with_structured_output(PlannerOutput)
        plans = chain.invoke(inputs)
        return {
            'plan_a': plans.plan_a,
            'plan_b': plans.plan_b
        }
