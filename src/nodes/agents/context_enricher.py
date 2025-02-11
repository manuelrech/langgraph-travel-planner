from langgraph.types import Command
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from dataclasses import dataclass
from random import randint

from ...config import CONTEXT_ENRICHER_MODEL_NAME
from ...states.state import State
from .tools.human_in_the_loop import human_in_the_loop

prompt_template = ChatPromptTemplate.from_template(
    "You are the first of a series of agents tasked with generating a travel plan for a user.\n"
    "Your task is to gather essential information that other specialized agents will need to create a comprehensive travel plan.\n"
    "The other agents will handle:\n"
    "- Accommodation recommendations\n"
    "- Transportation arrangements\n" 
    # "- Destination selection\n"
    # "- Activity planning\n"
    # "- Budget management\n\n"
    "You need to gather the following key information:\n"
    "- Preferred type of destination (sea, mountain, city, desert, etc.) or the destination itself\n"
    "- Number of people travelling\n"
    "- Trip duration\n"
    "- Start and End date of the trip\n"
    "- Specific activities or experiences they want to have\n"
    "- Starting location\n"
    "- Any other preferences or constraints\n\n"
    "You can use the tool 'human_in_the_loop' to ask the human for clarification or additional information.\n"
    "If you already have all information you need, stop asking questions"
    "If the user says to proceed with travel plan generation, you MUST respond with the word 'FINISH' and no tool calls regardless of anything else.\n"
    "Ask one question (one tool call) at a time.\n"
    "\n{messages}"
)

@dataclass
class ContextEnricher:
    model_name: str = CONTEXT_ENRICHER_MODEL_NAME

    def __post_init__(self):
        self.memory = MemorySaver()
        self.config = {"configurable": {"thread_id": str(randint(1, 1000000))}}
        self.agent: CompiledGraph = create_react_agent(
            model=self.model_name,
            tools=[human_in_the_loop],
            state_modifier=prompt_template,
            checkpointer=self.memory
        )

    def invoke(self, state: State) -> str:
        print("Context enricher: getting more info from the user ...\n")
        message = state.user_input
        res = self.agent.invoke({"messages": [message]}, self.config)

        is_ai_message = lambda message: isinstance(message, AIMessage)
        finished = False
        while not finished:
            last_message = self.agent.get_state(self.config).values['messages'][-1]
            if not is_ai_message(last_message):
                continue
            if not last_message.tool_calls:
                finished = True
                break

            for tool_call in last_message.tool_calls:
                if tool_call['name'] == 'human_in_the_loop':
                    feedback = input(tool_call['args']['question_for_human'])
                    res = self._resume(feedback)
        
        return {
            'ai_user_conversation': self._format_extra_content(messages=res['messages']),
        }
    
    def _format_extra_content(self, messages: list[BaseMessage]) -> str:
        # we want to exclude the first message which contain info that are already in the state
        messages = messages[1:]
        conversation = []
        for message in messages:
            if isinstance(message, AIMessage):
                for tool_call in message.tool_calls:
                    conversation.append(('AI question', tool_call['args']['question_for_human']))
            elif isinstance(message, ToolMessage):
                conversation.append(('Human answer', message.content))

        return conversation
                
    def _resume(self, feedback: str) -> str:
        return self.agent.invoke(
            Command(resume=feedback),
            self.config
        )