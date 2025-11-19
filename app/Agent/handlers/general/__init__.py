"""General handler services exports"""

from app.Agent.handlers.general.intent_detector import detect_general_intent
from app.Agent.handlers.general.llm_responder import generate_llm_response, should_use_llm
from app.Agent.handlers.general.templates import (
    get_help_template,
    get_about_template,
    get_features_template,
    get_greeting_template,
    get_default_template
)

__all__ = [
    "detect_general_intent",
    "generate_llm_response",
    "should_use_llm",
    "get_help_template",
    "get_about_template",
    "get_features_template",
    "get_greeting_template",
    "get_default_template"
]