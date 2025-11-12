"""
Pydantic models for the Agentic RAG system
"""

from typing import Annotated, Literal, List
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages


class SubQuery(BaseModel):
    """Represents a single question extracted from user input"""
    question: str = Field(..., description="A single, standalone question")
    query_type: Literal["policy", "personal_data", "general"] = Field(
        ..., description="The type of this specific question"
    )


class QueryDecomposition(BaseModel):
    """Result of breaking down a user message into sub-queries"""
    sub_queries: List[SubQuery] = Field(
        ..., 
        description="List of individual questions extracted from the user's message"
    )
    is_multiple: bool = Field(
        default=False,
        description="True if the user asked multiple questions"
    )


class AgentState(BaseModel):
    """State object passed through the LangGraph workflow"""
    messages: Annotated[list, add_messages]
    sub_queries: List[SubQuery] | None = None
    is_multiple: bool = False
    current_query_index: int = 0
    query_results: List[str] | None = None
    user_id: int | None = None
    query_type: str | None = None  