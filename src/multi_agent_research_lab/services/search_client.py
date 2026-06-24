"""Search client abstraction for ResearcherAgent."""

from multi_agent_research_lab.core.schemas import SourceDocument


class SearchClient:
    """Provider-agnostic search client with a deterministic local corpus."""

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query.

        The lab runs reliably without paid search APIs. The local corpus acts as a
        mock search source and can later be swapped for Tavily, Bing, or internal docs.
        """

        query_terms = {term.lower().strip(".,:;!?()") for term in query.split() if len(term) > 3}
        ranked = sorted(
            _LOCAL_CORPUS,
            key=lambda item: _score(item, query_terms),
            reverse=True,
        )
        return ranked[:max_results]


def _score(document: SourceDocument, query_terms: set[str]) -> int:
    haystack = f"{document.title} {document.snippet}".lower()
    return sum(1 for term in query_terms if term in haystack)


_LOCAL_CORPUS = [
    SourceDocument(
        title="Building effective agents",
        url="https://www.anthropic.com/engineering/building-effective-agents",
        snippet=(
            "Agentic systems work best when workflows are simple, transparent, and use tools "
            "only where the task benefits from decomposition or feedback loops."
        ),
        metadata={"source_type": "reference"},
    ),
    SourceDocument(
        title="OpenAI Agents SDK orchestration concepts",
        url="https://developers.openai.com/",
        snippet=(
            "Handoffs and orchestration patterns help route work between specialized agents "
            "while preserving state, tool outputs, and final response ownership."
        ),
        metadata={"source_type": "reference"},
    ),
    SourceDocument(
        title="LangGraph workflow concepts",
        url="https://langchain-ai.github.io/langgraph/concepts/",
        snippet=(
            "Graph-based agent workflows model nodes, conditional edges, state transitions, "
            "and stop conditions for controllable multi-step execution."
        ),
        metadata={"source_type": "reference"},
    ),
    SourceDocument(
        title="Production guardrails for LLM systems",
        url=None,
        snippet=(
            "Useful guardrails include max iteration limits, timeout budgets, retries, "
            "fallback behavior, input/output validation, and traceable error reporting."
        ),
        metadata={"source_type": "local_note"},
    ),
    SourceDocument(
        title="Benchmarking multi-agent systems",
        url=None,
        snippet=(
            "Compare single-agent and multi-agent runs using latency, estimated cost, "
            "quality score, citation coverage, and failure rate across the same queries."
        ),
        metadata={"source_type": "local_note"},
    ),
]
