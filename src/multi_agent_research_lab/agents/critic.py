"""Optional critic agent for bonus work."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState


class CriticAgent(BaseAgent):
    """Optional fact-checking and safety-review agent."""

    name = "critic"

    def run(self, state: ResearchState) -> ResearchState:
        """Validate final answer and append findings.

        Adds a lightweight citation coverage check for bonus review work.
        """

        cited = sum(
            1
            for index, _ in enumerate(state.sources, start=1)
            if f"[{index}]" in (state.final_answer or "")
        )
        coverage = cited / len(state.sources) if state.sources else 0.0
        content = f"Citation coverage: {coverage:.0%}. Sources cited: {cited}/{len(state.sources)}."
        state.agent_results.append(
            AgentResult(
                agent=AgentName.CRITIC, content=content, metadata={"citation_coverage": coverage}
            )
        )
        state.add_trace_event(
            "agent.critic", {"citation_coverage": coverage, "sources": len(state.sources)}
        )
        return state
