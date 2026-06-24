"""Deterministic multi-agent workflow.

The project keeps LangGraph as an optional dependency. This workflow mirrors a graph
with supervisor-controlled conditional routing while remaining runnable in a minimal
Python environment.
"""

from collections.abc import Callable

from multi_agent_research_lab.agents import (
    AnalystAgent,
    ResearcherAgent,
    SupervisorAgent,
    WriterAgent,
)
from multi_agent_research_lab.core.config import Settings, get_settings
from multi_agent_research_lab.core.errors import AgentExecutionError
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import trace_span


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph.

    Keep orchestration here; keep agent internals in `agents/`.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.supervisor = SupervisorAgent(self.settings)
        self.nodes: dict[str, Callable[[ResearchState], ResearchState]] = {
            "researcher": ResearcherAgent().run,
            "analyst": AnalystAgent().run,
            "writer": WriterAgent().run,
        }

    def build(self) -> dict[str, list[str]]:
        """Return the graph shape used by `run`.

        A production deployment can replace this with a compiled LangGraph graph.
        """

        return {
            "supervisor": ["researcher", "analyst", "writer", "done"],
            "researcher": ["supervisor"],
            "analyst": ["supervisor"],
            "writer": ["supervisor"],
        }

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the graph and return final state.

        The supervisor chooses the next worker. Each worker returns to the supervisor
        until `done` is selected or the guardrail budget is reached.
        """

        graph = self.build()
        state.add_trace_event("workflow.build", {"graph": graph})

        with trace_span("workflow.run", {"max_iterations": self.settings.max_iterations}) as span:
            while state.iteration < self.settings.max_iterations:
                state = self.supervisor.run(state)
                route = state.route_history[-1]
                if route == "done":
                    break
                node = self.nodes.get(route)
                if node is None:
                    raise AgentExecutionError(f"Supervisor selected unknown route: {route}")
                try:
                    state = node(state)
                except Exception as exc:
                    state.errors.append(f"{route} failed: {exc}")
                    if route == "writer":
                        state.final_answer = "Fallback answer unavailable because writer failed."
                        break
            else:
                state.errors.append("Workflow stopped after max_iterations.")

            if not state.final_answer and state.research_notes:
                state.final_answer = (
                    "Fallback final answer based on available research notes:\n"
                    f"{state.research_notes}\n\n"
                    "Limitations: analysis or writing did not complete before the "
                    "guardrail stopped execution."
                )
            span["iterations"] = state.iteration
            span["errors"] = len(state.errors)
        state.add_trace_event("workflow.run", span)
        return state
