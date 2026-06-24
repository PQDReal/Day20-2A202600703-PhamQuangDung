"""Benchmark helpers for single-agent vs multi-agent."""

from collections.abc import Callable
from time import perf_counter

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState

Runner = Callable[[str], ResearchState]


def run_benchmark(
    run_name: str, query: str, runner: Runner
) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency, cost, quality proxy, citation coverage, and failure rate."""

    started = perf_counter()
    state = runner(query)
    latency = perf_counter() - started
    costs: list[float] = []
    for result in state.agent_results:
        cost = result.metadata.get("cost_usd")
        if isinstance(cost, int | float):
            costs.append(float(cost))
    citation_coverage = _citation_coverage(state)
    notes = (
        f"sources={len(state.sources)}, "
        f"trace_events={len(state.trace)}, "
        f"citations={citation_coverage:.0%}"
    )
    metrics = BenchmarkMetrics(
        run_name=run_name,
        latency_seconds=latency,
        estimated_cost_usd=sum(costs) if costs else 0.0,
        quality_score=_quality_score(state),
        citation_coverage=citation_coverage,
        failure_rate=1.0 if state.errors or not state.final_answer else 0.0,
        notes=notes,
    )
    return state, metrics


def _citation_coverage(state: ResearchState) -> float:
    if not state.sources:
        return 0.0
    answer = state.final_answer or ""
    cited = sum(1 for index, _ in enumerate(state.sources, start=1) if f"[{index}]" in answer)
    return cited / len(state.sources)


def _quality_score(state: ResearchState) -> float:
    score = 0.0
    if state.sources:
        score += 2.0
    if state.research_notes:
        score += 2.0
    if state.analysis_notes:
        score += 2.0
    if state.final_answer and len(state.final_answer) > 120:
        score += 2.0
    if not state.errors:
        score += 2.0
    return score
