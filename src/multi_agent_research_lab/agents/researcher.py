"""Researcher agent."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import trace_span
from multi_agent_research_lab.services.search_client import SearchClient


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def __init__(self, search_client: SearchClient | None = None) -> None:
        self.search_client = search_client or SearchClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`.

        Search results are deduplicated by title and converted to compact notes with
        numbered source references for downstream analysis and writing.
        """

        with trace_span(self.name, {"query": state.request.query}) as span:
            sources = self.search_client.search(state.request.query, state.request.max_sources)
            seen: set[str] = set()
            unique_sources = []
            for source in sources:
                key = source.title.lower()
                if key not in seen:
                    seen.add(key)
                    unique_sources.append(source)

            state.sources = unique_sources
            lines = [
                f"[{index}] {source.title}: {source.snippet}"
                for index, source in enumerate(unique_sources, start=1)
            ]
            state.research_notes = "\n".join(lines) if lines else "No relevant sources found."
            state.agent_results.append(
                AgentResult(
                    agent=AgentName.RESEARCHER,
                    content=state.research_notes,
                    metadata={"source_count": len(unique_sources)},
                )
            )
            span["source_count"] = len(unique_sources)
        state.add_trace_event("agent.researcher", span)
        return state
