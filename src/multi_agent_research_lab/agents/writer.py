"""Writer agent."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import trace_span
from multi_agent_research_lab.services.llm_client import LLMClient


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`.

        Synthesizes a clear answer with citations and records token/cost metadata.
        """

        with trace_span(self.name, {"audience": state.request.audience}) as span:
            citations = "\n".join(
                f"[{index}] {source.title} - {source.url or 'local note'}"
                for index, source in enumerate(state.sources, start=1)
            )
            system_prompt = (
                "You are a careful technical writer. Use the research and analysis notes, "
                "cite source numbers, and state limitations."
            )
            user_prompt = (
                f"Question: {state.request.query}\n"
                f"Audience: {state.request.audience}\n\n"
                f"Research notes:\n{state.research_notes or 'No research notes.'}\n\n"
                f"Analysis notes:\n{state.analysis_notes or 'No analysis notes.'}\n\n"
                f"Sources:\n{citations or 'No sources.'}"
            )
            response = self.llm_client.complete(system_prompt, user_prompt)
            source_refs = " ".join(f"[{index}]" for index, _ in enumerate(state.sources, start=1))
            citation_text = source_refs or "No external citations available; using local fallback."
            state.final_answer = (
                f"{response.content}\n\n"
                f"Citations: {citation_text}\n\n"
                "Limitations: Live web search is not enabled in the default offline configuration, "
                "so source freshness depends on the configured search provider."
            )
            state.agent_results.append(
                AgentResult(
                    agent=AgentName.WRITER,
                    content=state.final_answer,
                    metadata={
                        "input_tokens": response.input_tokens,
                        "output_tokens": response.output_tokens,
                        "cost_usd": response.cost_usd,
                    },
                )
            )
            span["cost_usd"] = response.cost_usd
            span["output_tokens"] = response.output_tokens
        state.add_trace_event("agent.writer", span)
        return state
