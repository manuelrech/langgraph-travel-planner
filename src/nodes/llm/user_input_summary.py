from .base import LLMNode
from ...states.state import State

from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate.from_template("""
You are a helpful assistant that reformulates user travel preferences into a clear first-person statement.
Given the conversation between the user and an AI agent about travel plans, create a concise summary in first person that captures all the key details.

Example input:
"I want to go to Spain for food and culture"
[Conversation with details about duration, budget, etc]

Example output:
"I am planning a trip to Spain focused on experiencing the local food and culture. I will be traveling..."

Now reformulate this conversation into a first-person statement:

{user_input}

{ai_user_conversation}
""")

class UserInputSummary(LLMNode):

    def invoke(self, state: State) -> str:
        print("User input summary: reformulating user input with new information from the conversation ...\n")
        chain = prompt | self.llm
        return {
            'enriched_user_input': chain.invoke({
                'user_input': state.user_input,
                'ai_user_conversation': str(state.ai_user_conversation)
            }).content
        }