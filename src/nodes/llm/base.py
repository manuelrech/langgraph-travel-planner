from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from typing import Optional

@dataclass
class LLMNode:
    model_name: str
    prompt: Optional[str] = None

    def __post_init__(self):
        self.llm = ChatOpenAI(model_name=self.model_name)