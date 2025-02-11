from langgraph.types import interrupt
from langchain_core.tools import tool

@tool
def human_in_the_loop(question_for_human: str) -> str:
    """
    Use this tool when you need to ask the human for clarification or additional information.
    """
    feedback = interrupt(question_for_human)
    return feedback