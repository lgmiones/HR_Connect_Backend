"""
LangGraph orchestrator - coordinates the overall workflow
Backward compatibility wrapper for modular orchestrator
"""

import logging
from app.Agent.orchestrator.graph import create_agentic_orchestrator

logger = logging.getLogger(__name__)

# Create the compiled graph (same as before)
hr_agent_graph = create_agentic_orchestrator()

# Export for backward compatibility
__all__ = ["hr_agent_graph"]