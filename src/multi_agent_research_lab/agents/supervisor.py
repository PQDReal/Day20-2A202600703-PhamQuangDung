"""Supervisor / router agent."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.config import Settings, get_settings
from multi_agent_research_lab.core.state import ResearchState


class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def run(self, state: ResearchState) -> ResearchState:
        """Update `state.route_history` with the next route.

        Routing policy:
        - collect evidence first,
        - analyze evidence second,
        - write the answer third,
        - stop after a final answer or after the iteration budget is exhausted.
        """

        if state.iteration >= self.settings.max_iterations:
            route = "done"
            state.errors.append("Reached max_iterations; stopped by supervisor.")
        elif state.final_answer:
            route = "done"
        elif not state.research_notes:
            route = "researcher"
        elif not state.analysis_notes:
            route = "analyst"
        else:
            route = "writer"

        state.record_route(route)
        state.add_trace_event(
            "supervisor.route",
            {
                "next": route,
                "iteration": state.iteration,
                "has_sources": bool(state.sources),
                "has_analysis": bool(state.analysis_notes),
                "has_final": bool(state.final_answer),
            },
        )
        return state
