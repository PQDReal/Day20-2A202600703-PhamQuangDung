"""Analyst agent."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import trace_span


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`.

        Extracts claims, evidence strength, limitations, and recommended answer shape.
        """

        with trace_span(self.name, {"source_count": len(state.sources)}) as span:
            source_titles = ", ".join(source.title for source in state.sources) or "no sources"
            weak_evidence = (
                "None" if state.sources else "No sources were retrieved; answer must be caveated."
            )
            state.analysis_notes = (
                "Key claims:\n"
                "- Multi-agent systems are useful when a task splits into evidence gathering, "
                "reasoning, and communication.\n"
                "- Shared state lets each role inspect prior outputs.\n"
                "- Max iterations, timeout, retries, validation, and fallbacks reduce "
                "runaway behavior.\n"
                "\nEvidence considered:\n"
                f"- {source_titles}\n"
                "\nWeak evidence / risks:\n"
                f"- {weak_evidence}\n"
                "- Local mock search is repeatable but should be replaced for live research.\n"
                "\nRecommended final answer:\n"
                "- Start directly, support claims with citations, and end with limitations."
            )
            state.agent_results.append(
                AgentResult(
                    agent=AgentName.ANALYST,
                    content=state.analysis_notes,
                    metadata={"weak_evidence": weak_evidence},
                )
            )
            span["analysis_chars"] = len(state.analysis_notes)
        state.add_trace_event("agent.analyst", span)
        return state
