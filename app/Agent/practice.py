import os
import logging
from dotenv import load_dotenv
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.db.session import get_db
from app.services.retriever import query_hr_documents, get_vectorstore

load_dotenv()
logger = logging.getLogger(__name__)

llm = init_chat_model(
    "llama-3.1-8b-instant",
    model_provider="groq"
)

class MessageClassifier(BaseModel):
    message_type: Literal["emotional", "logical"] = Field(
        ...,
        description="Classifier if the message requires an emotional (therapist) or logical response"
    )

class AgentState(BaseModel):
    messages: Annotated[list, add_messages]
    message_type: str | None
    next: str | None = None

# nodes
def classify_message(state: AgentState):
    last_message = state.messages[-1]
    classifier_llm = llm.with_structured_output(MessageClassifier) # give us only output that matches the pydantic model
    
    result = classifier_llm.invoke([
        {
            "role": "system", 
            "content": """Classify the user message as either:
            - 'emotional': if it asks for emotional support, therapy, deals with feelings, or personal problems
            - 'logical': if it asks for facts, information, logical analysis, or practical solutions
            """
        },
        {"role": "user", "content":last_message.content}
    ])
    return {"message_type": result.message_type}

def router(state: AgentState):
    message_type = state.message_type or "logical" # default to logical type if message type is unclear
    if message_type == "emotional":
        return {"next": "therapist"}
    return {"next": "logical"}

def therapist_agent(state: AgentState):
    last_message = state.messages[-1]

    messages = [
        {"role": "system",
         "content": """You are a compassionate therapist. Focus on the emotional aspects of the user's message.
                        Show empathy, validate their feelings, and help them process their emotions.
                        Ask thoughtful questions to help them explore their feelings more deeply.
                        Avoid giving logical solutions unless explicitly asked."""
         },
        {
            "role": "user",
            "content": last_message.content
        }
    ]
    reply = llm.invoke(messages)
    return {"messages": [{"role": "assistant", "content": reply.content}]}

def logical_agent(state: AgentState):
    last_message = state.messages[-1]

    messages = [
        {"role": "system",
         "content": """You are a purely logical assistant. Focus only on facts and information.
            Provide clear, concise answers based on logic and evidence.
            Do not address emotions or provide emotional support.
            Be direct and straightforward in your responses."""
         },
        {
            "role": "user",
            "content": last_message.content
        }
    ]
    reply = llm.invoke(messages)
    return {"messages": [{"role": "assistant", "content": reply.content}]}

graph_builder = StateGraph(AgentState)

graph_builder.add_node("classifier", classify_message)
graph_builder.add_node("router", router)
graph_builder.add_node("therapist", therapist_agent)
graph_builder.add_node("logical", logical_agent)

graph_builder.add_edge(START, "classifier")
graph_builder.add_edge("classifier", "router")

graph_builder.add_conditional_edges(
    "router", # source
    lambda state: state.next,
    {"therapist": "therapist", "logical": "logical"} #path map
)

graph_builder.add_edge("therapist", END)
graph_builder.add_edge("logical", END)

# # node
# def chatbot(state: AgentState):
#     # Pass the messages list to llm.invoke
#     response = llm.invoke(state.messages)
#     return {"messages": [response]}

# graph_builder.add_node("chatbot", chatbot)
# graph_builder.add_edge(START, "chatbot")
# graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

# user_input = input("Enter a message: ")
# state = graph.invoke({"messages": [{"role": "user", "content": user_input}]})

# print(state["messages"])
# print(state["messages"][-1].content)

def run_chatbot():
    state = AgentState(messages=[], message_type=None, next=None)

    while True:
        user_input = input("Message: ")
        if user_input.lower() == "exit":
            print("Bye")
            break

        state.messages.append({"role": "user", "content": user_input})

        # Invoke the graph with Pydantic model
        state_dict = graph.invoke(state)
        state = AgentState(**state_dict)

        if state.messages:
            last_message = state.messages[-1]
            if hasattr(last_message, "content"):
                print(f"Assistant: {last_message.content}")
            else:
                print(f"Assistant: {last_message['content']}")


if __name__ == "__main__":
    run_chatbot()